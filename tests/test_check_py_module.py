import shutil
import os

import pytest
from voluptuous import Schema

from numdoclint import check_py_module
from numdoclint.helper import (
    DOC_PARAM_INFO_KEY_ARG_NAME, DOC_PARAM_INFO_KEY_TYPE_NAME,
    DOC_PARAM_INFO_KEY_DEFAULT_VAL, DOC_PARAM_INFO_KEY_DESCRIPTION,
    DOC_RETURN_INFO_KEY_NAME, DOC_RETURN_INFO_KEY_TYPE_NAME,
    DOC_RETURN_INFO_KEY_DESCRIPTION)

TMP_TEST_MODULE_DIR = './tests/tmp/'
TMP_TEST_MODULE_PATH = os.path.join(
    TMP_TEST_MODULE_DIR, 'tmp.py')


def setup():
    """Function to be executed at the start of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)
    os.makedirs(TMP_TEST_MODULE_DIR)
    init_file_path = os.path.join(TMP_TEST_MODULE_DIR, '__init__.py')
    with open(init_file_path, 'w') as f:
        f.write('\n')


def teardown():
    """Function to be executed at the end of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)


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


def test__check_lacked_docstring_param_type():
    expected_module_path = 'test/path/to/module.py'
    expected_func_name = 'test_func'
    param_info_list = [{
        DOC_PARAM_INFO_KEY_ARG_NAME: 'price',
        DOC_PARAM_INFO_KEY_TYPE_NAME: '',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample price.',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'name',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'str',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample name.',
    }]
    info_list = check_py_module._check_lacked_docstring_param_type(
        module_path=expected_module_path,
        func_name=expected_func_name,
        param_info_list=param_info_list)
    assert len(info_list) == 1
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_DOCSTRING_PARAM_TYPE,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema(info_list[0])


def test__check_docstring_param_order():
    expected_module_path = 'test/module/path.py'
    expected_func_name = 'test_func_name'
    arg_name_list = ['price', 'name']
    param_info_list = [{
        DOC_PARAM_INFO_KEY_ARG_NAME: 'price',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample price.',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'name',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'str',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample name.',
    }]

    info_list = check_py_module._check_docstring_param_order(
        module_path=expected_module_path,
        func_name=expected_func_name,
        arg_name_list=arg_name_list[:1],
        param_info_list=param_info_list)
    assert info_list == []

    info_list = check_py_module._check_docstring_param_order(
        module_path=expected_module_path,
        func_name=expected_func_name,
        arg_name_list=arg_name_list,
        param_info_list=param_info_list)
    assert info_list == []

    arg_name_list = list(reversed(arg_name_list))
    info_list = check_py_module._check_docstring_param_order(
        module_path=expected_module_path,
        func_name=expected_func_name,
        arg_name_list=arg_name_list,
        param_info_list=param_info_list)
    assert len(info_list) == 1
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_DIFFERENT_PARAM_ORDER,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema(info_list[0])


def test__check_func_description():
    expected_module_path = 'sample/module/path.py'
    expected_func_name = 'sample_func'
    docstring = """
    Sample docstring.

    Parameters
    ----------
    price : int
        Sample price.
    """
    info_list = check_py_module._check_func_description(
        module_path=expected_module_path,
        func_name='test_func',
        docstring=docstring)
    assert info_list == []

    info_list = check_py_module._check_func_description(
        module_path=expected_module_path,
        func_name=expected_func_name,
        docstring=docstring)
    assert info_list == []

    docstring = """
    Parameters
    ----------
    price : int
        Sample price.
    """
    info_list = check_py_module._check_func_description(
        module_path=expected_module_path,
        func_name=expected_func_name,
        docstring=docstring)
    assert len(info_list) == 1
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_FUNC_DESCRIPTION,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema(info_list[0])


def test__check_lacked_default_value():
    expected_module_path = 'sample/module/path.py'
    expected_func_name = 'sample_func'

    param_info_list = [{
        DOC_PARAM_INFO_KEY_ARG_NAME: 'price',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample price.',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'location_id',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '100',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample location id.',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'season',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '3',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample season type.',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'tax',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '5',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample tax value.',
    }]
    default_val_info_dict = {
        'price': '200',
        'location_id': '',
        'tax': '5',
    }
    info_list = check_py_module._check_lacked_default_value(
        module_path=expected_module_path,
        func_name=expected_func_name,
        param_info_list=param_info_list,
        default_val_info_dict=default_val_info_dict)
    assert len(info_list) == 2
    schema_1 = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_DOC_DEFAULT_VALUE,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema_1(info_list[0])
    schema_2 = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_ARG_DEFAULT_VALUE,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema_2(info_list[1])


