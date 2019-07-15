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
