%include "common.asm"

%macro COND_CHECK 3
    mov eax, 0x%1
    %3 error
    %2 pass%1
    jmp error
pass%1:
%endmacro

section .text
_test_impl:
    mov rax, 0xffffffff00000000 | 0x87654321
    and eax, 0x80000000
    COND_CHECK 1010, jnc, jc
    COND_CHECK 1011, jno, jo
    COND_CHECK 1012, js, jns
    COND_CHECK 1013, jnz, jz

    mov rax, 0xffffffff00000000 | 0x17654321
    or eax, 0x80000000
    COND_CHECK 1020, jnc, jc
    COND_CHECK 1021, jno, jo
    COND_CHECK 1022, js, jns
    COND_CHECK 1023, jnz, jz

    mov rax, 0xffffffff00000000 | 0x17654321
    xor eax, 0x80000000
    COND_CHECK 1030, jnc, jc
    COND_CHECK 1031, jno, jo
    COND_CHECK 1032, js, jns
    COND_CHECK 1033, jnz, jz

    mov rax, 0xffffffff00000000 | 0x87654321
    test eax, 0x80000000
    COND_CHECK 1040, jnc, jc
    COND_CHECK 1041, jno, jo
    COND_CHECK 1042, js, jns
    COND_CHECK 1043, jnz, jz

    mov rax, 0xffffffff00000000 | 0x78654321
    shl eax, 4
    COND_CHECK 1052, js, jns
    COND_CHECK 1053, jnz, jz

    mov rax, 0xffffffff00000000 | 0x87654321
    shr eax, 4
    COND_CHECK 1062, jns, js
    COND_CHECK 1063, jnz, jz

    mov rax, 0xffffffff00000000 | 0x87654321
    sar eax, 4
    COND_CHECK 1072, js, jns
    COND_CHECK 1073, jnz, jz

    mov eax, 0
	ret
error:
    ret