#include <cstdio>
#include <cstdint>

extern "C" uint64_t test_asm();
uint64_t sub_100000(uint64_t RCX, uint64_t RDX, uint64_t R8, uint64_t R9, uint64_t RSP_args);

int main() {
	auto ret = test_asm();
	if (ret != 0x12345678)
	    return 1;
	ret = sub_100000(0, 0, 0, 0, 0);
	if (ret != 0x12345678)
	    return 1;
}
