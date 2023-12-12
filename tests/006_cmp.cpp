#include <cstdio>
#include <cstdint>
#include <cstdlib>

extern "C" uint64_t test_asm(uint64_t a, uint64_t b, int32_t method);
uint64_t sub_100000(uint64_t RCX, uint64_t RDX, uint64_t R8, uint64_t R9, uint64_t RSP_args);

static void do_test(int32_t a, int32_t b) {
    auto retRef0 = test_asm(a, b, 0);
    for (int i = 0; i < 3; i++) {
        auto retRef = test_asm(a, b, i);
        auto retDec = sub_100000(a, b, i, 0, 0);
        if (retRef != retRef0) {
            printf("Bug in test %d %d %d ; %x %x\n", a, b, i, (int) retRef, (int) retRef0);
            exit(1);
        }
        if (retRef != retDec) {
            printf("Failed test %d %d %d ; %x %x\n", a, b, i, (int) retRef, (int) retDec);
            exit(1);
        }
    }
}

int main() {
    do_test(0, 0);
    do_test(1, 1);
    do_test(0, 1);
    do_test(1, 0);
    do_test(-1, 0);
    do_test(0, -1);
    do_test(-1, -1);
    do_test(-1, 1);
    do_test(0x7fffffff, 0x7fffffff);
    do_test(0x7fffffff, -0x80000000);
    do_test(-0x80000000, 0x7fffffff);

    srand(0);
    for (int i = 0; i < 1000000; i++) {
        int32_t a = rand();
        int32_t b = rand();
        do_test(a, b);
    }
}
