import pytest
from voluptuous import Schema

from numdoclint import check_py_module


def test__check_module_exists():
    check_py_module._check_module_exists(
        py_module_path='./tests/test_check_py_module.py')
    with pytest.raises(FileNotFoundError):
        check_py_module._check_module_exists(
            py_module_path='test_not_exists_file.py')


def test__make_info_dict():
    info_dict = check_py_module._make_info_dict(
        module_path='sample/path/to/module.py',
        func_name='sample_func',
        info_id=3,
        info='Sample information.')
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: \
                'sample/path/to/module.py',
            check_py_module.INFO_KEY_FUNC_NAME: 'sample_func',
            check_py_module.INFO_KEY_INFO_ID: 3,
            check_py_module.INFO_KEY_INFO: 'Sample information.',
        },
        required=True)
    schema(info_dict)
