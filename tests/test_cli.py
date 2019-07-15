import pytest
import six
from voluptuous import Any, Schema

from numdoclint import cli


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
