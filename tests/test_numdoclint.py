import inspect

import numdoclint
from numdoclint import py_module


def test_interface():
    interface_name_list = [
        'check_python_module',
        'check_python_module_recursively',
    ]
    for interface_name in interface_name_list:
        assert hasattr(numdoclint, interface_name)
        interface_func = getattr(numdoclint, interface_name)
        assert callable(interface_func)


def test_info_id_constants():
    numdoclint_info_id_const_num = 0
    members = inspect.getmembers(numdoclint)
    for name, obj in members:
        if not name.startswith('INFO_ID_'):
            continue
        if not isinstance(obj, int):
            continue
        numdoclint_info_id_const_num += 1

    py_module_const_num = 0
    members = inspect.getmembers(py_module)
    for name, obj in members:
        if not name.startswith('INFO_ID_'):
            continue
        if not isinstance(obj, int):
            continue
        py_module_const_num += 1

    assert numdoclint_info_id_const_num == py_module_const_num
