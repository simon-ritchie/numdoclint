import pytest
import six
from voluptuous import Any, Schema

from numdoclint import cli


def test__get_list_of_str_from_csv():
    result_list = cli._get_list_of_str_from_csv(csv='')
    assert result_list == []
    result_list = cli._get_list_of_str_from_csv(csv='apple,orange')
    assert result_list == ['apple', 'orange']
