cur_program = None


def set_cur_program(program):
    global cur_program
    cur_program = program


def get_sub_name(addr):
    return f"sub_{addr:x}"


def get_data_name(addr):
    if cur_program is not None and addr >= cur_program.code_addr and addr < cur_program.code_addr + len(cur_program.code_dump):
        return '(uint64_t) ' + get_sub_name(addr), False
    return f"data_{addr:x}", True

