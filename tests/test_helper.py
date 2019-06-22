import pytest

from numdoclint import helper


def test_read_file_str():
    file_str = helper.read_file_str('./tests/test_helper.py')
    assert isinstance(file_str, str)
    assert file_str != ''
    assert 'def' in file_str


def test_get_func_name_list():
    py_module_str = helper.read_file_str(
        file_path='./tests/test_helper.py')
    func_name_list = helper.get_func_name_list(
        py_module_str=py_module_str)
    assert 'test_read_file_str' in func_name_list
    assert 'test_get_func_name_list' in func_name_list


def test_get_arg_name_list():
    py_module_str = """
def sample_func_1():
    pass


def sample_func_2(apple, orange):
    pass


def sample_func_3(apple: str, fruit_id: int):
    pass


def sample_func_4(
        apple, orange,
        melon):
    pass
    """

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert arg_name_list == []

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_2')
    assert arg_name_list == ['apple', 'orange']

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_3')
    assert arg_name_list == ['apple', 'fruit_id']

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_4')
    assert arg_name_list == ['apple', 'orange', 'melon']


def test_get_func_indent_num():
    py_module_str = """
def sample_func_1(apple):

    def sample_func_2(orange):
        pass

        def sample_func_3(orange):
            pass

    pass


class Apple:

    def sample_func_4(self):
        pass
    """

    with pytest.raises(ValueError):
        helper.get_func_indent_num(
            py_module_str=py_module_str,
            func_name='sample_func_0')

    indent_num = helper.get_func_indent_num(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert indent_num == 1

    indent_num = helper.get_func_indent_num(
        py_module_str=py_module_str, func_name='sample_func_2')
    assert indent_num == 2

    indent_num = helper.get_func_indent_num(
        py_module_str=py_module_str, func_name='sample_func_3')
    assert indent_num == 3

    indent_num = helper.get_func_indent_num(
        py_module_str=py_module_str, func_name='sample_func_4')
    assert indent_num == 2


def test_get_line_indent_num():
    line_indent_num = helper.get_line_indent_num(
        line_str='print("100")')
    assert line_indent_num == 0

    line_indent_num = helper.get_line_indent_num(
        line_str='    print("100")')
    assert line_indent_num == 1

    line_indent_num = helper.get_line_indent_num(
        line_str='        if print == 100:')
    assert line_indent_num == 2


def test_get_func_overall_docstring():
    py_module_str = '''
def sample_func_1(apple):
    print(1)


def sample_func_2(apple):
    """
    sample_func_2.

    Parameters
    ----------
    apple : Fruit
        Apple object.
    """
    '''
    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_2')
    pass
