from capstone.x86 import *

from abi import CURRENT_ABI
from cbuilder import *
from consts import *
from ctx import get_sub_name, get_data_name, get_import_name
from utils import REG_TO_PRIMARY_REG

insn_handlers = {}


def insn_handler(insn_id):
    def decorator(fn):
        def wrapper(insn):
            return fn(insn)

        insn_handlers[insn_id] = wrapper
        return wrapper

    return decorator




REG_VARS = {}
REG_EXPR = {}
for (name, reg64, reg32, reg16, reg8l, reg8u) in X86_REGISTERS:
    REG_VARS[reg64] = CVar(name, CDataType.U64)
    REG_EXPR[reg64] = REG_VARS[reg64]
    REG_EXPR[reg32] = CCast(REG_VARS[reg64], CDataType.U32, True)
    REG_EXPR[reg16] = CCast(REG_VARS[reg64], CDataType.U16, True)
    REG_EXPR[reg8l] = CCast(REG_VARS[reg64], CDataType.U8, True)
    REG_EXPR[reg8u] = CArrIndex(CRef(CCast(REG_VARS[reg64], CDataType.U8, True)), CImm(1))
for (name, reg128) in X86_128_REGISTERS:
    REG_VARS[reg128] = CVar(name, CDataType.R128)
    REG_EXPR[reg128] = REG_VARS[reg128]
VAR_RSP = REG_VARS[X86_REG_RSP]

VAR_ZF, VAR_SF, VAR_OF, VAR_CF, VAR_PF = CVar('ZF', CDataType.BOOL), CVar('SF', CDataType.BOOL), CVar('OF', CDataType.BOOL), CVar('CF', CDataType.BOOL), CVar('PF', CDataType.BOOL)

SIZE_TO_DATATYPE = {
    1: CDataType.U8,
    2: CDataType.U16,
    4: CDataType.U32,
    8: CDataType.U64,
    16: CDataType.R128
}

def create_block(instructions: list['Instruction']):
    if len(instructions) > 1:
        return CBlock(instructions)
    return instructions[0]


def cast_signed(expr: CExpr, ref: bool = False):
    return CCast(expr, expr.datatype.make_signed(), ref)


def cast_to(expr: CExpr, datatype: CDataType, ref: bool = False):
    if datatype == expr.datatype:
        return expr
    return CCast(expr, datatype, ref)


def build_operand(insn, operand: X86Op, deref: bool = True, extend_to_64_bit: bool = False):
    i = insn.i
    if operand.type == X86_OP_MEM:
        ret = None
        if insn.reg_stack_off is not None and operand.mem.base in insn.reg_stack_off:
            stack_off = -insn.reg_stack_off[operand.mem.base]
            if operand.mem.disp >= stack_off + 8 + CURRENT_ABI.shadow_stack_space_size:
                # print(f'// arg {operand.mem.disp:x} {stack_off:x}')
                ret = CAdd(CVar('RSP_args', CDataType.U8_PTR), CImm(operand.mem.disp - (stack_off + 8 + CURRENT_ABI.shadow_stack_space_size), CDataType.S64))
            elif operand.mem.disp >= stack_off + 8:
                ret = CAdd(REG_EXPR[operand.mem.base], CImm(operand.mem.disp - 8, CDataType.S64))

        if ret is not None:
            pass
        elif operand.mem.base == X86_REG_RIP:
            data_name, do_ref = get_data_name(i.address + i.size + operand.mem.disp)
            ret = CVar(data_name, SIZE_TO_DATATYPE[operand.size])
            if do_ref:
                ret = CCast(CRef(ret), CDataType.U64, False)
        else:
            ret = CImm(0)
            if operand.mem.base != 0:
                ret = REG_EXPR[operand.mem.base]
            if operand.mem.disp != 0:
                ret = CAdd(ret, CImm(operand.mem.disp, CDataType.S64))
        if operand.mem.index != 0:
            ret = CAdd(ret, CMul(cast_signed(REG_EXPR[operand.mem.index]), operand.mem.scale))
        if deref:
            ret = CDeref(ret, SIZE_TO_DATATYPE[operand.size])
        return ret
    if operand.type == X86_OP_REG:
        if extend_to_64_bit and isinstance(REG_EXPR[operand.reg], CCast) and REG_EXPR[operand.reg].datatype.size() == 4:
            return REG_EXPR[operand.reg].expr
        return REG_EXPR[operand.reg]
    if operand.type == X86_OP_IMM:
        return CImm(operand.imm & ((1<<(8*operand.size))-1), SIZE_TO_DATATYPE[operand.size])
    return None


