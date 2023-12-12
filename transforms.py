from capstone.x86 import *

from abi import CURRENT_ABI


def remove_shadow_stack_writes(sub):
    entry_bb = sub.entry_bb
    i = 0
    while i < len(entry_bb.instructions):
        insn = entry_bb.instructions[i].i
        if not (insn.id == X86_INS_MOV and insn.operands[0].type == X86_OP_MEM and
                insn.operands[0].mem.base == X86_REG_RSP and insn.operands[0].mem.disp > 0):
            break
        i += 1
    if i > 0:
        entry_bb.instructions = entry_bb.instructions[i:]


def delete_prologue_epilogue(sub):
    bb = sub.entry_bb
    remove_insn_count = 0
    for j in range(len(bb.instructions)):
        if bb.instructions[j].i.id != X86_INS_PUSH:
            break
        remove_insn_count += 1
    if remove_insn_count > 0:
        bb.instructions = bb.instructions[remove_insn_count:]

    for bb in sub.bbs.values():
        if bb.instructions[-1].i.id == X86_INS_RET:
            remove_insn_count = 0
            for j in range(len(bb.instructions) - 2, -1, -1):
                if bb.instructions[j].i.id != X86_INS_POP:
                    break
                remove_insn_count += 1
            if remove_insn_count > 0:
                bb.instructions = bb.instructions[:-remove_insn_count-1] + [bb.instructions[-1]]


def delete_function_call(sub, call_addr):
    for bb in sub.bbs.values():
        for i in range(len(bb.instructions) - 1, -1, -1):
            if bb.instructions[i].i.id == X86_INS_CALL and bb.instructions[i].i.operands[0].imm == call_addr:
                bb.instructions.pop(i)


def get_stack_size(sub):
    ret = 0
    for insn in sub.entry_bb.instructions:
        i = insn.i
        if i.id == X86_INS_PUSH:
            ret += i.operands[0].size
        elif i.id == X86_INS_SUB and i.operands[0].type == X86_OP_REG and i.operands[0].reg == X86_REG_RSP and i.operands[1].type == X86_OP_IMM:
            ret += i.operands[1].imm
    return ret
