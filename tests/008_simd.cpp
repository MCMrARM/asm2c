#include <cstdio>
#include <cstdint>
#include <cstring>

struct retstruct {
    uint64_t r0_p0, r0_p1;
    uint64_t r1_p0, r1_p1;
    uint64_t r2_p0, r2_p1;
};

extern "C" uint64_t test_asm(uint64_t addr);
uint64_t sub_100000(uint64_t RCX, uint64_t RDX, uint64_t R8, uint64_t R9, uint64_t RSP_args);

int main() {
    retstruct structRef, structDec;
	auto retRef = test_asm((uint64_t) &structRef);
	if (retRef != 1)
	    return 2;
	auto retDec = sub_100000((uint64_t) &structDec, 0, 0, 0, 0);
	if (retDec != 1)
	    return 1;
	if (!memcmp(&structRef, &structDec, sizeof(retstruct)))
        return 0;
    else
        return 3;
}
