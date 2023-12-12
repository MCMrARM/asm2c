from collections import defaultdict, deque

from consts import X86_REGISTERS
from capstone.x86 import *

REG_TO_PRIMARY_REG = {}

for (name, reg64, reg32, reg16, reg8l, reg8u) in X86_REGISTERS:
    REG_TO_PRIMARY_REG[reg64] = reg64
    REG_TO_PRIMARY_REG[reg32] = reg64
    REG_TO_PRIMARY_REG[reg16] = reg64
    REG_TO_PRIMARY_REG[reg8l] = reg64
    REG_TO_PRIMARY_REG[reg8u] = reg64


def find_calls(bbs):
    calls = []
    for bb in bbs:
        for insn in bb.instructions:
            if insn.i.id == X86_INS_CALL:
                calls.append(insn)
    return calls


def find_calls_recursive(prog: 'Program', sub_addrs: list[int]):
    q = sub_addrs.copy()
    qs = set(sub_addrs)

    while len(q) > 0:
        cur = q.pop()
        for bb in prog.disassemble_sub(cur).bbs.values():
            for insn in bb.instructions:
                if insn.i.id == X86_INS_CALL:
                    target = insn.i.operands[0].imm
                    if target not in qs:
                        q.append(target)
                        qs.add(target)

    return list(qs)


def find_bb_order(entry_bb: 'BB'):
    visited = set()
    visited_subtree = set()
    good_edges = defaultdict(list)
    in_edge_count = defaultdict(lambda: 0)

    def dfs(cur: 'BB'):
        if cur.start in visited:
            return
        visited.add(cur.start)
        visited_subtree.add(cur.start)
        for next_bb in cur.next_blocks:
            if next_bb.start not in visited_subtree:
                good_edges[cur.start].append(next_bb)
                in_edge_count[next_bb.start] += 1
                dfs(next_bb)
        visited_subtree.remove(cur.start)

    dfs(entry_bb)

    q = deque()
    q.append(entry_bb)

    ret = []

    while len(q) > 0:
        cur = q.popleft()
        ret.append(cur)
        for next in good_edges[cur.start]:
            in_edge_count[next.start] -= 1
            if in_edge_count[next.start] == 0:
                q.append(next)

    return ret
