%include "common.asm"

section .text
_test_impl:
    sub rsp, 0x100

    mov rax, 0x0123456789abcdef
    mov [rsp+0x00], rax
    mov rax, 0x001122334455667788
    mov [rsp+0x08], rax

    mov rax, 0xec1844f13d56614d
    mov [rsp+0x10], rax
    mov rax, 0x39252cebadfba3ee
    mov [rsp+0x18], rax

    movdqa xmm0, [rsp+0x00]
    movdqa xmm1, [rsp+0x10]
    paddq  xmm0, xmm1
    movdqa [rcx], xmm0

    movdqa    xmm0, [rsp+0x00]
    movdqa    xmm1, [rsp+0x10]
    punpckldq xmm0, xmm1
    movdqa    [rcx+0x10], xmm0

    movdqa  xmm0, [rsp+0x10]
    psrldq  xmm0, 2
    movdqa  [rcx+0x20], xmm0

    mov rax, 1
    add rsp, 0x100
    ret
