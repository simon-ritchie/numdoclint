import os
import shutil
from typing import List

import pytest
import six
from voluptuous import Any, Schema

from numdoclint import jupyter_notebook, py_module

TMP_TEST_MODULE_DIR: str = './tests/tmp/'
TMP_TEST_NOTEBOOK_PATH_1: str = os.path.join(
    TMP_TEST_MODULE_DIR, 'tmp_1.ipynb')
TMP_TEST_NOTEBOOK_PATH_2: str = os.path.join(
    TMP_TEST_MODULE_DIR, 'tmp_2.ipynb')

STR_SCHEMA: Any = Any(*six.string_types)


def setup() -> None:
    """Function to be executed at the start of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)
    os.makedirs(TMP_TEST_MODULE_DIR)


def teardown() -> None:
    """Function to be executed at the end of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)


def _delete_test_notebook() -> None:
    """Delete notebook for testing if exists.
    """
    if os.path.exists(TMP_TEST_NOTEBOOK_PATH_1):
        os.remove(TMP_TEST_NOTEBOOK_PATH_1)
    if os.path.exists(TMP_TEST_NOTEBOOK_PATH_2):
        os.remove(TMP_TEST_NOTEBOOK_PATH_2)


def test__check_notebook_exists() -> None:
    _delete_test_notebook()

    with pytest.raises(IOError):  # type: ignore
        jupyter_notebook._check_notebook_exists(
            notebook_path=TMP_TEST_NOTEBOOK_PATH_1)

    with open(TMP_TEST_NOTEBOOK_PATH_1, 'w') as f:
        f.write('\n')

    jupyter_notebook._check_notebook_exists(
        notebook_path=TMP_TEST_NOTEBOOK_PATH_1)
    _delete_test_notebook()


def test__check_notebook_extension() -> None:
    with pytest.raises(IOError):  # type: ignore
        jupyter_notebook._check_notebook_extension(
            notebook_path='sample/path.py')
    jupyter_notebook._check_notebook_extension(
        notebook_path='sample/path.ipynb')


def test__read_notebook_data_dict() -> None:
    notebook_data_dict: dict = jupyter_notebook._read_notebook_data_dict(
        notebook_path='./tests/jupyter/test_jupyter_notebook_py3.ipynb')
    assert isinstance(notebook_data_dict, dict)
    has_key: bool = 'cells' in notebook_data_dict
    assert has_key


def test__get_code_cell_str_list() -> None:
    code_str_list: List[str] = jupyter_notebook._get_code_cell_str_list(
        notebook_data_dict={})
    assert code_str_list == []

    notebook_data_dict: dict = {
        'cells': [{
            'cell_type': 'code',
            'source': [
                'import pandas as pd\n',
                'import numpy as np',
            ],
        }, {
            'cell_type': 'markdown',
            'source': [
                '# Markdown cell\n',
                '\n',
                'Contents of this cell should be ignored.\n',
            ],
        }, {
            'cell_type': 'code',
            'source': [
                'def sample_func():\n',
                '    pass',
            ],
        }]
    }
    code_str_list = jupyter_notebook._get_code_cell_str_list(
        notebook_data_dict=notebook_data_dict)
    assert len(code_str_list) == 2
    expected_code_str: str = 'import pandas as pd\nimport numpy as np'
    assert code_str_list[0] == expected_code_str
    expected_code_str = 'def sample_func():\n    pass'
    assert code_str_list[1] == expected_code_str


