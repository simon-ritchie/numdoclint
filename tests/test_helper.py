import pytest
from voluptuous import Schema, All, Any

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


def test_get_splitted_param_doc_list():
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
    splitted_param_doc_list = helper.get_splitted_param_doc_list(
        docstring=docstring)
    assert len(splitted_param_doc_list) == 2
    expected_param_doc = """    name : str
        Sample name."""
    assert splitted_param_doc_list[0] == expected_param_doc

    expected_param_doc = """    location_id : int
        Sample id."""
    assert splitted_param_doc_list[1] == expected_param_doc


def test__get_docstring_var_name():
    var_doc = """    price : int
        Sample price.
    """
    var_name = helper._get_docstring_var_name(var_doc=var_doc)
    assert var_name == 'price'


def test__get_docstring_type_name():
    var_doc = """    price : int or None, default None, optional
        Sample price.
    """
    type_name = helper._get_docstring_type_name(var_doc=var_doc)
    assert type_name == 'int or None'

    var_doc = """    price, optional
        Sample price.
    """
    type_name = helper._get_docstring_type_name(var_doc=var_doc)
    assert type_name == ''


def test__get_docstring_default_value():
    var_doc = """    price : int
        Sample price.
    """
    default_val = helper._get_docstring_default_value(var_doc=var_doc)
    assert default_val == ''

    var_doc = """    price : int or None, default None, optional
        Sample price.
    """
    default_val = helper._get_docstring_default_value(var_doc=var_doc)
    assert default_val == 'None'


def test__get_docstring_var_description():
    var_doc = """    price : int
        Sample price.
        Sample price.
    """
    description = helper._get_docstring_var_description(
        var_doc=var_doc)
    expected_description = """        Sample price.
        Sample price."""
    assert description == expected_description

    var_doc = """   print : int
    """
    description = helper._get_docstring_var_description(
        var_doc=var_doc)


def test_get_docstring_param_info_list():
    param_info_list = helper.get_docstring_param_info_list(docstring='')
    assert param_info_list == []

    docstring = """
    Sample docstring.

    Returns
    -------
    price : int
        Sample price.
    """
    param_info_list = helper.get_docstring_param_info_list(
        docstring=docstring)
    assert param_info_list == []

    docstring = """
    Sample docstring.

    Parameters
    ----------
    name : str, default 'apple'
        Sample name.
    location_id : int or None
        Sample id.
        Sample id.

    Returns
    -------
    price : int
        Sample price.
    """
    param_info_list = helper.get_docstring_param_info_list(
        docstring=docstring)
    assert len(param_info_list) == 2
    schema_1 = Schema(
        schema={
            helper.DOC_PARAM_INFO_KEY_ARG_NAME: 'name',
            helper.DOC_PARAM_INFO_KEY_TYPE_NAME: 'str',
            helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL: "'apple'",
            helper.DOC_PARAM_INFO_KEY_DESCRIPTION: '        Sample name.',
        },
        required=True)
    schema_1(param_info_list[0])
    schema_2 = Schema(
        schema={
            helper.DOC_PARAM_INFO_KEY_ARG_NAME: 'location_id',
            helper.DOC_PARAM_INFO_KEY_TYPE_NAME: 'int or None',
            helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
            helper.DOC_PARAM_INFO_KEY_DESCRIPTION: \
                '        Sample id.\n        Sample id.',
        },
        required=True)
    schema_2(param_info_list[1])


def test_get_func_description_from_docstring():
    func_description = helper.get_func_description_from_docstring(
        docstring='')
    assert func_description == ''

    func_description = helper.get_func_description_from_docstring(
        docstring='------\nSample Docstring.')
    assert func_description == ''

    docstring = """
    Parameters
    ----------
    price : int
        Sample price.
    """
    func_description = helper.get_func_description_from_docstring(
        docstring=docstring)
    assert func_description == ''

    docstring = """Sample docstring.
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.

    Parameters
    ----------
    price : int
        Sample price.
    """
    func_description = helper.get_func_description_from_docstring(
        docstring=docstring)
    expected_description = """    Sample docstring.
    Lorem ipsum dolor sit amet, consectetur adipiscing elit."""
    assert func_description == expected_description
