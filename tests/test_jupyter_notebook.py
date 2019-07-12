import os
import shutil

import pytest
import six
from voluptuous import Any, Schema

from numdoclint import jupyter_notebook

TMP_TEST_MODULE_DIR = './tests/tmp/'
TMP_TEST_NOTEBOOK_PATH_1 = os.path.join(TMP_TEST_MODULE_DIR, 'tmp_1.ipynb')
TMP_TEST_NOTEBOOK_PATH_2 = os.path.join(TMP_TEST_MODULE_DIR, 'tmp_2.ipynb')


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