def test__rename_dict_key() -> None:
    info_list: List[dict] = [{
        py_module.INFO_KEY_MODULE_PATH: 'sample/path.ipynb',
        py_module.INFO_KEY_FUNC_NAME: 'sample_func_1',
        py_module.INFO_KEY_INFO_ID: 1,
        py_module.INFO_KEY_INFO: 'Sample information 1.',
    }, {
        py_module.INFO_KEY_MODULE_PATH: 'sample/path.ipynb',
        py_module.INFO_KEY_FUNC_NAME: 'sample_func_2',
        py_module.INFO_KEY_INFO_ID: 2,
        py_module.INFO_KEY_INFO: 'Sample information 2.',
    }]
    info_list = jupyter_notebook._rename_dict_key(
        info_list=info_list)
    assert len(info_list) == 2
    schema: Schema = Schema(
        schema={
            jupyter_notebook.INFO_KEY_NOTEBOOK_PATH: 'sample/path.ipynb',
            jupyter_notebook.INFO_KEY_FUNC_NAME: Any(
                'sample_func_1', 'sample_func_2'),
            jupyter_notebook.INFO_KEY_INFO_ID: Any(1, 2),
            jupyter_notebook.INFO_KEY_INFO: Any(
                'Sample information 1.', 'Sample information 2.'),
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)


def test__add_code_cell_index() -> None:
    info_list: List[dict] = [{}, {}]
    info_list = jupyter_notebook._add_code_cell_index(
        info_list=info_list,
        code_cell_idx=5)
    assert len(info_list) == 2
    schema: Schema = Schema(
        schema={
            jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: 5,
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)


def test__check_unit_code_cell_str() -> None:
    expected_notebook_path: str = 'sample/path.ipynb'
    expected_code_cell_idx: int = 5
    code_cell_str: str = """
import pandas as pd
import numpy as np
    """
    info_list: List[dict] = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False)
    assert info_list == []

    schema: Schema = Schema(
        schema={
            jupyter_notebook.INFO_KEY_NOTEBOOK_PATH: STR_SCHEMA,
            jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: int,
            jupyter_notebook.INFO_KEY_FUNC_NAME: STR_SCHEMA,
            jupyter_notebook.INFO_KEY_INFO_ID: int,
            jupyter_notebook.INFO_KEY_INFO: STR_SCHEMA,
        },
        required=True)

    code_cell_str = '''
import pandas as pd


def sample_func(price):
    return 100
    '''
    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False)
    assert info_list
    for info_dict in info_list:
        schema(info_dict)
        notebook_path = info_dict[jupyter_notebook.INFO_KEY_NOTEBOOK_PATH]
        assert notebook_path == expected_notebook_path
        code_cell_idx = info_dict[jupyter_notebook.INFO_KEY_CODE_CELL_INDEX]
        assert code_cell_idx == expected_code_cell_idx

    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_prefix_list=['sample_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False)
    assert info_list == []

    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[
            py_module.INFO_ID_LACKED_DOCSTRING_PARAM,
            py_module.INFO_ID_LACKED_FUNC_DESCRIPTION,
            py_module.INFO_ID_LACKED_DOCSTRING_RETURN,
        ],
        enable_default_or_optional_doc_check=False)
    assert info_list == []

    code_cell_str = '''
import pandas as pd


def sample_func(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : int
        Sample price.
    """
    pass
    '''
    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False)
    assert info_list == []
    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True)
    assert info_list


def test__print_info_list() -> None:
    printed_str: str = jupyter_notebook._print_info_list(
        info_list=[], verbose=jupyter_notebook.VERBOSE_ENABLED)
    assert printed_str == ''

    info_list: List[dict] = [{
        jupyter_notebook.INFO_KEY_NOTEBOOK_PATH: 'sample/path.ipynb',
        jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: 5,
        jupyter_notebook.INFO_KEY_FUNC_NAME: 'sample_func_1',
        jupyter_notebook.INFO_KEY_INFO_ID: 3,
        jupyter_notebook.INFO_KEY_INFO: 'Sample infomation 1.',
    }, {
        jupyter_notebook.INFO_KEY_NOTEBOOK_PATH: 'sample/path.ipynb',
        jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: 6,
        jupyter_notebook.INFO_KEY_FUNC_NAME: 'sample_func_2',
        jupyter_notebook.INFO_KEY_INFO_ID: 5,
        jupyter_notebook.INFO_KEY_INFO: 'Sample infomation 2.',
    }]

    printed_str = jupyter_notebook._print_info_list(
        info_list=info_list,
        verbose=jupyter_notebook.VERBOSE_DISABLED)
    assert printed_str == ''

    printed_str = jupyter_notebook._print_info_list(
        info_list=info_list,
        verbose=jupyter_notebook.VERBOSE_ENABLED)
    assert 'sample/path.ipynb' in printed_str
    assert 'sample_func_1' in printed_str
    assert '5' in printed_str
    assert 'Sample infomation 1.' in printed_str
    assert '6' in printed_str
    assert 'sample_func_2' in printed_str
    assert 'Sample infomation 2.' in printed_str


