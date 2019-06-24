import pytest
from voluptuous import Schema

from numdoclint import check_py_module
from numdoclint.helper import (
    DOC_PARAM_INFO_KEY_ARG_NAME, DOC_PARAM_INFO_KEY_TYPE_NAME,
    DOC_PARAM_INFO_KEY_DEFAULT_VAL, DOC_PARAM_INFO_KEY_DESCRIPTION)


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


def test__check_lacked_param():
    expected_module_path = 'test/module/path.py'
    expected_func_name = 'test_func_name'
    arg_name_list = ['name', 'location_id']
    param_info_list = [{
        DOC_PARAM_INFO_KEY_ARG_NAME: 'name',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'str',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample name.',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'price',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample price.',
    }]
    info_list = check_py_module._check_lacked_param(
        module_path=expected_module_path,
        func_name=expected_func_name,
        arg_name_list=arg_name_list,
        param_info_list=param_info_list)
    assert len(info_list) == 2
    schema_1 = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_ARGUMENT,
            check_py_module.INFO_KEY_INFO: str,
        }, required=True)
    schema_1(info_list[0])
    schema_2 = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_DOCSTRING_PARAM,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema_2(info_list[1])
