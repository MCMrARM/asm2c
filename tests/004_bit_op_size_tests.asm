%include "common.asm"

section .text
_test_impl:
    mov rax, 0x1234567890ABCDEF

    ; =========
    ; XOR TESTS
    ; =========

    ; 32 bit xor over 64 bit reg
    mov rdx, 0x187654321
    xor edx, 0xfefefef1
    add rax, rdx

    ; 16 bit xor over 64 bit reg
    mov rdx, rax
    xor dx, 0xfef9
    add rax, rdx

    ; 8 bit xor over 64 bit reg
    mov rdx, rax
    xor dl, 0xf1
    add rax, rdx

    ; dh test
    mov rdx, rax
    xor dh, 0xf1
    add rax, rdx

    ; ========
    ; OR TESTS
    ; ========

    ; 32 bit or over 64 bit reg
    mov rdx, 0x187654321
    or edx, 0xfefefef1
    add rax, rdx

    ; 16 bit or over 64 bit reg
    mov rdx, rax
    or dx, 0xfef9
    add rax, rdx

    ; 8 bit or over 64 bit reg
    mov rdx, rax
    or dl, 0xf1
    add rax, rdx

    ; dh test
    mov rdx, rax
    or dh, 0xf1
    add rax, rdx

    ; =========
    ; AND TESTS
    ; =========

    ; 32 bit and over 64 bit reg
    mov rdx, 0x187654321
    mov edx, 0x87654321
    and edx, 0xfefefef1
    add rax, rdx

    ; 16 bit or over 64 bit reg
    mov rdx, rax
    and dx, 0xfef9
    add rax, rdx

    ; 8 bit or over 64 bit reg
    mov rdx, rax
    and dl, 0xf1
    add rax, rdx

    ; dh test
    mov rdx, rax
    and dh, 0xf1
    add rax, rdx

    ; =========
    ; SHL TESTS
    ; =========

    ; 32 bit and over 64 bit reg
    mov rdx, 0x187654321
    shl edx, 4
    add rax, rdx

    ; 16 bit or over 64 bit reg
    mov rdx, rax
    shl dx, 4
    add rax, rdx

    ; 8 bit or over 64 bit reg
    mov rdx, rax
    shl dl, 2
    add rax, rdx

    ; dh test
    mov rdx, rax
    shl dh, 2
    add rax, rdx

    ; =========
    ; SHR TESTS
    ; =========

    ; 32 bit and over 64 bit reg
    mov rdx, 0x187654321
    shr edx, 4
    add rax, rdx

    ; 16 bit or over 64 bit reg
    mov rdx, rax
    shr dx, 4
    add rax, rdx

    ; 8 bit or over 64 bit reg
    mov rdx, rax
    shr dl, 2
    add rax, rdx

    ; dh test
    mov rdx, rax
    shr dh, 2
    add rax, rdx

    ; =========
    ; SAR TESTS
    ; =========

    ; 32 bit and over 64 bit reg
    mov rdx, 0x187654321
    sar edx, 4
    add rax, rdx

    ; 16 bit or over 64 bit reg
    mov rdx, rax
    sar dx, 4
    add rax, rdx

    ; 8 bit or over 64 bit reg
    mov rdx, rax
    sar dl, 2
    add rax, rdx

    ; dh test
    mov rdx, rax
    sar dh, 2
    add rax, rdx

    ; =========
    ; NOT TESTS
    ; =========

    ; 32 bit and over 64 bit reg
    mov rdx, 0x187654321
    not edx
    add rax, rdx

    ; 16 bit or over 64 bit reg
    mov rdx, rax
    not dx
    add rax, rdx

    ; 8 bit or over 64 bit reg
    mov rdx, rax
    not dl
    add rax, rdx

    ; dh test
    mov rdx, rax
    not dh
    add rax, rdx

    ; =========
    ; NEG TESTS
    ; =========

    ; 32 bit and over 64 bit reg
    mov rdx, 0x187654321
    neg edx
    add rax, rdx

    ; 16 bit or over 64 bit reg
    mov rdx, rax
    neg dx
    add rax, rdx

    ; 8 bit or over 64 bit reg
    mov rdx, rax
    neg dl
    add rax, rdx

    ; dh test
    mov rdx, rax
    neg dh
    add rax, rdx

	ret
