import os
import shutil
from typing import List

import pytest
import six
from voluptuous import Any, Schema

from numdoclint import cli, jupyter_notebook, py_module

TMP_TEST_MODULE_DIR: str = 'tests/tmp_test/'
TMP_TEST_MODULE_PATH_1: str = os.path.join(
    TMP_TEST_MODULE_DIR,
    'tmp_test_1.py')
TMP_TEST_MODULE_PATH_2: str = os.path.join(
    TMP_TEST_MODULE_DIR,
    'tmp_test_2.py')


def setup() -> None:
    """Function to be executed at the start of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)
    os.makedirs(TMP_TEST_MODULE_DIR)
    init_file_path: str = os.path.join(TMP_TEST_MODULE_DIR, '__init__.py')
    with open(init_file_path, 'w') as f:
        f.write('\n')


def teardown() -> None:
    """Function to be executed at the end of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)


def test__get_list_of_str_from_csv() -> None:
    result_list: List[str] = cli._get_list_of_str_from_csv(csv='')
    assert result_list == []
    result_list = cli._get_list_of_str_from_csv(csv='apple,orange')
    assert result_list == ['apple', 'orange']


def test__get_list_of_int_from_csv() -> None:
    result_list: List[int] = cli._get_list_of_int_from_csv(csv='')
    assert result_list == []
    result_list = cli._get_list_of_int_from_csv(csv='1,2,3')
    assert result_list == [1, 2, 3]


def _assert_default_value_check_info_id_is_in(info_list: List[dict]) -> None:
    """
    Check that the check result of the default value
    is included in the list.

    Parameters
    ----------
    info_list : list of dict
        List of check results.

    Raises
    ------
    AssertionError
        If not included in the list.
    """
    default_val_info_exists: bool = False
    for info_dict in info_list:
        if (info_dict[py_module.INFO_KEY_INFO_ID]
                == py_module.INFO_ID_LACKED_DOC_DEFAULT_VALUE):
            default_val_info_exists = True
            break
    assert default_val_info_exists


def _assert_default_value_check_info_id_is_not_in(
        info_list: List[dict]) -> None:
    """
    Check that the check result of the default value is not
    included in the list.

    Parameters
    ----------
    info_list : list of dicts
        List of check results.

    Raises
    ------
    AssertionError
        If included in the list.
    """
    info_id_list: List[int] = [
        info_dict[py_module.INFO_KEY_INFO_ID] for info_dict in info_list]
    for info_id in info_id_list:
        assert info_id != py_module.INFO_ID_LACKED_DOC_DEFAULT_VALUE


def test__validate_args() -> None:
    with pytest.raises(Exception):  # type: ignore
        cli._validate_args(
            path=None,  # type: ignore
            ignore_info_id_list=[],
            check_recursively=False)
    with pytest.raises(Exception):  # type: ignore
        cli._validate_args(
            path='sample/path.py',
            ignore_info_id_list=[-1],
            check_recursively=False)
    with pytest.raises(Exception):  # type: ignore
        cli._validate_args(
            path='sample/path.py',
            ignore_info_id_list=[],
            check_recursively=True)
    cli._validate_args(
        path='sample/path.py',
        ignore_info_id_list=[],
        check_recursively=False)


