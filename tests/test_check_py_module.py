import pytest

from numdoclint import check_py_module


def test__check_module_exists():
    check_py_module._check_module_exists(
        py_module_path='./tests/test_check_py_module.py')
    with pytest.raises(FileNotFoundError):
        check_py_module._check_module_exists(
            py_module_path='test_not_exists_file.py')