def common_flags(insn: 'Instruction', arith_result: CExpr):
    ret = []
    if (insn.set_flags & FLAG_ZF) != 0:
        ret.append(CAssign(VAR_ZF, CEq(arith_result, CImm(0))))
    if (insn.set_flags & FLAG_SF) != 0:
        r = cast_signed(arith_result)
        ret.append(CAssign(VAR_SF, CLt(r, CImm(0, r.datatype))))
    if (insn.set_flags & FLAG_PF) != 0:
        raise Exception("PF not implemented")
    return ret


@insn_handler(X86_INS_PUSH)
def push_handler(insn: 'Instruction'):
    i = insn.i
    return [
        CAssign(VAR_RSP, CSub(VAR_RSP, CImm(i.operands[0].size))),
        CMemWrite(VAR_RSP, build_operand(insn, i.operands[0]), SIZE_TO_DATATYPE[i.operands[0].size])
    ]


@insn_handler(X86_INS_POP)
def pop_handler(insn: 'Instruction'):
    i = insn.i
    return [
        CAssign(build_operand(insn, i.operands[0]), CDeref(VAR_RSP, SIZE_TO_DATATYPE[i.operands[0].size])),
        CAssign(VAR_RSP, CAdd(VAR_RSP, CImm(i.operands[0].size)))
    ]


@insn_handler(X86_INS_RET)
def ret_handler(insn: 'Instruction'):
    return [
        CReturn(REG_VARS[X86_REG_RAX])
    ]


@insn_handler(X86_INS_MOV)
@insn_handler(X86_INS_MOVQ)
@insn_handler(X86_INS_MOVDQU)
@insn_handler(X86_INS_MOVDQA)
@insn_handler(X86_INS_MOVABS)
@insn_handler(X86_INS_MOVUPS)
@insn_handler(X86_INS_MOVAPS)
@insn_handler(X86_INS_MOVZX)
def mov_handler(insn: 'Instruction'):
    i = insn.i
    ret = []
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), cast_to(build_operand(insn, i.operands[1]), SIZE_TO_DATATYPE[i.operands[0].size], False)))
    return ret


@insn_handler(X86_INS_MOVSXD)
def movsxd_handler(insn: 'Instruction'):
    i = insn.i
    ret = []
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), cast_signed(build_operand(insn, i.operands[1]))))
    return ret



@insn_handler(X86_INS_LEA)
def lea_handler(insn: 'Instruction'):
    i = insn.i
    ret = []
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), build_operand(insn, i.operands[1], deref=False)))
    return ret


def handle_add_flags(insn: 'Instruction', left: CExpr, right: CExpr, expr: CExpr):
    ret = []
    if (insn.set_flags & FLAG_CF) != 0:
        ret.append(CAssign(VAR_CF, CLt(expr, left)))
    if (insn.set_flags & FLAG_OF) != 0:
        zero = CImm(0, CDataType.S32)
        ret.append(CAssign(VAR_OF, CBoolOr(
            CBoolAnd(CBoolAnd(CGt(cast_signed(left), zero), CGt(cast_signed(right), zero)), CLt(cast_signed(expr), zero)),
            CBoolAnd(CBoolAnd(CLt(cast_signed(left), zero), CLt(cast_signed(right), zero)), CGt(cast_signed(expr), zero))
        )))
    return ret


