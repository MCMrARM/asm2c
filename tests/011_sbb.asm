%include "common.asm"

section .text
_test_impl:
    mov rax, 0x0123456789abcdef
    mov rcx, 0x100
    stc
    sbb rax, rcx
    mov rcx, 0x0123456789abcdef-0x100-1
    cmp rax, rcx
    jne .fail

    mov rax, 0x0123456789abcdef
    mov rcx, 0x100
    clc
    sbb rax, rcx
    mov rcx, 0x0123456789abcdef-0x100
    cmp rax, rcx
    jne .fail

    mov eax, 0x1
    mov ecx, 0x1
    stc
    sbb rax, rcx
    mov rcx, 0xffffffffffffffff
    cmp rax, rcx
    jne .fail

    mov rax, 1
	ret
.fail:
    mov rax, 0
    ret
