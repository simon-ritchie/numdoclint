import os
import shutil

import pytest
import six
from voluptuous import Any, Schema

from numdoclint import jupyter_notebook
from numdoclint import py_module

TMP_TEST_MODULE_DIR = './tests/tmp/'
TMP_TEST_NOTEBOOK_PATH_1 = os.path.join(TMP_TEST_MODULE_DIR, 'tmp_1.ipynb')
TMP_TEST_NOTEBOOK_PATH_2 = os.path.join(TMP_TEST_MODULE_DIR, 'tmp_2.ipynb')

STR_SCHEMA = Any(*six.string_types)


def setup():
    """Function to be executed at the start of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)
    os.makedirs(TMP_TEST_MODULE_DIR)


def teardown():
    """Function to be executed at the end of the test.
    """
    shutil.rmtree(TMP_TEST_MODULE_DIR, ignore_errors=True)


def _delete_test_notebook():
    """Delete notebook for testing if exists.
    """
    if os.path.exists(TMP_TEST_NOTEBOOK_PATH_1):
        os.remove(TMP_TEST_NOTEBOOK_PATH_1)
    if os.path.exists(TMP_TEST_NOTEBOOK_PATH_2):
        os.remove(TMP_TEST_NOTEBOOK_PATH_2)


def test__check_notebook_exists():
    _delete_test_notebook()

    with pytest.raises(IOError):
        jupyter_notebook._check_notebook_exists(
            notebook_path=TMP_TEST_NOTEBOOK_PATH_1)

    with open(TMP_TEST_NOTEBOOK_PATH_1, 'w') as f:
        f.write('\n')

    jupyter_notebook._check_notebook_exists(
        notebook_path=TMP_TEST_NOTEBOOK_PATH_1)
    _delete_test_notebook()


def test__check_notebook_extension():
    with pytest.raises(IOError):
        jupyter_notebook._check_notebook_extension(
            notebook_path='sample/path.py')
    jupyter_notebook._check_notebook_extension(
        notebook_path='sample/path.ipynb')


def test__read_notebook_data_dict():
    notebook_data_dict = jupyter_notebook._read_notebook_data_dict(
        notebook_path='./tests/jupyter/test_jupyter_notebook_py3.ipynb')
    assert isinstance(notebook_data_dict, dict)
    has_key = 'cells' in notebook_data_dict
    assert has_key


def test__get_code_cell_str_list():
    code_str_list = jupyter_notebook._get_code_cell_str_list(
        notebook_data_dict={})
    assert code_str_list == []

    notebook_data_dict = {
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
    expected_code_str = 'import pandas as pd\nimport numpy as np'
    assert code_str_list[0] == expected_code_str
    expected_code_str = 'def sample_func():\n    pass'
    assert code_str_list[1] == expected_code_str


def test__rename_dict_key():
    info_list = [{
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
    schema = Schema(
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


def test__add_code_cell_index():
    info_list = [{}, {}]
    info_list = jupyter_notebook._add_code_cell_index(
        info_list=info_list,
        code_cell_idx=5)
    assert len(info_list) == 2
    schema = Schema(
        schema={
            jupyter_notebook.INFO_KEY_CODE_CELL_INDEX: 5,
        },
        required=True)
    for info_dict in info_list:
        schema(info_dict)


def test__check_unit_code_cell_str():
    expected_notebook_path = 'sample/path.ipynb'
    expected_code_cell_idx = 5
    code_cell_str = """
import pandas as pd
import numpy as np
    """
    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False)
    assert info_list == []

    schema = Schema(
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
        ignore_func_name_suffix_list=[],
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
        ignore_func_name_suffix_list=['sample_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False)
    assert info_list == []

    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_suffix_list=[],
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
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False)
    assert info_list == []
    info_list = jupyter_notebook._check_unit_code_cell_str(
        notebook_path=expected_notebook_path,
        code_cell_idx=expected_code_cell_idx,
        code_cell_str=code_cell_str,
        ignore_func_name_suffix_list=[],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=True)
    assert info_list


def test__print_info_list():
    printed_str = jupyter_notebook._print_info_list(
        info_list=[], verbose=jupyter_notebook.VERBOSE_ENABLED)
    assert printed_str == ''

    info_list = [{
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


def test_check_jupyter_notebook():
    pass