def test__check_lacked_return():
    expected_module_path = 'sample/module/path.py'
    expected_func_name = 'sample_func'
    info_list = check_py_module._check_lacked_return(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=[],
        return_val_exists_in_func=False)
    assert info_list == []

    return_val_info_list = [{
        DOC_RETURN_INFO_KEY_NAME: 'price',
        DOC_RETURN_INFO_KEY_TYPE_NAME: 'int',
        DOC_RETURN_INFO_KEY_DESCRIPTION: 'Sample price.',
    }, {
        DOC_RETURN_INFO_KEY_NAME: 'name',
        DOC_RETURN_INFO_KEY_TYPE_NAME: 'str',
        DOC_RETURN_INFO_KEY_DESCRIPTION: 'Sample name.',
    }]
    info_list = check_py_module._check_lacked_return(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=return_val_info_list,
        return_val_exists_in_func=True)
    assert info_list == []

    info_list = check_py_module._check_lacked_return(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=[],
        return_val_exists_in_func=True)
    assert len(info_list) == 1
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_DOCSTRING_RETURN,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema(info_list[0])

    info_list = check_py_module._check_lacked_return(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=return_val_info_list,
        return_val_exists_in_func=False)
    assert len(info_list) == 1
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_RETURN_VAL,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema(info_list[0])


def test__check_lacked_return_docstring_type():
    expected_module_path = 'sample/module/path.py'
    expected_func_name = 'sample_func'

    info_list = check_py_module._check_lacked_return_docstring_type(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=[])
    assert info_list == []

    return_val_info_list = [{
        DOC_RETURN_INFO_KEY_NAME: 'price',
        DOC_RETURN_INFO_KEY_TYPE_NAME: '',
        DOC_RETURN_INFO_KEY_DESCRIPTION: 'Sample price.',
    }, {
        DOC_RETURN_INFO_KEY_NAME: 'name',
        DOC_RETURN_INFO_KEY_TYPE_NAME: '',
        DOC_RETURN_INFO_KEY_DESCRIPTION: 'Sample name.',
    }, {
        DOC_RETURN_INFO_KEY_NAME: 'location_id',
        DOC_RETURN_INFO_KEY_TYPE_NAME: 'int',
        DOC_RETURN_INFO_KEY_DESCRIPTION: 'Sample location id.',
    }]
    info_list = check_py_module._check_lacked_return_docstring_type(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=return_val_info_list)
    assert len(info_list) == 2
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_DOCSTRING_RETURN_TYPE,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)
    assert 'price' in info_list[0][check_py_module.INFO_KEY_INFO]
    assert 'name' in info_list[1][check_py_module.INFO_KEY_INFO]


def test__check_lacked_docstring_param_description():
    expected_module_path = 'sample/module/path.py'
    expected_func_name = 'sample_func'

    info_list = check_py_module._check_lacked_docstring_param_description(
        module_path=expected_module_path,
        func_name=expected_func_name,
        param_info_list=[])
    assert info_list == []

    param_info_list = [{
        DOC_PARAM_INFO_KEY_ARG_NAME: 'price',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: '',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'name',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'str',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: 'Apple',
        DOC_PARAM_INFO_KEY_DESCRIPTION: '',
    }, {
        DOC_PARAM_INFO_KEY_ARG_NAME: 'location_id',
        DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
        DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
        DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample location id.',
    }]
    info_list = check_py_module._check_lacked_docstring_param_description(
        module_path=expected_module_path,
        func_name=expected_func_name,
        param_info_list=param_info_list)
    assert len(info_list) == 2
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_DOCSTRING_PARAM_DESCRIPTION,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)
    assert 'price' in info_list[0][check_py_module.INFO_KEY_INFO]
    assert 'name' in info_list[1][check_py_module.INFO_KEY_INFO]


def test__check_lacked_return_docstring_description():
    expected_module_path = 'sample/module/path.py'
    expected_func_name = 'sample_func'

    info_list = check_py_module._check_lacked_return_docstring_description(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=[])
    assert info_list == []

    return_val_info_list = [{
        DOC_RETURN_INFO_KEY_NAME: 'price',
        DOC_RETURN_INFO_KEY_TYPE_NAME: 'int',
        DOC_RETURN_INFO_KEY_DESCRIPTION: '',
    }, {
        DOC_RETURN_INFO_KEY_NAME: 'name',
        DOC_RETURN_INFO_KEY_TYPE_NAME: 'str',
        DOC_RETURN_INFO_KEY_DESCRIPTION: '',
    }, {
        DOC_RETURN_INFO_KEY_NAME: 'location_id',
        DOC_RETURN_INFO_KEY_TYPE_NAME: 'str',
        DOC_RETURN_INFO_KEY_DESCRIPTION: 'Sample location id.',
    }]
    info_list = check_py_module._check_lacked_return_docstring_description(
        module_path=expected_module_path,
        func_name=expected_func_name,
        return_val_info_list=return_val_info_list)
    assert len(info_list) == 2
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: expected_module_path,
            check_py_module.INFO_KEY_FUNC_NAME: expected_func_name,
            check_py_module.INFO_KEY_INFO_ID: \
                check_py_module.INFO_ID_LACKED_DOCSTRING_RETURN_DESCRIPTION,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    schema(info_list[0])
    schema(info_list[1])
    assert 'price' in info_list[0][check_py_module.INFO_KEY_INFO]
    assert 'name' in info_list[1][check_py_module.INFO_KEY_INFO]