schema: Schema = Schema(
    schema={
        jupyter_notebook.INFO_KEY_NOTEBOOK_PATH: STR_SCHEMA,
        jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: int,
        jupyter_notebook.INFO_KEY_FUNC_NAME: STR_SCHEMA,
        jupyter_notebook.INFO_KEY_INFO_ID: int,
        jupyter_notebook.INFO_KEY_INFO: STR_SCHEMA,
    }, required=True)


def test_check_jupyter_notebook() -> None:
    notebook_path: str = './tests/jupyter/test_jupyter_notebook_py3.ipynb'
    info_list: List[dict] = jupyter_notebook.check_jupyter_notebook(
        notebook_path=notebook_path,
        verbose=0,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True)
    assert info_list
    for info_dict in info_list:
        schema(info_dict)
    assert len(info_list) >= 10

    ignore_info_id_list: List[int] = [
        info_dict[jupyter_notebook.INFO_KEY_INFO_ID]
        for info_dict in info_list]

    info_list = jupyter_notebook.check_jupyter_notebook(
        notebook_path=notebook_path,
        verbose=0,
        ignore_func_name_prefix_list=['test_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True)
    assert info_list == []

    info_list = jupyter_notebook.check_jupyter_notebook(
        notebook_path=notebook_path,
        verbose=0,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=ignore_info_id_list,
        enable_default_or_optional_doc_check=True)
    info_list
    assert info_list == []

    notebook_path = './tests/jupyter/test_blank_notebook.ipynb'
    info_list = jupyter_notebook.check_jupyter_notebook(
        notebook_path=notebook_path,
        verbose=jupyter_notebook.VERBOSE_DISABLED,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True)
    assert info_list == []


def test_check_jupyter_notebook_recursively() -> None:
    info_list: List[dict] = \
        jupyter_notebook.check_jupyter_notebook_recursively(
            dir_path='./numdoclint/',
            verbose=jupyter_notebook.VERBOSE_DISABLED,
            ignore_func_name_prefix_list=[],
            ignore_info_id_list=[],
            enable_default_or_optional_doc_check=True)
    assert info_list == []

    info_list = jupyter_notebook.check_jupyter_notebook_recursively(
        dir_path='./tests/',
        verbose=jupyter_notebook.VERBOSE_DISABLED,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True)
    assert info_list
    for info_dict in info_list:
        schema(info_dict)
    notebook_path_list: List[str] = [
        info_dict[jupyter_notebook.INFO_KEY_NOTEBOOK_PATH]
        for info_dict in info_list]
    unique_path_list: List[str] = list(set(notebook_path_list))
    assert len(unique_path_list) > 1

    ignore_info_id_list: List[int] = [
        info_dict[jupyter_notebook.INFO_KEY_INFO_ID]
        for info_dict in info_list]

    info_list = jupyter_notebook.check_jupyter_notebook_recursively(
        dir_path='./tests/',
        verbose=jupyter_notebook.VERBOSE_DISABLED,
        ignore_func_name_prefix_list=['test_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True)
    assert info_list == []

    info_list = jupyter_notebook.check_jupyter_notebook_recursively(
        dir_path='./tests/',
        verbose=jupyter_notebook.VERBOSE_DISABLED,
        ignore_func_name_prefix_list=[],
        ignore_info_id_list=ignore_info_id_list,
        enable_default_or_optional_doc_check=True)
    assert info_list == []
