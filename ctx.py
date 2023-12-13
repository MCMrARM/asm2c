cur_program = None
sub_names = {}
data_names = {}
import_names = {}
strings = {}


def set_cur_program(program: 'Program'):
    global cur_program
    cur_program = program


def get_sub_name(addr: int) -> str:
    if addr in sub_names:
        return sub_names[addr]
    return f"sub_{addr:x}"


def is_known_sub(addr: int) -> bool:
    return addr in sub_names


def get_data_name(addr: int) -> tuple[str, bool]:
    if addr in data_names:
        return data_names[addr], True
    if addr in strings:
        import json
        return '(uint64_t) ' + json.dumps(strings[addr]), False
    if cur_program is not None and addr >= cur_program.code_addr and addr < cur_program.code_addr + len(cur_program.code_dump):
        return '(uint64_t) ' + get_sub_name(addr), False
    return f"data_{addr:x}", True


def get_import_name(addr: int) -> str:
    return import_names.get(addr, None)


def add_sub_names(data: dict[int, str]):
    sub_names.update(data)


def add_data_names(data: dict[int, str]):
    data_names.update(data)


def add_import_names(data: dict[int, str]):
    import_names.update(data)


def add_strings(data: dict[int, str]):
    strings.update(data)
