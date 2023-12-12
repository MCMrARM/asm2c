%include "common.asm"

section .text
_test_impl:
    mov rax, 0x1234567890ABCDEF

    ; 32 bit mov over 64 bit reg
    mov rdx, rax
    mov edx, 0x12345678
    add rax, rdx

    ; 16 bit mov over 64 bit reg
    mov rdx, rax
    mov dx, 0x1234
    add rax, rdx

    ; 8 bit mov over 64 bit reg
    mov rdx, rax
    mov dl, 0x24
    add rax, rdx

    ; dh test
    mov rdx, rax
    mov dh, 0x24
    add rax, rdx

	ret
