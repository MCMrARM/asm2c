%include "common.asm"

section .text
_test_impl:
    mov eax, 0x8
    bt rax, 3
    jnc .fail
    bt eax, 3
    jnc .fail
    bt ax, 3
    jnc .fail

    mov eax, 0x8
    bt rax, 0x43
    jnc .fail
    bt eax, 0x23
    jnc .fail
    bt ax, 0x13
    jnc .fail

    mov rax, 0xffffffff80000008
    bt rax, 3
    jnc .fail
    bt eax, 3
    jnc .fail
    bt ax, 3
    jnc .fail

    mov rax, 0xffffffff80000008
    bt rax, 2
    jc .fail
    bt eax, 2
    jc .fail
    bt ax, 2
    jc .fail

    mov rax, 0x4000000000000000
    bt rax, 0x3e
    jnc .fail
    bt rax, 0xfe
    jnc .fail
    bt rax, 0x3f
    jc .fail

    mov rax, 0x4000000000000000
    mov edx, 0x3e
    bt rax, rdx
    jnc .fail
    mov edx, 0x7e
    bt rax, rdx
    jnc .fail
    mov edx, 0x3f
    bt rax, rdx
    jc .fail
    mov rdx, 0xfffffffffffffffe
    bt rax, rdx
    jnc .fail

    mov rax, 1
	ret
.fail:
    mov rax, 0
    ret
