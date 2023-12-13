import subprocess
import sys
from pathlib import Path

from asm2c import Program, decompile_all
from utils import find_calls_recursive

SRC_DIR = Path('tests').absolute()
BUILD_DIR = Path('tests/build').absolute()


def run_test(test_name):
    BUILD_DIR.mkdir(exist_ok=True)
    subprocess.run(['nasm', '-o', str(BUILD_DIR / (test_name + '_asm.o')), '-f', 'macho64', str(SRC_DIR / (test_name + '.asm'))], cwd=SRC_DIR, check=True)
    subprocess.run(['nasm', '-dSTANDALONE', '-o', str(BUILD_DIR / (test_name + '_asm.bin')), str(SRC_DIR / (test_name + '.asm'))], cwd=SRC_DIR, check=True)

    with open(BUILD_DIR / (test_name + '_asm.bin'), 'rb') as f:
        bin_data = f.read()
    program = Program()
    program.code_addr = 0x100000
    program.code_dump = bin_data

    sub_addrs = find_calls_recursive(program, [0x100000])

    with open(BUILD_DIR / (test_name + '_dec.cpp'), 'w') as f:
        bak_stdout = sys.stdout
        sys.stdout = f
        try:
            print('#include <asm2c.h>')
            decompile_all(program, sub_addrs)
        finally:
            sys.stdout = bak_stdout

    subprocess.run(['arch', '-x86_64', 'g++', '-std=c++17',
                    '-I', str(SRC_DIR / '..' / 'include'),
                    '-o', str(BUILD_DIR / test_name),
                    str(BUILD_DIR / (test_name + '_asm.o')),
                    str(SRC_DIR / (test_name + '.cpp')),
                    str(BUILD_DIR / (test_name + '_dec.cpp'))], check=True)

    subprocess.run([BUILD_DIR / test_name], check=True)


run_test('000_sanity_check')
run_test('001_mov_size_tests')
run_test('002_add_sub_size_tests')
run_test('003_add_sub_flags')
run_test('004_bit_op_size_tests')
run_test('005_bit_op_flags')
run_test('006_cmp')
run_test('007_cdq')
run_test('008_simd')
run_test('009_stack')
run_test('010_bt')