def handle_sub_flags(insn: 'Instruction', left: CExpr, right: CExpr, expr: CExpr):
    ret = []
    if (insn.set_flags & FLAG_CF) != 0:
        ret.append(CAssign(VAR_CF, CLt(left, right)))
    if (insn.set_flags & FLAG_OF) != 0:
        zero = CImm(0, CDataType.S32)
        ret.append(CAssign(VAR_OF, CBoolOr(
            CBoolAnd(CBoolAnd(CGt(cast_signed(left), zero), CLt(cast_signed(right), zero)), CLt(cast_signed(expr), zero)),
            CBoolAnd(CBoolAnd(CLt(cast_signed(left), zero), CGt(cast_signed(right), zero)), CGt(cast_signed(expr), zero))
        )))
    return ret


def handle_zero_cf_of(insn: 'Instruction'):
    ret = []
    if (insn.set_flags & FLAG_CF) != 0:
        ret.append(CAssign(VAR_CF, CImm(False, CDataType.BOOL)))
    if (insn.set_flags & FLAG_OF) != 0:
        ret.append(CAssign(VAR_OF, CImm(False, CDataType.BOOL)))
    return ret


@insn_handler(X86_INS_SUB)
def sub_handler(insn: 'Instruction'):
    i = insn.i
    expr = CSub(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_sub_flags(insn, expr.left, expr.right, expr_c)
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_DEC)
def dec_handler(insn: 'Instruction'):
    i = insn.i
    expr = CSub(build_operand(insn, i.operands[0]), CImm(1, SIZE_TO_DATATYPE[i.operands[0].size]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_sub_flags(insn, expr.left, expr.right, expr_c)
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_ADD)
def add_handler(insn: 'Instruction'):
    i = insn.i
    expr = CAdd(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_add_flags(insn, expr.left, expr.right, expr_c)
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_INC)
def inc_handler(insn: 'Instruction'):
    i = insn.i
    expr = CAdd(build_operand(insn, i.operands[0]), CImm(1, SIZE_TO_DATATYPE[i.operands[0].size]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_add_flags(insn, expr.left, expr.right, expr_c)  # lack of CF change is handled by not adding it to set_flags
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_CMP)
def cmp_handler(insn: 'Instruction'):
    i = insn.i
    expr = CSub(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_sub_flags(insn, expr.left, expr.right, expr_c)
    return ret


@insn_handler(X86_INS_XOR)
@insn_handler(X86_INS_XORPS)
def xor_handler(insn: 'Instruction'):
    i = insn.i
    expr = CXor(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    if insn.i.operands[0].type == X86_OP_REG and insn.i.operands[0].reg == insn.i.operands[1].reg:
        expr = CImm(0, SIZE_TO_DATATYPE[insn.i.operands[0].size])
        expr_c = expr

    ret = common_flags(insn, expr_c)
    ret += handle_zero_cf_of(insn)
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_OR)
def or_handler(insn: 'Instruction'):
    i = insn.i
    expr = COr(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_zero_cf_of(insn)
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_AND)
def and_handler(insn: 'Instruction'):
    i = insn.i
    expr = CAnd(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_zero_cf_of(insn)
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_TEST)
def test_handler(insn: 'Instruction'):
    i = insn.i
    expr = CAnd(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_zero_cf_of(insn)
    return ret


@insn_handler(X86_INS_SHL)
def shl_handler(insn: 'Instruction'):
    i = insn.i
    expr = CShl(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    if (insn.set_flags & FLAG_CF) != 0:
        raise Exception("SHR: CF not implemented")
    if (insn.set_flags & FLAG_OF) != 0:
        raise Exception("SHR: OF not implemented")
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_SHR)
def shr_handler(insn: 'Instruction'):
    i = insn.i
    expr = CShr(build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    if (insn.set_flags & FLAG_CF) != 0:
        raise Exception("SHR: CF not implemented")
    if (insn.set_flags & FLAG_OF) != 0:
        raise Exception("SHR: OF not implemented")
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_SAR)
def sar_handler(insn: 'Instruction'):
    i = insn.i
    left = build_operand(insn, i.operands[0])
    expr = CShr(cast_signed(left), build_operand(insn, i.operands[1]))
    expr_c = cast_to(expr, left.datatype)
    ret = common_flags(insn, expr_c)
    if (insn.set_flags & FLAG_CF) != 0:
        raise Exception("SAR: CF not implemented")
    if (insn.set_flags & FLAG_OF) != 0:
        raise Exception("SAR: OF not implemented")
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret


@insn_handler(X86_INS_INT3)
def int3_handler(insn: 'Instruction'):
    return [
        CCall(CVar('INT3', CDataType.FUNC_PTR), [])
    ]


@insn_handler(X86_INS_NOP)
def nop_handler(insn: 'Instruction'):
    return []


@insn_handler(X86_INS_JMP)
def jmp_handler(insn: 'Instruction'):
    i = insn.i
    ret = [CGoto(f'bb_{i.operands[0].imm:x}')]
    if i.operands[0].imm not in insn.sub.bbs:
        ret = [*call_handler(insn), CReturn(REG_VARS[X86_REG_RAX])]
    return ret


X86_COND_CONDS = {
    X86_INS_JE: VAR_ZF,
    X86_INS_JNE: CNot(VAR_ZF),
    X86_INS_JA: CAnd(CNot(VAR_CF), CNot(VAR_ZF)),
    X86_INS_JAE: CNot(VAR_CF),
    X86_INS_JB: VAR_CF,
    X86_INS_JBE: COr(VAR_CF, VAR_ZF),
    X86_INS_JG: CAnd(CNot(VAR_ZF), CEq(VAR_SF, VAR_OF)),
    X86_INS_JGE: CEq(VAR_SF, VAR_OF),
    X86_INS_JL: CNot(CEq(VAR_SF, VAR_OF)),
    X86_INS_JLE: COr(VAR_ZF, CNot(CEq(VAR_SF, VAR_OF))),
    X86_INS_JNO: CNot(VAR_OF),
    X86_INS_JNP: CNot(VAR_PF),
    X86_INS_JNS: CNot(VAR_SF),
    X86_INS_JO: VAR_OF,
    X86_INS_JP: VAR_PF,
    X86_INS_JS: VAR_SF
}

for cond_id, cond_expr in X86_COND_CONDS.items():
    @insn_handler(cond_id)
    def cond_handler(insn: 'Instruction', cond_expr=cond_expr):
        embedded = create_block(jmp_handler(insn))
        return [CIf(cond_expr, embedded)]

for cond_id, jmp_id in X86_CMOV_TO_JMP.items():
    @insn_handler(cond_id)
    def cmovs_handler(insn: 'Instruction', cond_expr=X86_COND_CONDS[jmp_id]):
        embedded = create_block(mov_handler(insn))
        return [CIf(cond_expr, embedded)]

for cond_id, jmp_id in X86_SET_TO_JMP.items():
    @insn_handler(cond_id)
    def set_handler(insn: 'Instruction', cond_expr=X86_COND_CONDS[jmp_id]):
        i = insn.i
        return [
            CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), CCast(cond_expr, SIZE_TO_DATATYPE[i.operands[0].size], False))
        ]


@insn_handler(X86_INS_CALL)
def call_handler(insn: 'Instruction'):
    i = insn.i
    regs = CURRENT_ABI.func_registers
    args = [REG_EXPR[reg] if REG_TO_PRIMARY_REG[reg] in insn.sub.used_regs else CVar('UNDEF', CDataType.U64) for reg in regs]
    args += [CAdd(REG_EXPR[X86_REG_RSP], CURRENT_ABI.shadow_stack_space_size) if X86_REG_RSP in insn.sub.used_regs else CVar('UNDEF', CDataType.U64)]
    target = None
    if i.operands[0].type == X86_OP_IMM:
        target = CVar(get_sub_name(i.operands[0].imm), CDataType.FUNC)
    elif i.operands[0].type == X86_OP_MEM and i.operands[0].mem.base == X86_REG_RIP:
        import_name = get_import_name(i.address + i.size + i.operands[0].mem.disp)
        if import_name is not None:
            target = CVar(import_name, CDataType.FUNC)
    if target is None:
        target = CDeref(build_operand(insn, i.operands[0], True), CDataType.FUNC)
    return [
        CAssign(REG_VARS[X86_REG_RAX], CCall(target, args), CDataType.U64)
    ]


@insn_handler(X86_INS_PADDQ)
@insn_handler(X86_INS_PUNPCKLDQ)
@insn_handler(X86_INS_PSRLDQ)
def paddq_handler(insn: 'Instruction'):
    i = insn.i
    assert i.operands[0].size == 16
    return [
        CCall(CVar(i.mnemonic, CDataType.FUNC_PTR), [build_operand(insn, i.operands[0]), build_operand(insn, i.operands[1])])
    ]


@insn_handler(X86_INS_CDQ)
def cdq_handler(insn: 'Instruction'):
    return [
        CAssign(REG_EXPR[X86_REG_RDX], CCast(CShr(CCast(cast_signed(REG_EXPR[X86_REG_EAX]), CDataType.S32, False), 31), CDataType.U32, False))
    ]


@insn_handler(X86_INS_CDQE)
def cdqe_handler(insn: 'Instruction'):
    return [
        CAssign(REG_VARS[X86_REG_RAX], CCast(CCast(cast_signed(REG_EXPR[X86_REG_EAX]), CDataType.S64, False), CDataType.U64, False))
    ]


@insn_handler(X86_INS_BT)
def bt_handler(insn: 'Instruction'):
    ret = []
    if (insn.set_flags & FLAG_CF) != 0:
        right = build_operand(insn, insn.i.operands[1])
        ret.append(CAssign(VAR_CF, CAnd(CShr(build_operand(insn, insn.i.operands[0]), CAnd(right, CImm(8 * insn.i.operands[0].size - 1, CDataType.U64))), CImm(1, CDataType.U32))))
    if (insn.set_flags & FLAG_SF) != 0:
        raise Exception("BT: SF is undefined")
    if (insn.set_flags & FLAG_PF) != 0:
        raise Exception("BT: PF is undefined")
    if (insn.set_flags & FLAG_OF) != 0:
        raise Exception("BT: OF is undefined")
    return ret


@insn_handler(X86_INS_STC)
def stc_handler(insn: 'Instruction'):
    ret = []
    if (insn.set_flags & FLAG_CF) != 0:
        ret.append(CAssign(VAR_CF, CImm(True, CDataType.BOOL)))
    return ret


@insn_handler(X86_INS_CLC)
def clc_handler(insn: 'Instruction'):
    ret = []
    if (insn.set_flags & FLAG_CF) != 0:
        ret.append(CAssign(VAR_CF, CImm(False, CDataType.BOOL)))
    return ret


@insn_handler(X86_INS_NOT)
def not_handler(insn: 'Instruction'):
    return [
        CAssign(build_operand(insn, insn.i.operands[0], extend_to_64_bit=True), CBitNot(build_operand(insn, insn.i.operands[0])))
    ]


@insn_handler(X86_INS_NEG)
def neg_handler(insn: 'Instruction'):
    return [
        CAssign(build_operand(insn, insn.i.operands[0], extend_to_64_bit=True), CNeg(cast_signed(build_operand(insn, insn.i.operands[0]))))
    ]


@insn_handler(X86_INS_SBB)
def sbb_handler(insn: 'Instruction'):
    i = insn.i
    expr = CSub(build_operand(insn, i.operands[0]), CAdd(build_operand(insn, i.operands[1]), CCast(VAR_CF, SIZE_TO_DATATYPE[i.operands[1].size], False)))
    expr_c = cast_to(expr, expr.left.datatype)
    ret = common_flags(insn, expr_c)
    ret += handle_sub_flags(insn, expr.left, expr.right, expr_c)
    ret.append(CAssign(build_operand(insn, i.operands[0], extend_to_64_bit=True), expr_c))
    return ret
