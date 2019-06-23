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
    pass


def sample_func_3(orange):
    """sample_func_3.

    Returns
    -------
    price : int
        Sample price.
    """


    def sample_func_4(orange):
        """
        sample_func_4.

        Returns
        -------
        price : int
            Sample price.
        """
    '''
    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_0')
    assert docstring == ''

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert docstring == ''

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_2')
    expected_docstring = """    sample_func_2.

    Parameters
    ----------
    apple : Fruit
        Apple object."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str,
        func_name='sample_func_3')
    expected_docstring = """    sample_func_3.

    Returns
    -------
    price : int
        Sample price."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str,
        func_name='sample_func_4')
    expected_docstring = """    sample_func_4.

    Returns
    -------
    price : int
        Sample price."""
    assert docstring == expected_docstring


def test__set_docstring_indent_number_to_one():
    docstring = """
    Sample docstring.

    Parameters
    ----------
    name : str
        Sample name.
    """
    result_docstring = helper._set_docstring_indent_number_to_one(
        docstring=docstring, indent_num=1)
    assert docstring == result_docstring

    docstring = """
        Sample docstring.

        Parameters
        ----------
        name : str
            Sample name."""
    result_docstring = helper._set_docstring_indent_number_to_one(
        docstring=docstring, indent_num=2)
    expected_docstring = """
    Sample docstring.

    Parameters
    ----------
    name : str
        Sample name."""
    assert result_docstring == expected_docstring


def test_get_param_docstring():

    param_docstring = helper.get_param_docstring(docstring='')
    assert param_docstring == ''

    docstring = """
    Sample docstring.

    Parameters
    ----------
    name : str
        Sample name.
    location_id : int
        Sample location id.

    Returns
    -------
    price : int
        Sample price.
    """

    param_docstring = helper.get_param_docstring(docstring=docstring)
    expected_docstring = """    name : str
        Sample name.
    location_id : int
        Sample location id."""
    assert param_docstring == expected_docstring

    docstring = """
    Sample docstring.

    Returns
    -------
    price : int
        Sample price.
    """
    param_docstring = helper.get_param_docstring(docstring=docstring)
    assert param_docstring == ''


def test_get_splited_param_doc_list():
    docstring = """
    Sample function.

    Parameters
    ----------
    name : str
        Sample name.
    location_id : int
        Sample id.

    Returns
    -------
    price : int
        Sample price.
    """
    splited_param_doc_list = helper.get_splited_param_doc_list(
        docstring=docstring)
    assert len(splited_param_doc_list) == 2
    expected_param_doc = """    name : str
        Sample name."""
    assert splited_param_doc_list[0] == expected_param_doc

    expected_param_doc = """    location_id : int
        Sample id."""
    assert splited_param_doc_list[1] == expected_param_doc
