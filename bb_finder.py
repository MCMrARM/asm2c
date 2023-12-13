from consts import X86_TERMINATING_INSTRUCTIONS, X86_CONDITIONAL_INSTRUCTIONS, X86_JUMP_INSTRUCTIONS
from ctx import is_known_sub

MAX_BB_SIZE = 0x1000
MAX_FN_SIZE = 0x10000


def is_bb_terminating(i):
    return i.id in X86_TERMINATING_INSTRUCTIONS


def get_possible_jump_targets(i):
    possible_jump_targets = []
    if i.id in X86_CONDITIONAL_INSTRUCTIONS:
        possible_jump_targets.append(i.address + i.size)
        possible_jump_targets.append(i.operands[0].imm)
    elif i.id in X86_JUMP_INSTRUCTIONS:
        possible_jump_targets.append(i.operands[0].imm)
    elif i.id not in X86_TERMINATING_INSTRUCTIONS:
        possible_jump_targets = [i.address + i.size]
    return possible_jump_targets


def find_bbs(md, fn_addr, code_dump, code_addr):
    def check_bb(addr: int):
        offset = addr - code_addr

        for i in md.disasm(code_dump[offset:offset+MAX_BB_SIZE], addr):
            if is_bb_terminating(i) or i.address + i.size in qs:
                return get_possible_jump_targets(i), i.address + i.size

        return [], -1

    def check_prologue(addr: int):
        offset = addr - code_addr
        return code_dump[offset:offset+2] == b'\x40\x55'  # push rbp

    q = [fn_addr]
    qs = {fn_addr}
    max_end_addr = -1

    while len(q) > 0:
        cur = q.pop()
        possible_jump_targets, end_addr = check_bb(cur)
        max_end_addr = max(max_end_addr, end_addr)

        if len(possible_jump_targets) == 0:
            continue

        for target in possible_jump_targets:
            if target not in qs and abs(target - fn_addr) <= MAX_FN_SIZE and (target < max_end_addr or not check_prologue(target)) and not is_known_sub(target):
                q.append(target)
                qs.add(target)

    qs.add(max_end_addr)
    qqs = list(sorted(qs))
    return list(zip(qqs[:-1], qqs[1:]))