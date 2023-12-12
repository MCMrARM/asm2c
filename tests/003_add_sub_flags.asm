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
    ; ===========
    ; ADD (-1), 1
    ; ===========
    ; CF = 1, OF = 0, SF = 0, ZF = 1

    mov rax, 0xffffffffffffffff
    add rax, 1
    COND_CHECK 1010, jc, jnc
    COND_CHECK 1011, jno, jo
    COND_CHECK 1012, jns, js
    COND_CHECK 1013, jz, jnz

    mov eax, 0xffffffff
    add eax, 1
    COND_CHECK 1020, jc, jnc
    COND_CHECK 1021, jno, jo
    COND_CHECK 1022, jns, js
    COND_CHECK 1023, jz, jnz

    mov ax, 0xffff
    add ax, 1
    COND_CHECK 1030, jc, jnc
    COND_CHECK 1031, jno, jo
    COND_CHECK 1032, jns, js
    COND_CHECK 1033, jz, jnz

    mov al, 0xff
    add al, 1
    COND_CHECK 1040, jc, jnc
    COND_CHECK 1041, jno, jo
    COND_CHECK 1042, jns, js
    COND_CHECK 1043, jz, jnz

    mov ah, 0xff
    add ah, 1
    COND_CHECK 1050, jc, jnc
    COND_CHECK 1051, jno, jo
    COND_CHECK 1052, jns, js
    COND_CHECK 1053, jz, jnz

    ; ===========
    ; INC (-1), 1
    ; ===========
    ; CF = 1, OF = 0, SF = 0, ZF = 1

    mov rax, 0xffffffffffffffff
    inc rax
    COND_CHECK 2010, jc, jnc
    COND_CHECK 2011, jno, jo
    COND_CHECK 2012, jns, js
    COND_CHECK 2013, jz, jnz

    mov eax, 0xffffffff
    inc eax
    COND_CHECK 2020, jc, jnc
    COND_CHECK 2021, jno, jo
    COND_CHECK 2022, jns, js
    COND_CHECK 2023, jz, jnz

    mov ax, 0xffff
    inc ax
    COND_CHECK 2030, jc, jnc
    COND_CHECK 2031, jno, jo
    COND_CHECK 2032, jns, js
    COND_CHECK 2033, jz, jnz

    mov al, 0xff
    inc al
    COND_CHECK 2040, jc, jnc
    COND_CHECK 2041, jno, jo
    COND_CHECK 2042, jns, js
    COND_CHECK 2043, jz, jnz

    mov ah, 0xff
    inc ah
    COND_CHECK 2050, jc, jnc
    COND_CHECK 2051, jno, jo
    COND_CHECK 2052, jns, js
    COND_CHECK 2053, jz, jnz

    ; ===========
    ; SUB 0, 1
    ; ===========
    ; CF = 1, OF = 0, SF = 1, ZF = 0

    mov rax, 0
    sub rax, 1
    COND_CHECK 3010, jc, jnc
    COND_CHECK 3011, jno, jo
    COND_CHECK 3012, js, jns
    COND_CHECK 3013, jnz, jz

    mov eax, 0
    sub eax, 1
    COND_CHECK 3020, jc, jnc
    COND_CHECK 3021, jno, jo
    COND_CHECK 3022, js, jns
    COND_CHECK 3023, jnz, jz

    mov rax, 0xffffffffffffffff
    mov ax, 0
    sub ax, 1
    COND_CHECK 3030, jc, jnc
    COND_CHECK 3031, jno, jo
    COND_CHECK 3032, js, jns
    COND_CHECK 3033, jnz, jz

    mov rax, 0xffffffffffffffff
    mov al, 0
    sub al, 1
    COND_CHECK 3040, jc, jnc
    COND_CHECK 3041, jno, jo
    COND_CHECK 3042, js, jns
    COND_CHECK 3043, jnz, jz

    mov rax, 0xffffffffffffffff
    mov ah, 0
    sub ah, 1
    COND_CHECK 3050, jc, jnc
    COND_CHECK 3051, jno, jo
    COND_CHECK 3052, js, jns
    COND_CHECK 3053, jnz, jz

    ; ===========
    ; DEC 0, 1
    ; ===========
    ; CF = 1, OF = 0, SF = 1, ZF = 0

    mov rax, 0
    dec rax
    COND_CHECK 4010, jc, jnc
    COND_CHECK 4011, jno, jo
    COND_CHECK 4012, js, jns
    COND_CHECK 4013, jnz, jz

    mov eax, 0
    dec eax
    COND_CHECK 4020, jc, jnc
    COND_CHECK 4021, jno, jo
    COND_CHECK 4022, js, jns
    COND_CHECK 4023, jnz, jz

    mov rax, 0xffffffffffffffff
    mov ax, 0
    dec ax
    COND_CHECK 4030, jc, jnc
    COND_CHECK 4031, jno, jo
    COND_CHECK 4032, js, jns
    COND_CHECK 4033, jnz, jz

    mov rax, 0xffffffffffffffff
    mov al, 0
    dec al
    COND_CHECK 4040, jc, jnc
    COND_CHECK 4041, jno, jo
    COND_CHECK 4042, js, jns
    COND_CHECK 4043, jnz, jz

    mov rax, 0xffffffffffffffff
    mov ah, 0
    dec ah
    COND_CHECK 4050, jc, jnc
    COND_CHECK 4051, jno, jo
    COND_CHECK 4052, js, jns
    COND_CHECK 4053, jnz, jz

    ; ===========
    ; CMP 0, 1
    ; ===========
    ; CF = 1, OF = 0, SF = 1, ZF = 0

    mov rax, 0
    cmp rax, 1
    COND_CHECK 5010, jc, jnc
    COND_CHECK 5011, jno, jo
    COND_CHECK 5012, js, jns
    COND_CHECK 5013, jnz, jz

    mov eax, 0
    cmp eax, 1
    COND_CHECK 5020, jc, jnc
    COND_CHECK 5021, jno, jo
    COND_CHECK 5022, js, jns
    COND_CHECK 5023, jnz, jz

    mov rax, 0xffffffffffffffff
    mov ax, 0
    cmp ax, 1
    COND_CHECK 5030, jc, jnc
    COND_CHECK 5031, jno, jo
    COND_CHECK 5032, js, jns
    COND_CHECK 5033, jnz, jz

    mov rax, 0xffffffffffffffff
    mov al, 0
    cmp al, 1
    COND_CHECK 5040, jc, jnc
    COND_CHECK 5041, jno, jo
    COND_CHECK 5042, js, jns
    COND_CHECK 5043, jnz, jz

    mov rax, 0xffffffffffffffff
    mov ah, 0
    cmp ah, 1
    COND_CHECK 5050, jc, jnc
    COND_CHECK 5051, jno, jo
    COND_CHECK 5052, js, jns
    COND_CHECK 5053, jnz, jz

    ; ============
    ; ADD (16 BIT)
    ; ============

    ; 1 + 1 => CF = 0, OF = 0, SF = 0, ZF = 0
    mov ax, 1
    add ax, 1
    COND_CHECK 6011, jnc, jc
    COND_CHECK 6012, jno, jo
    COND_CHECK 6013, jns, js
    COND_CHECK 6014, jnz, jz

    ; (-1) + (-2) => CF = 1, OF = 0, SF = 1, ZF = 0
    mov ax, -1
    add ax, -2
    COND_CHECK 6021, jc, jnc
    COND_CHECK 6022, jno, jo
    COND_CHECK 6023, js, jns
    COND_CHECK 6024, jnz, jz

    ; 0 + 0 => CF = 0, OF = 0, SF = 0, ZF = 1
    mov ax, 0
    add ax, 0
    COND_CHECK 6031, jnc, jc
    COND_CHECK 6032, jno, jo
    COND_CHECK 6033, jns, js
    COND_CHECK 6034, jz, jnz

    ; 1 + (-1) => CF = 1, OF = 0, SF = 0, ZF = 1
    mov ax, 1
    add ax, -1
    COND_CHECK 6041, jc, jnc
    COND_CHECK 6042, jno, jo
    COND_CHECK 6043, jns, js
    COND_CHECK 6044, jz, jnz

    ; 0x7fff + 1 => CF = 0, OF = 1, SF = 1, ZF = 0
    mov ax, 0x7fff
    add ax, 1
    COND_CHECK 6051, jnc, jc
    COND_CHECK 6052, jo, jno
    COND_CHECK 6053, js, jns
    COND_CHECK 6054, jnz, jz

    ; 0x7ffe + 1 => CF = 0, OF = 0, SF = 0, ZF = 0
    mov ax, 0x7ffe
    add ax, 1
    COND_CHECK 6061, jnc, jc
    COND_CHECK 6062, jno, jo
    COND_CHECK 6063, jns, js
    COND_CHECK 6064, jnz, jz

    ; 0x8000 + 0xffff => CF = 1, OF = 1, SF = 0, ZF = 0
    mov ax, 0x8000
    add ax, 0xffff
    COND_CHECK 6071, jc, jnc
    COND_CHECK 6072, jo, jno
    COND_CHECK 6073, jns, js
    COND_CHECK 6074, jnz, jz

    ; 0x8000 + 0x7fff => CF = 0, OF = 0, SF = 1, ZF = 0
    mov ax, 0x8000
    add ax, 0x7fff
    COND_CHECK 6081, jnc, jc
    COND_CHECK 6082, jno, jo
    COND_CHECK 6083, js, jns
    COND_CHECK 6084, jnz, jz

    ; ============
    ; SUB (16 BIT)
    ; ============

    ; 1 - 0xffff => CF = 1, OF = 0, SF = 0, ZF = 0
    mov ax, 1
    sub ax, 0xffff
    COND_CHECK 7011, jc, jnc
    COND_CHECK 7012, jno, jo
    COND_CHECK 7013, jns, js
    COND_CHECK 7014, jnz, jz

    ; (-1) - 2 => CF = 0, OF = 0, SF = 1, ZF = 0
    mov ax, -1
    sub ax, 2
    COND_CHECK 7021, jnc, jc
    COND_CHECK 7022, jno, jo
    COND_CHECK 7023, js, jns
    COND_CHECK 7024, jnz, jz

    ; 0 - 0 => CF = 0, OF = 0, SF = 0, ZF = 1
    mov ax, 0
    sub ax, 0
    COND_CHECK 7031, jnc, jc
    COND_CHECK 7032, jno, jo
    COND_CHECK 7033, jns, js
    COND_CHECK 7034, jz, jnz

    ; 1 - 1 => CF = 0, OF = 0, SF = 0, ZF = 1
    mov ax, 1
    sub ax, 1
    COND_CHECK 7041, jnc, jc
    COND_CHECK 7042, jno, jo
    COND_CHECK 7043, jns, js
    COND_CHECK 7044, jz, jnz

    ; 0x7fff - 0xffff => CF = 1, OF = 1, SF = 1, ZF = 0
    mov ax, 0x7fff
    sub ax, 0xffff
    COND_CHECK 7051, jc, jnc
    COND_CHECK 7052, jo, jno
    COND_CHECK 7053, js, jns
    COND_CHECK 7054, jnz, jz

    ; 0x7ffe - 0xffff => CF = 1, OF = 0, SF = 0, ZF = 0
    mov ax, 0x7ffe
    sub ax, 0xffff
    COND_CHECK 7061, jc, jnc
    COND_CHECK 7062, jno, jo
    COND_CHECK 7063, jns, js
    COND_CHECK 7064, jnz, jz

    ; 0x8000 - 1 => CF = 0, OF = 1, SF = 0, ZF = 0
    mov ax, 0x8000
    sub ax, 1
    COND_CHECK 7071, jnc, jc
    COND_CHECK 7072, jo, jno
    COND_CHECK 7073, jns, js
    COND_CHECK 7074, jnz, jz

    ; 0x8000 - 0x8001 => CF = 1, OF = 0, SF = 1, ZF = 0
    mov ax, 0x8000
    sub ax, 0x8001
    COND_CHECK 7081, jc, jnc
    COND_CHECK 7082, jno, jo
    COND_CHECK 7083, js, jns
    COND_CHECK 7084, jnz, jz

    ; ============
    ; CMP (16 BIT)
    ; ============

    ; 1 - 0xffff => CF = 1, OF = 0, SF = 0, ZF = 0
    mov ax, 1
    cmp ax, 0xffff
    COND_CHECK 8011, jc, jnc
    COND_CHECK 8012, jno, jo
    COND_CHECK 8013, jns, js
    COND_CHECK 8014, jnz, jz

    ; (-1) - 2 => CF = 0, OF = 0, SF = 1, ZF = 0
    mov ax, -1
    cmp ax, 2
    COND_CHECK 8021, jnc, jc
    COND_CHECK 8022, jno, jo
    COND_CHECK 8023, js, jns
    COND_CHECK 8024, jnz, jz

    ; 0 - 0 => CF = 0, OF = 0, SF = 0, ZF = 1
    mov ax, 0
    cmp ax, 0
    COND_CHECK 8031, jnc, jc
    COND_CHECK 8032, jno, jo
    COND_CHECK 8033, jns, js
    COND_CHECK 8034, jz, jnz

    ; 1 - 1 => CF = 0, OF = 0, SF = 0, ZF = 1
    mov ax, 1
    cmp ax, 1
    COND_CHECK 8041, jnc, jc
    COND_CHECK 8042, jno, jo
    COND_CHECK 8043, jns, js
    COND_CHECK 8044, jz, jnz

    ; 0x7fff - 0xffff => CF = 1, OF = 1, SF = 1, ZF = 0
    mov ax, 0x7fff
    cmp ax, 0xffff
    COND_CHECK 8051, jc, jnc
    COND_CHECK 8052, jo, jno
    COND_CHECK 8053, js, jns
    COND_CHECK 8054, jnz, jz

    ; 0x7ffe - 0xffff => CF = 1, OF = 0, SF = 0, ZF = 0
    mov ax, 0x7ffe
    cmp ax, 0xffff
    COND_CHECK 8061, jc, jnc
    COND_CHECK 8062, jno, jo
    COND_CHECK 8063, jns, js
    COND_CHECK 8064, jnz, jz

    ; 0x8000 - 1 => CF = 0, OF = 1, SF = 0, ZF = 0
    mov ax, 0x8000
    cmp ax, 1
    COND_CHECK 8071, jnc, jc
    COND_CHECK 8072, jo, jno
    COND_CHECK 8073, jns, js
    COND_CHECK 8074, jnz, jz

    ; 0x8000 - 0x8001 => CF = 1, OF = 0, SF = 1, ZF = 0
    mov ax, 0x8000
    cmp ax, 0x8001
    COND_CHECK 8081, jc, jnc
    COND_CHECK 8082, jno, jo
    COND_CHECK 8083, js, jns
    COND_CHECK 8084, jnz, jz


    mov eax, 0
	ret
error:
    ret