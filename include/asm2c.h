#pragma once

#include <cstdint>
#include <cstdio>
#include <cstdlib>

#define INT3() abort()
typedef uint64_t (afunc_t)(uint64_t RCX, uint64_t RDX, uint64_t R8, uint64_t R9, uint64_t RSP);

struct reg128 {
    uint64_t low, high;
    inline reg128(uint64_t low = 0, uint64_t high = 0) : low(low), high(high){}
    inline operator uint64_t() { return low; }
    inline operator uint32_t() { return (uint32_t) low; }
    inline operator uint16_t() { return (uint16_t) low; }
    inline operator uint8_t() { return (uint8_t) low; }
};
static inline void paddq(reg128& to, reg128 const& from) {
    to.low += from.low;
    to.high += from.high;
}
static inline void punpckldq(reg128& to, reg128 const& from) {
    auto p_to = (uint32_t*) &to;
    auto p_from = (uint32_t*) &from;
    p_to[0] = p_to[0];
    p_to[2] = p_to[1];
    p_to[1] = p_from[0];
    p_to[3] = p_from[1];
}
static inline void psrldq(reg128& to, unsigned int shift) {
    shift *= 8;
    to.low = (to.low >> shift) | (to.high << (64 - shift));
    to.high = (to.high >> shift);
}
static inline void UNIMPLEMENTED(const char* instr) {
    printf("UNIMPLEMENTED: %s\n", instr);
    abort();
}