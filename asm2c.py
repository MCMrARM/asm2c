from typing import Any, Optional

from capstone import *
import dataclasses

from abi import CURRENT_ABI
from bb_finder import *
from cbuilder import CCall, CVar, CImm, CDataType
from consts import *
from insns import insn_handlers, REG_VARS
from ctx import get_sub_name, set_cur_program, get_import_name
from transforms import remove_shadow_stack_writes, get_stack_size, delete_prologue_epilogue, delete_function_call
from utils import REG_TO_PRIMARY_REG, find_bb_order


@dataclasses.dataclass
class Instruction:
    sub: Optional['Subroutine']
    i: Any
    settable_flags: int
    set_flags: int
    received_flags: int
    reg_stack_off: Optional[dict[int, int]]

    def __init__(self, i: Any):
        self.sub = None
        self.i = i
        self.settable_flags = 0
        self.set_flags = 0
        self.received_flags = 0
        self.reg_stack_off = None

        if i.id in (X86_INS_SUB, X86_INS_ADD, X86_INS_CMP, X86_INS_XOR, X86_INS_OR, X86_INS_AND, X86_INS_TEST, X86_INS_SHL, X86_INS_SHR, X86_INS_SAR, X86_INS_SBB):
            self.settable_flags = FLAG_OF | FLAG_SF | FLAG_ZF | FLAG_AF | FLAG_PF | FLAG_CF
        if i.id in (X86_INS_INC, X86_INS_DEC):
            self.settable_flags = FLAG_OF | FLAG_SF | FLAG_ZF | FLAG_AF | FLAG_PF
        if i.id == X86_INS_BT:
            self.settable_flags = FLAG_OF | FLAG_SF | FLAG_AF | FLAG_PF | FLAG_CF
        if i.id in (X86_INS_STC, X86_INS_CLC):
            self.settable_flags = FLAG_CF
        if i.id in X86_JUMP_FLAGS:
            self.received_flags = X86_JUMP_FLAGS[i.id]
        if i.id in X86_CMOV_TO_JMP:
            self.received_flags = X86_JUMP_FLAGS[X86_CMOV_TO_JMP[i.id]]
        if i.id in X86_SET_TO_JMP:
            self.received_flags = X86_JUMP_FLAGS[X86_SET_TO_JMP[i.id]]
        if i.id in (X86_INS_SBB, ):
            self.received_flags = FLAG_CF

    def get_used_registers(self, ret: set[int]):
        for op in self.i.operands:
            if op.type == X86_OP_REG:
                ret.add(op.reg)
            if op.type == X86_OP_MEM and op.mem.base != 0:
                ret.add(op.mem.base)
            if op.type == X86_OP_MEM and op.mem.index != 0:
                ret.add(op.mem.index)

    def get_changed_registers(self):
        if self.i.id in X86_INSTRUCTIONS_CHANGING_FIRST_REG:
            if self.i.operands[0].type == X86_OP_REG:
                return {self.i.operands[0].reg}
        return None

    def to_c(self):
        if self.i.id not in insn_handlers:
            return [CCall(CVar('UNIMPLEMENTED', CDataType.FUNC_PTR), [CImm(str(self) + '\t(id=' + str(self.i.id) + ')', CDataType.CONST_CHAR_PTR)])]
        return insn_handlers[self.i.id](self)

    def __str__(self):
        i = self.i
        return "0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str)


@dataclasses.dataclass
class BB:
    start: int
    instructions: list
    next_block_addresses: list[int]
    next_blocks: list['BB']
    prev_blocks: list['BB']


@dataclasses.dataclass
class Subroutine:
    bbs: dict[int, BB]
    entry_bb: BB
    ordered_bbs: list[BB]
    used_regs: set[int]
    stack_size: int = 0


class Program:
    def __init__(self):
        self.code_dump = b''
        self.code_addr = 0

        self.md = Cs(CS_ARCH_X86, CS_MODE_64)
        self.md.detail = True

    def disassemble_sub(self, addr: int):
        bbs = {}

        addrs = find_bbs(self.md, addr, self.code_dump, self.code_addr)

        for bb_start, bb_end in addrs:
            bb = self.disassemble_bb(bb_start, bb_end)
            if bb is None:
                continue
            bbs[bb_start] = bb

        for bb in bbs.values():
            for target_addr in bb.next_block_addresses:
                if target_addr in bbs:
                    bb.next_blocks.append(bbs[target_addr])
                    bbs[target_addr].prev_blocks.append(bb)

        used_regs = expand_used_registers(find_all_used_registers(bbs))
        ordered_bbs = find_bb_order(bbs[addr])
        ret = Subroutine(bbs, bbs[addr], ordered_bbs, used_regs)
        for bb in bbs.values():
            for i in bb.instructions:
                i.sub = ret
        return ret

    def disassemble_bb(self, addr: int, end_addr: int):
        offset = addr - self.code_addr

        insns = []
        for i in self.md.disasm(self.code_dump[offset:offset+end_addr-addr], addr):
            ins = Instruction(i)
            insns.append(ins)
            if is_bb_terminating(i):
                break

        if len(insns) == 0:
            return None
        possible_jump_targets = get_possible_jump_targets(insns[-1].i)

        return BB(addr, insns, possible_jump_targets, [], [])


