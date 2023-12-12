#include <cstdio>
#include <cstdint>

extern "C" uint64_t test_asm();
uint64_t sub_100000(uint64_t RCX, uint64_t RDX, uint64_t R8, uint64_t R9, uint64_t RSP_args);

int main() {
	auto retRef = test_asm();
	auto retDec = sub_100000(0, 0, 0, 0, 0);
	if (retRef != retDec) {
	    printf("Error: %llu != %llu\n", retRef, retDec);
	    return 1;
    }
}