def test__exec_numdoclint() -> None:
    module_str_1: str = """
def sample_func_1(price):
    pass
    """
    with open(TMP_TEST_MODULE_PATH_1, 'w') as f:
        f.write(module_str_1)
    module_str_2: str = '''
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

    info_list: List[dict] = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_PATH_1,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    schema: Schema = Schema(
        schema={
            py_module.INFO_KEY_MODULE_PATH: TMP_TEST_MODULE_PATH_1,
            py_module.INFO_KEY_FUNC_NAME: 'sample_func_1',
            py_module.INFO_KEY_INFO_ID: int,
            py_module.INFO_KEY_INFO: Any(*six.string_types),
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)
    info_id_list: List[int] = [
        info_dict[py_module.INFO_KEY_INFO_ID] for info_dict in info_list]
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_PATH_1,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_prefix_list=['sample_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_PATH_1,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=info_id_list,
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_PATH_2,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_PATH_2,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_PATH_2,
        check_recursively=False,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
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
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list
    for info_dict in info_list:
        schema(info_dict)
    module_path_list: List[str] = [
        info_dict[py_module.INFO_KEY_MODULE_PATH] for info_dict in info_list]
    module_path_1_exists: bool = False
    module_path_2_exists: bool = False
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
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_prefix_list=['test_', 'sample_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=info_id_list,
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []

    info_list = cli._exec_numdoclint(
        path=TMP_TEST_MODULE_DIR,
        check_recursively=True,
        is_jupyter=False,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False,
        skip_decorator_name_list=[])
    info_id_list = [
        info_dict[py_module.INFO_KEY_INFO_ID] for info_dict in info_list]
    _assert_default_value_check_info_id_is_not_in(info_list=info_list)
    schema = Schema(
        schema={
            jupyter_notebook.INFO_KEY_NOTEBOOK_PATH:
            './tests/jupyter/test_jupyter_notebook_py3.ipynb',
            jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: int,
            jupyter_notebook.INFO_KEY_FUNC_NAME: Any(*six.string_types),
            jupyter_notebook.INFO_KEY_INFO_ID: int,
            jupyter_notebook.INFO_KEY_INFO: Any(*six.string_types),
        },
        required=True)
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/test_jupyter_notebook_py3.ipynb',
        check_recursively=False,
        is_jupyter=True,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list
    for info_dict in info_list:
        schema(info_dict)
    info_id_list = [
        info_dict[jupyter_notebook.INFO_KEY_INFO_ID]
        for info_dict in info_list]
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/test_jupyter_notebook_py3.ipynb',
        check_recursively=False,
        is_jupyter=True,
        ignore_func_name_prefix_list=['sample_', 'test_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/test_jupyter_notebook_py3.ipynb',
        check_recursively=False,
        is_jupyter=True,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=info_id_list,
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/test_jupyter_notebook_py3.ipynb',
        check_recursively=False,
        is_jupyter=True,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    _assert_default_value_check_info_id_is_in(info_list=info_list)
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/test_jupyter_notebook_py3.ipynb',
        check_recursively=False,
        is_jupyter=True,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False,
        skip_decorator_name_list=[])
    for info_dict in info_list:
        assert (
            info_dict[jupyter_notebook.INFO_KEY_INFO_ID]
            != py_module.INFO_ID_LACKED_DOC_DEFAULT_VALUE)

    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/',
        check_recursively=True,
        is_jupyter=True,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    schema = Schema(
        schema={
            jupyter_notebook.INFO_KEY_NOTEBOOK_PATH: Any(*six.string_types),
            jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: int,
            jupyter_notebook.INFO_KEY_FUNC_NAME: Any(*six.string_types),
            jupyter_notebook.INFO_KEY_INFO_ID: int,
            jupyter_notebook.INFO_KEY_INFO: Any(*six.string_types),
        },
        required=True)
    assert info_list
    for info_dict in info_list:
        schema(info_dict)
    unique_notebook_path_list = [
        info_dict[jupyter_notebook.INFO_KEY_NOTEBOOK_PATH]
        for info_dict in info_list]
    unique_notebook_path_list = list(set(unique_notebook_path_list))
    assert len(unique_notebook_path_list) > 1
    _assert_default_value_check_info_id_is_in(info_list=info_list)
    info_id_list = [
        info_dict[jupyter_notebook.INFO_KEY_INFO_ID]
        for info_dict in info_list]
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/',
        check_recursively=True,
        is_jupyter=True,
        ignore_func_name_prefix_list=['test_', 'sample_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/',
        check_recursively=True,
        is_jupyter=True,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=info_id_list,
        enable_default_or_optional_doc_check=True,
        skip_decorator_name_list=[])
    assert info_list == []
    info_list = cli._exec_numdoclint(
        path='./tests/jupyter/',
        check_recursively=True,
        is_jupyter=True,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False,
        skip_decorator_name_list=[])
    _assert_default_value_check_info_id_is_not_in(info_list=info_list)


def test_main() -> None:
    module_str_1: str = """
def sample_func_1(price):
    pass
    """
    with open(TMP_TEST_MODULE_PATH_1, 'w') as f:
        f.write(module_str_1)

    class Args:

        path: str = TMP_TEST_MODULE_PATH_1
        check_recursively: bool = False
        is_jupyter: bool = False
        ignore_func_name_prefix_list: List[str] = []
        ignore_info_id_list: List[int] = []
        enable_default_or_optional_doc_check: bool = True
        skip_decorator_name_list: List[str] = []

    args: Args = Args()
    info_list: List[dict] = cli.main(
        args=args,  # type: ignore
        return_list=True)
    assert info_list
    schema: Schema = Schema(
        schema={
            py_module.INFO_KEY_MODULE_PATH: TMP_TEST_MODULE_PATH_1,
            py_module.INFO_KEY_FUNC_NAME: 'sample_func_1',
            py_module.INFO_KEY_INFO_ID: int,
            py_module.INFO_KEY_INFO: Any(*six.string_types),
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)
