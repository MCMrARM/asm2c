from asm2c import get_fn_sig, decompile_all
from ctx import add_sub_names, add_data_names, add_strings, get_data_name, sub_names, get_sub_name, add_import_names, \
    import_names


def generate_output(program, ida_data):
    sub_addrs = list(int(x, 16) for x in ida_data['funcs'])
    program.check_cookie_addr = ida_data['check_cookie_func']
    add_sub_names({int(k, 16): v for k, v in ida_data['func_names'].items()})
    add_import_names({int(k, 16): v for k, v in ida_data['func_imports'].items()})
    add_data_names({int(k, 16): v for k, v in ida_data['data_names'].items()})
    add_strings({int(k, 16): v for k, v in ida_data['strings'].items()})

    print('#include <asm2c.h>')
    print('#include <array>')
    for addr, vt in ida_data['vtables'].items():
        print(f'extern std::array<afunc_t*, {len(vt)}> ' + get_data_name(int(addr, 16))[0] + ';')
    for addr in [*sub_names.keys(), *import_names.keys()]:
        print(get_fn_sig(addr) + ';')
    decompile_all(program, sub_addrs)
    for addr, vt in ida_data['vtables'].items():
        print(f'std::array<afunc_t*, {len(vt)}> ' + get_data_name(int(addr, 16))[0] + ' = {')
        for x in vt:
            print(f'  {get_sub_name(int(x, 16))},')
        print('};')