def analyze_cond_flags(sub: dict[int, BB]):
    bb_queue = set(sub.keys())
    bb_flags = {}
    while len(bb_queue) > 0:
        bb_addr = bb_queue.pop()
        bb = sub[bb_addr]

        flags = bb_flags.get(bb_addr, 0)
        for insn in reversed(bb.instructions):
            insn.set_flags = flags & insn.settable_flags
            flags &= ~insn.settable_flags
            flags |= insn.received_flags
            insn.received_flags = flags

        for obb in bb.prev_blocks:
            old_flags = bb_flags.get(obb.start, 0)
            if (old_flags | flags) != old_flags:
                bb_flags[obb.start] = old_flags | flags
                bb_queue.add(obb.start)


def analyze_stack_old(sub: dict[int, BB]):
    bb_stack_off = {}
    for bb in sub.values():
        stack_off, rbp_stack_off = bb_stack_off.get(bb.start, (0, -1))
        for insn in bb.instructions:
            insn.stack_off = stack_off
            insn.rbp_stack_off = rbp_stack_off
            if insn.i.id == X86_INS_PUSH:
                stack_off += insn.i.operands[0].size
            elif insn.i.id == X86_INS_POP:
                stack_off -= insn.i.operands[0].size
            elif insn.i.id == X86_INS_SUB and insn.i.operands[0].type == X86_OP_REG and insn.i.operands[0].reg == X86_REG_RSP and insn.i.operands[1].type == X86_OP_IMM:
                stack_off += insn.i.operands[1].imm
            elif insn.i.id == X86_INS_ADD and insn.i.operands[0].type == X86_OP_REG and insn.i.operands[0].reg == X86_REG_RSP and insn.i.operands[1].type == X86_OP_IMM:
                stack_off -= insn.i.operands[1].imm
            elif insn.i.id == X86_INS_MOV and insn.i.operands[0].type == X86_OP_REG and insn.i.operands[0].reg == X86_REG_RBP and insn.i.operands[1].type == X86_OP_REG and insn.i.operands[1].reg == X86_REG_RSP:
                rbp_stack_off = stack_off
            elif insn.i.id == X86_INS_LEA and insn.i.operands[0].type == X86_OP_REG and insn.i.operands[0].reg == X86_REG_RBP and insn.i.operands[1].type == X86_OP_MEM and insn.i.operands[1].mem.base == X86_REG_RSP:
                rbp_stack_off = stack_off - insn.i.operands[1].mem.disp
        for next in bb.next_blocks:
            v_stack_off, v_rbp_stack_off = bb_stack_off.get(next.start, (0, -1))
            bb_stack_off[next.start] = max(stack_off, v_stack_off), max(rbp_stack_off, v_rbp_stack_off)


