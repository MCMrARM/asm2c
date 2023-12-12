%include "common.asm"

section .text
_test_impl:
    sub rsp, 0x38

    mov  edx, 2
    mov  qword [rsp+20h], 5
    lea  r9d, [rdx+2]
    lea  r8d, [rdx+1]
    lea  ecx, [rdx-1]
    call sum5
    cmp  rax, 15
    jne  .fail

    call sum5_shadowstack
    cmp  rax, 15
    jne  .fail

    call sum5_shadowstack_regshuffle
    cmp  rax, 15
    jne  .fail

    mov rax, 1
    add rsp, 0x38
    ret
.fail:
    mov rax, 0
    add rsp, 0x38
    ret

sum5:
    lea     rax, [rcx+rdx]
    add     rax, r8
    add     rax, r9
    add     rax, [rsp+0x28]
    ret

sum5_shadowstack:
    mov     [rsp+0x20], r9
    mov     [rsp+0x18], r8
    mov     [rsp+8], rbx

    lea     rbx, [rcx+rdx]
    add     rbx, [rsp+0x20]
    add     rbx, [rsp+0x18]
    add     rbx, [rsp+0x28]
    mov     rax, rbx

    mov     rbx, [rsp+8]
    ret


sum5_shadowstack_regshuffle:
    mov     [rsp+0x20], r9
    lea     r9, [rsp-0x1000]
    mov     [rsp+0x18], r8
    mov     [r9+0x1008], rbx

    mov     rax, 0
    cmp     rax, 0
    jne     .skip

    lea     rbx, [rcx+rdx]
    add     rbx, [rsp+0x20]
    add     rbx, [r9+0x1018]
    add     rbx, [rsp+0x28]
    mov     rax, rbx

.skip:
    mov     rbx, [rsp+8]
    ret