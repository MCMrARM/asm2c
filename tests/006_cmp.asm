%include "common.asm"

%macro CMP_SET_FLAG 2
    cmp ecx, edx
    %2 %%setflag
    jmp %%cont
%%setflag:
    or rax, 1 << %1
%%cont:
%endmacro

%macro CMOV_SET_FLAG 2
    cmp ecx, edx
    mov r8d, 0
    mov r9d, 1 << %1
    %2 r8d, r9d
    or rax, r8
%endmacro

%macro SET_SET_FLAG 2
    xor r8d, r8d
    cmp ecx, edx
    %2 r8b
    shl r8, %1
    or rax, r8
%endmacro

section .text
_test_impl:
    cmp r8, 0
    je cmp_set_flag
    cmp r8, 1
    je cmov_set_flag
    cmp r8, 2
    je set_set_flag

    mov rax, -1
    ret

cmp_set_flag:
    mov eax, 0
    CMP_SET_FLAG 0x0, je
    CMP_SET_FLAG 0x1, jne
    CMP_SET_FLAG 0x2, ja
    CMP_SET_FLAG 0x3, jae
    CMP_SET_FLAG 0x4, jb
    CMP_SET_FLAG 0x5, jbe
    CMP_SET_FLAG 0x6, jg
    CMP_SET_FLAG 0x7, jge
    CMP_SET_FLAG 0x8, jl
    CMP_SET_FLAG 0x9, jle
    CMP_SET_FLAG 0xa, jo
    CMP_SET_FLAG 0xb, jno
    CMP_SET_FLAG 0xc, js
    CMP_SET_FLAG 0xd, jns
	ret

cmov_set_flag:
    mov eax, 0
    CMOV_SET_FLAG 0x0, cmove
    CMOV_SET_FLAG 0x1, cmovne
    CMOV_SET_FLAG 0x2, cmova
    CMOV_SET_FLAG 0x3, cmovae
    CMOV_SET_FLAG 0x4, cmovb
    CMOV_SET_FLAG 0x5, cmovbe
    CMOV_SET_FLAG 0x6, cmovg
    CMOV_SET_FLAG 0x7, cmovge
    CMOV_SET_FLAG 0x8, cmovl
    CMOV_SET_FLAG 0x9, cmovle
    CMOV_SET_FLAG 0xa, cmovo
    CMOV_SET_FLAG 0xb, cmovno
    CMOV_SET_FLAG 0xc, cmovs
    CMOV_SET_FLAG 0xd, cmovns
	ret

set_set_flag:
    mov eax, 0
    SET_SET_FLAG 0x0, sete
    SET_SET_FLAG 0x1, setne
    SET_SET_FLAG 0x2, seta
    SET_SET_FLAG 0x3, setae
    SET_SET_FLAG 0x4, setb
    SET_SET_FLAG 0x5, setbe
    SET_SET_FLAG 0x6, setg
    SET_SET_FLAG 0x7, setge
    SET_SET_FLAG 0x8, setl
    SET_SET_FLAG 0x9, setle
    SET_SET_FLAG 0xa, seto
    SET_SET_FLAG 0xb, setno
    SET_SET_FLAG 0xc, sets
    SET_SET_FLAG 0xd, setns
	ret