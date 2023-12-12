%ifdef STANDALONE
BITS 64
ORG 0x100000
%else
global _test_asm
section .text
_test_asm:
    mov r8, rdx
    mov r9, rcx
    mov rcx, rdi
    mov rdx, rsi
    jmp _test_impl
%endif