import importlib
import idautils
import idaapi
import json
import ida_nalt
import ida_xref
import ida_funcs
from runpy import run_path

globals().update(run_path("user_data.py"))


explored = set()
empty_string_ea = None
imports = {}
dump_funcs = []
dump_imports = {}
dump_names = {}
dump_vtables = {}
dump_strings = {}
logfile = open('ida_log.txt', 'w')


def resolve_dict_symbols(m: dict):
    if None not in m:
        return m
    names = m.pop(None)
    for name in names:
        m[idaapi.get_name_ea(idaapi.BADADDR, name)] = name
    return m


def find_imports():
    for i in range(ida_nalt.get_import_module_qty()):
        mod_name = ida_nalt.get_import_module_name(i)

        def imp_cb(ea, name, ordinal):
            if not name:
                name = f'{mod_name}_{ordinal}'

            imports[ea] = name
            return True

        ida_nalt.enum_import_names(i, imp_cb)


def try_find_empty_string():
    global empty_string_ea
    str1 = idaapi.get_name_ea(idaapi.BADADDR, 'Str1')
    if ida_bytes.get_byte(str1) == 0:
        empty_string_ea = str1


def try_recognize_import(ea):
    xrefs = list(idautils.XrefsFrom(ea, ida_xref.XREF_ALL))
    if len(xrefs) == 1 and (xrefs[0].type == ida_xref.fl_JN or xrefs[0].type == ida_xref.fl_JF):
        ret = try_recognize_import(xrefs[0].to)
        if ret:
            dump_names[ea] = ret
        return ret
    if len(xrefs) == 1 and xrefs[0].type == ida_xref.dr_R:
        dump_names[ea] = idaapi.get_short_name(ea).partition('(')[0].replace('::', '$')
        return dump_names[ea]
    return False


def try_recognize_crt_exception_throw(ea):
    if ida_funcs.calc_func_size(ea) > 0x100:
        return False

    call_eas = []
    offsets = []
    for inst_ea in idautils.FuncItems(ea):
        for xref in idautils.XrefsFrom(inst_ea, ida_xref.XREF_ALL):
            if xref.type == idaapi.fl_CN or xref.type == idaapi.fl_CF:
                call_eas.append(xref.to)
            if xref.type == idaapi.fl_JN or xref.type == idaapi.fl_JF:
                return False
            if xref.type == idaapi.dr_O:
                offsets.append(xref.to)

    if len(call_eas) != 2 or len(offsets) != 1:
        return False
    if idaapi.get_name(call_eas[1]) != '_CxxThrowException':
        return False
    name = idaapi.get_name(offsets[0])
    if name == '__TI2?AVbad_alloc@std@@':
        dump_names[ea] = '__scrt_throw_std_bad_alloc'
    elif name == '__TI3?AVbad_array_new_length@std@@':
        dump_names[ea] = '__scrt_throw_std_bad_array_new_length'
    else:
        return False
    return True


def explore_fn(ea):
    if ea in explored:
        return
    explored.add(ea)

    fn = idaapi.get_func(ea)
    if fn is None:
        return

    if try_recognize_import(ea):
        return
    if try_recognize_crt_exception_throw(ea):
        return

    dump_funcs.append(ea)

    for inst_ea in idautils.FuncItems(ea):
        for xref in idautils.XrefsFrom(inst_ea, ida_xref.XREF_ALL):
            if xref.type == idaapi.fl_CN or xref.type == idaapi.fl_CF:
                print("%x -> %x [call]" % (inst_ea, xref.to), file=logfile)
                explore_fn(xref.to)
            if (xref.type == idaapi.fl_JF or xref.type == idaapi.fl_JN) and idaapi.get_func(xref.to).start_ea == xref.to:
                print("%x -> %x [jump]" % (inst_ea, xref.to), file=logfile)
                explore_fn(xref.to)
            if xref.type == idaapi.dr_O:
                print("%x -> %x [offset]" % (inst_ea, xref.to), file=logfile)
                if idaapi.get_func(get_qword(xref.to)) is not None:
                    explore_vt(xref.to)
                elif ida_nalt.get_str_type(xref.to) == ida_nalt.STRTYPE_C:
                    dump_strings[xref.to] = idaapi.get_strlit_contents(xref.to, -1, ida_nalt.STRTYPE_C).decode()
                elif xref.to == empty_string_ea:
                    dump_strings[xref.to] = ''
            if xref.type == idaapi.dr_R:
                print("%x -> %x [read]" % (inst_ea, xref.to), file=logfile)
                if xref.to in imports:
                    dump_imports[xref.to] = imports[xref.to]


def explore_vt(ea):
    if ea in dump_vtables:
        return
    ret = [get_qword(ea)]
    for i in range(1, 100):
        if idaapi.get_name(ea + i * 8):
            break
        ptr = get_qword(ea + i * 8)
        if idaapi.get_func(ptr) is not None:
            ret.append(ptr)
    print("%x [vtable]" % ea, "=", ', '.join([hex(x) for x in ret]), file=logfile)
    dump_vtables[ea] = ret
    for ptr in ret:
        explore_fn(ptr)


func_roots = resolve_dict_symbols(func_roots)
vt_roots = resolve_dict_symbols(vt_roots)
overrides = resolve_dict_symbols(overrides)
data_names = resolve_dict_symbols(data_names)

explored.update(overrides.keys())
find_imports()
try_find_empty_string()
for ea, name in func_roots.items():
    explore_fn(ea)
for ea, name in vt_roots.items():
    explore_vt(ea)

with open('ida_data.json', 'w') as f:
    f.write(json.dumps({
        'check_cookie_func': hex(idaapi.get_name_ea(idaapi.BADADDR, '__security_check_cookie')),
        'funcs': [hex(x) for x in dump_funcs],
        'func_names': {hex(k): 'asm2c_' + v for k, v in dump_names.items()} |
                      {hex(k): v for k, v in func_roots.items()} |
                      {hex(k): v for k, v in overrides.items()},
        'func_imports': {hex(k): 'asm2c_' + v for k, v in dump_imports.items()},
        'data_names': {hex(k): v for k, v in data_names.items()} |
                      {hex(k): v for k, v in vt_roots.items()},
        'vtables': {hex(k): [hex(x) for x in v] for k, v in dump_vtables.items()},
        'strings': {hex(k): v for k, v in dump_strings.items()},
    }, indent=4))
logfile.close()