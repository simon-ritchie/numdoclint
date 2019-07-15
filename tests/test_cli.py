import os
import shutil

import pytest
import six
from voluptuous import Any, Schema

from numdoclint import cli
from numdoclint import py_module

TMP_TEST_MODULE_DIR = 'tests/tmp_test/'
TMP_TEST_MODULE_PATH_1 = os.path.join(
    TMP_TEST_MODULE_DIR,
    'tmp_test_1.py')
TMP_TEST_MODULE_PATH_2 = os.path.join(
    TMP_TEST_MODULE_DIR,
    'tmp_test_2.py')


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


def test__get_list_of_str_from_csv():
    result_list = cli._get_list_of_str_from_csv(csv='')
    assert result_list == []
    result_list = cli._get_list_of_str_from_csv(csv='apple,orange')
    assert result_list == ['apple', 'orange']


def test__get_list_of_int_from_csv():
    result_list = cli._get_list_of_int_from_csv(csv='')
    assert result_list == []
    result_list = cli._get_list_of_int_from_csv(csv='1,2,3')
    assert result_list == [1, 2, 3]


def test__validate_args():
    with pytest.raises(Exception):
        cli._validate_args(
            path=None,
            ignore_info_id_list=[],
            check_recursively=False)
    with pytest.raises(Exception):
        cli._validate_args(
            path='sample/path.py',
            ignore_info_id_list=[-1],
            check_recursively=False)
    with pytest.raises(Exception):
        cli._validate_args(
            path='sample/path.py',
            ignore_info_id_list=[],
            check_recursively=True)
    cli._validate_args(
        path='sample/path.py',
        ignore_info_id_list=[],
        check_recursively=False)


def test__exec_numdoclist():
    module_str_1 = """
def sample_func_1(price):
    pass
    """
    with open(TMP_TEST_MODULE_PATH_1, 'w') as f:
        f.write(module_str_1)
    module_str_2 = '''
@Appender
def sample_func_2(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : bool
        Sample price
    """
    pass
    '''
    with open(TMP_TEST_MODULE_PATH_2, 'w') as f:
        f.write(module_str_2)

    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_PATH_1,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    schema = Schema(
        schema={
            py_module.INFO_KEY_MODULE_PATH: TMP_TEST_MODULE_PATH_1,
            py_module.INFO_KEY_FUNC_NAME: 'sample_func_1',
            py_module.INFO_KEY_INFO_ID: int,
            py_module.INFO_KEY_INFO: Any(*six.string_types),
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)
    info_id_list = [
        info_dict[py_module.INFO_KEY_INFO_ID] for info_dict in info_list]
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_PATH_1,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_suffix_list=['sample_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_PATH_1,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=info_id_list,
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_PATH_2,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_PATH_2,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_PATH_2,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=['Appender'])
    assert info_list == []

    schema = Schema(
        schema={
            py_module.INFO_KEY_MODULE_PATH: Any(*six.string_types),
            py_module.INFO_KEY_FUNC_NAME: Any(*six.string_types),
            py_module.INFO_KEY_INFO_ID: int,
            py_module.INFO_KEY_INFO: Any(*six.string_types),
        },
        required=True)
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list
    for info_dict in info_list:
        schema(info_dict)
    module_path_list = [
        info_dict[py_module.INFO_KEY_MODULE_PATH] for info_dict in info_list]
    module_path_1_exists = False
    module_path_2_exists = False
    for module_path in module_path_list:
        if TMP_TEST_MODULE_PATH_1 in module_path:
            module_path_1_exists = True
            continue
        if TMP_TEST_MODULE_PATH_2 in module_path:
            module_path_2_exists = True
            continue
    assert module_path_1_exists
    assert module_path_2_exists
    info_id_list = [
        info_dict[py_module.INFO_KEY_INFO_ID] for info_dict in info_list]
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_suffix_list=['test_', 'sample_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=info_id_list,
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []

    info_list = cli._exec_numdoclist(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False,
        skip_decorator_name_list=[])
    info_id_list = [
        info_dict[py_module.INFO_KEY_INFO_ID] for info_dict in info_list]
    for info_id in info_id_list:
        assert info_id != py_module.INFO_ID_LACKED_DOC_DEFAULT_VALUE
