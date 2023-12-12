%include "common.asm"

section .text
_test_impl:
    ; test cdq with input 0x87654321
    mov r8, 0x1234567887654321
    mov rax, r8
    mov rdx, r8
    cdq
    cmp rax, r8
    jne .fail
    mov r8d, 0xffffffff
    cmp rdx, r8
    jne .fail

    ; test cdq with input 0x1234567
    mov r8, 0x8765432112345678
    mov rax, r8
    mov rdx, r8
    cdq
    cmp rax, r8
    jne .fail
    mov r8d, 0
    cmp rdx, r8
    jne .fail

    ; test cdqe with input 0x87654321
    mov rax, 0x1234567887654321
    cdqe
    mov r8, 0xffffffff87654321
    cmp rax, r8
    jne .fail

    ; test cdqe with input 0x1234567
    mov rax, 0x8765432112345678
    cdqe
    mov r8, 0x12345678
    cmp rax, r8
    jne .fail

    mov rax, 1
	ret
.fail:
    mov rax, 0
    ret
