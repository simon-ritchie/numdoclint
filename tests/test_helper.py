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


def test__get_args_str():
    py_module_str = """
    def sample_func_1():
        print(100)


    def sample_func_2(price, location_id):
        print(200)


    def sample_func_3(price, location_id=200):
        print(300)


    def sample_func_4(price=100: int, location_id=200: int) -> str:
        print(400)


    def sample_func_5(
            price, location_id,
            season):
        print(500)


    def sample_func_6( prince = 100, location_id = 200 ):
        print(600)
    """
    args_str = helper._get_args_str(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert args_str == ''

    args_str = helper._get_args_str(
        py_module_str=py_module_str, func_name='sample_func_2')
    assert args_str == 'price, location_id'

    args_str = helper._get_args_str(
        py_module_str=py_module_str, func_name='sample_func_3')
    assert args_str == 'price, location_id=200'

    args_str = helper._get_args_str(
        py_module_str=py_module_str, func_name='sample_func_4')
    assert args_str == 'price=100: int, location_id=200: int'

    args_str = helper._get_args_str(
        py_module_str=py_module_str, func_name='sample_func_5')
    assert args_str == 'price, location_id, season'

    args_str = helper._get_args_str(
        py_module_str=py_module_str, func_name='sample_func_6')
    assert args_str == 'prince = 100, location_id = 200'


def test_get_arg_default_val_info_dict():
    py_module_str = """
    def sample_func_1():
        print(100)


    def sample_func_2(price, location_id=100, season=3):
        print(200)


    def sample_func_3(
            price: int, location_id=100: int) -> str:
        print(300)
    """
    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert default_val_info_dict == {}

    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=py_module_str, func_name='sample_func_2')
    expected_dict = {
        'price': '',
        'location_id': '100',
        'season': '3',
    }
    assert default_val_info_dict == expected_dict

    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=py_module_str, func_name='sample_func_3')
    expected_dict = {
        'price': '',
        'location_id': '100',
    }
    assert default_val_info_dict == expected_dict


def test__get_return_value_docstring():
    docstring = """
    Sample docstring.

    Parameters
    ----------
    price : int
        Sample price.

    Returns
    -------
    name : str
        Sample name.
    location_id : int
        Sample location id.

    Notes
    -----
    - Sample notes 1.
    - Sample notes 2.
    """
    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring)
    expected_return_value_docstring = """    name : str
        Sample name.
    location_id : int
        Sample location id."""
    assert return_value_docstring, expected_return_value_docstring


def test_append_return_value_info_unit_dict():
    expected_name = 'sample_name'
    expected_type_name = 'str'
    expected_description = '        Sample description.'
    return_val_info_list = helper._append_return_value_info_unit_dict(
        name=expected_name,
        type_name=expected_type_name,
        description=expected_description,
        return_val_info_list=[])
    assert len(return_val_info_list) == 1
    schema = Schema(
        schema={
            helper.DOC_RETURN_INFO_KEY_NAME: expected_name,
            helper.DOC_RETURN_INFO_KEY_TYPE_NAME: expected_type_name,
            helper.DOC_RETURN_INFO_KEY_DESCRIPTION: expected_description,
        },
        required=True)
    schema(return_val_info_list[0])


def test__get_return_value_name_from_line():
    line_str = '        price : int'
    return_value_name = helper._get_return_value_name_from_line(
        line_str=line_str)
    assert return_value_name == 'price'


def test__get_return_value_type_name_from_line():
    line_str = '        price : int'
    return_value_type_name = helper._get_return_value_type_name_from_line(
        line_str=line_str)
    assert return_value_type_name == 'int'


def test_get_docstring_return_val_info_list():
    docstring = """
    Sample docstring.

    Paramters
    ---------
    price : int
        Sample price.
    """
    return_val_info_list = helper.get_docstring_return_val_info_list(
        docstring=docstring)
    assert return_val_info_list == []

    docstring = """
    Sample docstring.

    Paramters
    ---------
    price : int
        Sample price.

    Returns
    -------
    name : str
        Sample name.
        Sample text.
    location_id : int or None
        Sample location id.
    """
    return_val_info_list = helper.get_docstring_return_val_info_list(
        docstring=docstring)
    assert len(return_val_info_list) == 2
    expected_description = """        Sample name.
        Sample text."""
    schema_1 = Schema(
        schema={
            helper.DOC_RETURN_INFO_KEY_NAME: 'name',
            helper.DOC_RETURN_INFO_KEY_TYPE_NAME: 'str',
            helper.DOC_RETURN_INFO_KEY_DESCRIPTION: expected_description,
        },
        required=True)
    schema_1(return_val_info_list[0])
    schema_2 = Schema(
        schema={
            helper.DOC_RETURN_INFO_KEY_NAME: 'location_id',
            helper.DOC_RETURN_INFO_KEY_TYPE_NAME: 'int or None',
            helper.DOC_RETURN_INFO_KEY_DESCRIPTION: \
                '        Sample location id.',
        }, required=True)
    schema_2(return_val_info_list[1])


def test_get_func_str():
    func_str = helper.get_func_str(
        module_str='', func_name='sample_func')
    assert func_str == ''

    module_str = '''
sample_int = 100


def sample_func_1(price):
    """
    Sample func.

    Parameters
    ----------
    price : int
        Sample price.

    Returns
    -------
    c : int
        Sample value.
    """
    a = 1
    b = 2
    c = a + b
    return c


class SampleClass:

    def __init__(self):
        pass

    def sample_func_2(location_id):
        a = 1
        b = 2
        c = a * b
        return c


sample_str = 'apple'
    '''
    func_str = helper.get_func_str(
        module_str=module_str,
        func_name='sample_func_1')
    expected_func_str = '''def sample_func_1(price):
    """
    Sample func.

    Parameters
    ----------
    price : int
        Sample price.

    Returns
    -------
    c : int
        Sample value.
    """
    a = 1
    b = 2
    c = a + b
    return c'''
    assert func_str == expected_func_str

    func_str = helper.get_func_str(
        module_str=module_str,
        func_name='sample_func_2')
    expected_func_str = """    def sample_func_2(location_id):
        a = 1
        b = 2
        c = a * b
        return c"""
    assert func_str == expected_func_str
