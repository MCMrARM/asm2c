from consts import X86_REGISTERS

REG_TO_PRIMARY_REG = {}

for (name, reg64, reg32, reg16, reg8l, reg8u) in X86_REGISTERS:
    REG_TO_PRIMARY_REG[reg64] = reg64
    REG_TO_PRIMARY_REG[reg32] = reg64
    REG_TO_PRIMARY_REG[reg16] = reg64
    REG_TO_PRIMARY_REG[reg8l] = reg64
    REG_TO_PRIMARY_REG[reg8u] = reg64