def analyze_stack(sub: Subroutine):
    used_regs = set()
    bb_stack_off = {}
    bb_stack_off[sub.entry_bb.start] = {X86_REG_RSP: 0}
    for bb in sub.ordered_bbs:
        reg_stack_off = bb_stack_off.get(bb.start, {})
        for insn in bb.instructions:
            insn.stack_off = reg_stack_off[X86_REG_RSP]
            used_regs.clear()
            insn.get_used_registers(used_regs)
            for reg in used_regs:
                reg = REG_TO_PRIMARY_REG.get(reg, reg)
                if reg in reg_stack_off:
                    if insn.reg_stack_off is None:
                        insn.reg_stack_off = {}
                    insn.reg_stack_off[reg] = reg_stack_off[reg]

            if insn.i.id == X86_INS_PUSH:
                reg_stack_off[X86_REG_RSP] -= insn.i.operands[0].size
            elif insn.i.id == X86_INS_POP:
                reg_stack_off[X86_REG_RSP] += insn.i.operands[0].size
            elif insn.i.id == X86_INS_SUB and insn.i.operands[0].type == X86_OP_REG and insn.i.operands[0].reg == X86_REG_RSP and insn.i.operands[1].type == X86_OP_IMM:
                reg_stack_off[X86_REG_RSP] -= insn.i.operands[1].imm
            elif insn.i.id == X86_INS_ADD and insn.i.operands[0].type == X86_OP_REG and insn.i.operands[0].reg == X86_REG_RSP and insn.i.operands[1].type == X86_OP_IMM:
                reg_stack_off[X86_REG_RSP] += insn.i.operands[1].imm
            elif insn.i.id == X86_INS_MOV and insn.i.operands[0].type == X86_OP_REG:
                if insn.i.operands[1].type == X86_OP_REG and insn.i.operands[1].reg in reg_stack_off:
                    reg_stack_off[insn.i.operands[0].reg] = reg_stack_off[insn.i.operands[1].reg]
                elif insn.i.operands[0].reg in reg_stack_off:
                    del reg_stack_off[insn.i.operands[0].reg]
            elif insn.i.id == X86_INS_LEA and insn.i.operands[0].type == X86_OP_REG and insn.i.operands[1].type == X86_OP_MEM:
                if insn.i.operands[1].mem.base in reg_stack_off:
                    reg_stack_off[insn.i.operands[0].reg] = reg_stack_off[insn.i.operands[1].mem.base] + insn.i.operands[1].mem.disp
                elif insn.i.operands[0].reg in reg_stack_off:
                    del reg_stack_off[insn.i.operands[0].reg]
            else:
                regs = insn.get_changed_registers()
                if regs is not None:
                    for reg in regs:
                        if reg in REG_TO_PRIMARY_REG and REG_TO_PRIMARY_REG[reg] in reg_stack_off:
                            del reg_stack_off[REG_TO_PRIMARY_REG[reg]]

        for next in bb.next_blocks:
            if next.start not in bb_stack_off:
                bb_stack_off[next.start] = dict(reg_stack_off)
            else:
                v_reg_stack_off = bb_stack_off[next.start]
                for reg in list(v_reg_stack_off.keys()):
                    if reg not in reg_stack_off:
                        del v_reg_stack_off[reg]
                for reg, stack_off in reg_stack_off.items():
                    if reg in v_reg_stack_off:
                        v_reg_stack_off[reg] = min(v_reg_stack_off[reg], stack_off)


def find_all_used_registers(sub: dict[int, BB]):
    used_registers = set()
    used_registers.add(X86_REG_RAX)
    for bb in sub.values():
        for insn in bb.instructions:
            insn.get_used_registers(used_registers)
    return used_registers


def expand_used_registers(regs: set[int]):
    for reg in list(regs):
        if reg in REG_TO_PRIMARY_REG:
            regs.add(REG_TO_PRIMARY_REG[reg])
    return regs


def get_fn_sig(sub_addr):
    param_regs = CURRENT_ABI.func_registers
    sub_name = get_import_name(sub_addr)
    sub_name = get_sub_name(sub_addr) if sub_name is None else sub_name
    return 'uint64_t ' + sub_name + '(' + ', '.join([REG_VARS[x].datatype.value + ' ' + REG_VARS[x].name for x in param_regs]) + ', uint64_t RSP_args)'


def decompile_function(program, sub_addr):
    sub = program.disassemble_sub(sub_addr)
    analyze_stack(sub)
    # remove_shadow_stack_writes(sub)
    # delete_prologue_epilogue(sub)
    if hasattr(program, 'check_cookie_addr'):
        delete_function_call(sub, program.check_cookie_addr)
    stack_size = get_stack_size(sub)
    sub.stack_size = stack_size
    analyze_cond_flags(sub.bbs)
    print(get_fn_sig(sub_addr) + ' {')
    param_regs = CURRENT_ABI.func_registers
    regs = [str(x[0]) for x in X86_REGISTERS if x[1] in sub.used_regs and x[1] not in param_regs]
    if len(regs) > 0:
        print('  uint64_t ' + ', '.join(regs + ['UNDEF']) + ';')
    regs128 = [str(x[0]) for x in X86_128_REGISTERS if x[1] in sub.used_regs and x[1] not in param_regs]
    if len(regs128) > 0:
        print('  reg128 ' + ', '.join(regs128) + ';')
    print('  bool ZF, SF, CF, OF, AF, PF;')
    if X86_REG_RSP in sub.used_regs:
        print(f'  uint8_t stack[0x{stack_size + CURRENT_ABI.shadow_stack_space_size:x}]; RSP = (uint64_t) stack + sizeof(stack) - 0x{CURRENT_ABI.shadow_stack_space_size:x};')
    for addr in sorted(sub.bbs.keys()):
        bb = sub.bbs[addr]
        print('bb_%x:' % bb.start)
        for insn in bb.instructions:
            exprs = insn.to_c()
            print('  ' + ' '.join(str(i) + ';' for i in exprs))
    print('}')


def decompile_all(program: Program, sub_addrs: list[int]):
    set_cur_program(program)
    for addr in sub_addrs:
        print(get_fn_sig(addr) + ';')
    for addr in sub_addrs:
        decompile_function(program, addr)
