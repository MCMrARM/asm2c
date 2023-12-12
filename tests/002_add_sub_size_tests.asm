%include "common.asm"

section .text
_test_impl:
    mov rax, 0x1234567890ABCDEF

    ; 32 bit add over 64 bit reg
    mov rdx, rax
    add edx, 0x12345678
    add rax, rdx

    ; 16 bit add over 64 bit reg
    mov rdx, rax
    add dx, 0x1234
    add rax, rdx

    ; 8 bit add over 64 bit reg
    mov rdx, rax
    add dl, 0x24
    add rax, rdx

    ; dh test
    mov rdx, rax
    add dh, 0x24
    add rax, rdx

    ; 32 bit sub over 64 bit reg
    mov rdx, rax
    sub edx, 0xfefefef1
    add rax, rdx

    ; 16 bit sub over 64 bit reg
    mov rdx, rax
    sub dx, 0xfef9
    add rax, rdx

    ; 8 bit sub over 64 bit reg
    mov rdx, rax
    sub dl, 0xf1
    add rax, rdx

    ; dh test
    mov rdx, rax
    sub dh, 0xf1
    add rax, rdx

	ret
