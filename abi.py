import dataclasses

from capstone.x86 import *


@dataclasses.dataclass
class ABI:
    func_registers: list[int]
    shadow_stack_space_size: int


WIN_ABI = ABI([
    X86_REG_RCX,
    X86_REG_RDX,
    X86_REG_R8,
    X86_REG_R9,
    # X86_REG_XMM0,
    # X86_REG_XMM1,
    # X86_REG_XMM2,
    # X86_REG_XMM3,
], 0x20)

CURRENT_ABI = WIN_ABI