def _check_info_list_schema(info_list):
    """
    Check the list schema of lint result information.

    Parameters
    ----------
    info_list : list of dicsts
        A list of check results for one function.

    Raises
    ------
    MultipleInvalid
        If the schema is invalid.
    """
    schema = Schema(
        schema={
            check_py_module.INFO_KEY_MODULE_PATH: str,
            check_py_module.INFO_KEY_FUNC_NAME: str,
            check_py_module.INFO_KEY_INFO_ID: int,
            check_py_module.INFO_KEY_INFO: str,
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)


def _check_info_id_is_in_list(expected_info_id, info_list):
    """
    Check that the target info id is included in the list.

    Parameters
    ----------
    expected_info_id : int
        The expected info id included in the list.
    info_list : list of dicts
        A list of check results for one function.

    Raises
    ------
    AssertionError
        If the target id is not included in the list.
    """
    id_list = [info_dict[check_py_module.INFO_KEY_INFO_ID]
               for info_dict in info_list]
    is_in = expected_info_id in id_list
    assert is_in


def test__get_single_func_info_list():

    module_str = '''
import os
import sys


def sample_func_1(price):
    """
    Parameters
    ----------
    price : int
        Sample price.
    """
    pass


def sample_func_2():
    """
    Sample function.

    Parameters
    ----------
    price : int
        Sample price.
    """
    pass


def sample_func_3(price):
    """
    Sample function.
    """
    pass


def sample_func_4(price):
    """
    Sample function.

    Parameters
    ----------
    price
        Sample price.
    """
    pass


def sample_func_5(price):
    """
    Sample function.

    Parameters
    ----------
    price : int
    """
    pass


def sample_func_6(price, name):
    """
    Sample function.

    Parameters
    ----------
    name : str
        Sample name.
    price : int
        Sample price.
    """
    pass


def sample_func_7(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : int
        Sample price.
    """
    pass


def sample_func_8(price):
    """
    Sample function.

    Parameters
    ----------
    price : int, default 100
        Sample price.
    """
    pass


def sample_func_9():
    """
    Sample function.

    Returns
    -------
    price : int
        Sample price.
    """
    pass


def sample_func_10():
    """
    Sample function.
    """
    return 100


def sample_func_11():
    """
    Sample function.

    Returns
    -------
    price
        Sample price.
    """
    return 100


def sample_func_12():
    """
    Sample function.

    Returns
    -------
    price : int
    """
    return 100


def sample_func_13(price: int, name='apple': str) -> int:
    """
    Sample function.

    Parameters
    ----------
    price : int
        Sample price
    name : str, default 'apple'
        Sample name.

    Returns
    -------
    x : int
        Sample value.
    y : int
        Sample value.
    """
    return 100, 200
'''

    def _exec_target_func(func_name):
        """
        Execute the function to be tested and get the return value.

        Parameters
        ----------
        func_name : str
            Target function name.
        """
        info_list = check_py_module._get_single_func_info_list(
            module_path=TMP_TEST_MODULE_PATH,
            module_str=module_str,
            func_name=func_name)
        return info_list

    with open(TMP_TEST_MODULE_PATH, 'w') as f:
        f.write(module_str)

    info_list = _exec_target_func(func_name='sample_func_1')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_FUNC_DESCRIPTION,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_2')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_ARGUMENT,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_3')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_DOCSTRING_PARAM,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_4')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_DOCSTRING_PARAM_TYPE,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_5')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.\
            INFO_ID_LACKED_DOCSTRING_PARAM_DESCRIPTION,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_6')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_DIFFERENT_PARAM_ORDER,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_7')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_DOC_DEFAULT_VALUE,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_8')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_ARG_DEFAULT_VALUE,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_9')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_RETURN_VAL,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_10')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.INFO_ID_LACKED_DOCSTRING_RETURN,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_11')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=\
            check_py_module.INFO_ID_LACKED_DOCSTRING_RETURN_TYPE,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_12')
    _check_info_list_schema(info_list=info_list)
    _check_info_id_is_in_list(
        expected_info_id=check_py_module.\
            INFO_ID_LACKED_DOCSTRING_RETURN_DESCRIPTION,
        info_list=info_list)

    info_list = _exec_target_func(func_name='sample_func_13')
    assert info_list == []
