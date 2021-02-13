import re
from typing import Dict, List, Optional

import pytest
import six
from voluptuous import Schema

from numdoclint import helper


def test_read_file_str() -> None:
    file_str: str = helper.read_file_str('./tests/test_helper.py')
    assert isinstance(file_str, six.string_types)
    assert file_str != ''
    assert 'def' in file_str


def test_get_func_name_list() -> None:
    code_str: str = """
def sample_func_1():
    pass


def sample_func_2(
        name='apple', price=100):

    def sample_func_3(
            location_id=30):
        pass

    pass


def sample_func
(
    price, name
):
    '''
    Sample function.

    Examples
    --------
    >>> def sample_func_4():
    ...     pass
    '''
    pass


sample_str = r'def .*?\\(.*?\\)'
    """
    func_name_list: List[str] = helper.get_func_name_list(
        code_str=code_str)
    assert len(func_name_list) == 4
    assert 'sample_func_1' in func_name_list
    assert 'sample_func_2' in func_name_list
    assert 'sample_func_3' in func_name_list
    assert 'sample_func' in func_name_list


def test_get_arg_name_list() -> None:
    py_module_str: str = """
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


def sample_func_5(price=100, name='apple'):
    pass


class SampleClass:

    def sample_func_6(self, cls, price, name, *args, **kwargs):
        pass

def sample_func_7(price: int = 100, name: str = 'apple'):
    pass


def sample_func_8(dict_val: Optional[Dict[str, int]] = None):
    pass
    """

    arg_name_list: List[str] = helper.get_arg_name_list(
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

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_5')
    assert arg_name_list == ['price', 'name']

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_6')
    assert arg_name_list == ['price', 'name']

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_6',
        exclude_ignoring_args=False)
    assert arg_name_list == [
        'self', 'cls', 'price', 'name', '*args', '**kwargs']

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_7')
    assert arg_name_list == ['price', 'name']

    arg_name_list = helper.get_arg_name_list(
        py_module_str=py_module_str, func_name='sample_func_8')
    assert arg_name_list == ['dict_val']


def test_get_func_indent_num() -> None:
    py_module_str: str = """
def sample_func_1(apple):

    def sample_func_2(orange):
        pass

        def sample_func_3(orange):
            pass

    def sample_func(price):
        pass

    pass


class Apple:

    def sample_func_4(self):
        pass
    """

    with pytest.raises(ValueError):  # type: ignore
        helper.get_func_indent_num(
            py_module_str=py_module_str,
            func_name='sample_func_0')

    indent_num: int = helper.get_func_indent_num(
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

    indent_num = helper.get_func_indent_num(
        py_module_str=py_module_str, func_name='sample_func')
    assert indent_num == 2


def test_get_line_indent_num() -> None:
    line_indent_num: int = helper.get_line_indent_num(
        line_str='print("100")')
    assert line_indent_num == 0

    line_indent_num = helper.get_line_indent_num(
        line_str='    print("100")')
    assert line_indent_num == 1

    line_indent_num = helper.get_line_indent_num(
        line_str='        if print == 100:')
    assert line_indent_num == 2


def test_get_func_overall_docstring() -> None:
    py_module_str: str = '''
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
    pass

    def sample_func_4(orange):
        """
        sample_func_4.

        Returns
        -------
        price : int
            Sample price.
        """
        pass


def sample_func_5(price):
    sample_str = """Sample str.
    """
    pass


def sample_func_6(price):
    """
    Sample docstring.

    Parameters
    ----------
    price : int
        Sample price.
    """
    \'\'\'
    sample_str = \'\'\'apple
    orange


def sample_func_7():
    r"""
    Sample docstring.
    """
    pass


def sample_func_8():
    r\'\'\'
    Sample docstring.
    \'\'\'


def sample():
    """
    Sample docstring (foward match).
    """
    pass


class SampleClass1:

    def sample_func_9(
        price=100,
        name='apple'
    ):
        """
        Sample docstring.
        Parameters
        ----------
        price : int, default 100
            Sample price.
        name : str, default 'apple'
            Sample name.
        """
        pass


def sample_func_10(price):
    """Sample function.

Sample docstring."""
    pass


def sample_func_11(price):
    # type: (int) -> None
    """
    Sample function with type annotation comment.
    """
    '''
    docstring: str = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_0')
    assert docstring == ''

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert docstring == ''

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_2')
    expected_docstring: str = """    sample_func_2.

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

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str,
        func_name='sample_func_4',
        set_indent_to_1=False)
    expected_docstring = """        sample_func_4.

        Returns
        -------
        price : int
            Sample price."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_5')
    assert docstring == ''

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_6')
    expected_docstring = """    Sample docstring.

    Parameters
    ----------
    price : int
        Sample price."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_7')
    expected_docstring = """    Sample docstring."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_8')
    expected_docstring = """    Sample docstring."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_9')
    expected_docstring = """    Sample docstring.
    Parameters
    ----------
    price : int, default 100
        Sample price.
    name : str, default 'apple'
        Sample name."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample')
    expected_docstring = """    Sample docstring (foward match)."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str, func_name='sample_func_10')
    expected_docstring = """    Sample function.

Sample docstring."""
    assert docstring == expected_docstring

    docstring = helper.get_func_overall_docstring(
        py_module_str=py_module_str,
        func_name='sample_func_11')
    expected_docstring = \
        """    Sample function with type annotation comment"""
    assert docstring, expected_docstring


def test__set_docstring_indent_number_to_one() -> None:
    docstring: str = """
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


def test_get_param_docstring() -> None:

    param_docstring: str = helper.get_param_docstring(docstring='')
    assert param_docstring == ''

    docstring: str = """
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
    expected_docstring: str = """    name : str
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

    docstring = """
    Parameters
    ----------
    price : int
        Sample price."""
    param_docstring = helper.get_param_docstring(docstring=docstring)
    expected_docstring = """    price : int
        Sample price."""
    assert param_docstring == expected_docstring


def test_get_splitted_param_doc_list() -> None:
    docstring: str = """
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
    splitted_param_doc_list: List[str] = helper.get_splitted_param_doc_list(
        docstring=docstring)
    assert len(splitted_param_doc_list) == 2
    expected_param_doc: str = """    name : str
        Sample name."""
    assert splitted_param_doc_list[0] == expected_param_doc

    expected_param_doc = """    location_id : int
        Sample id."""
    assert splitted_param_doc_list[1] == expected_param_doc

    docstring = """
    Sample function.

    Parameters
    ----------
    name : str
        Sample name.
    """
    splitted_param_doc_list = helper.get_splitted_param_doc_list(
        docstring=docstring)
    assert len(splitted_param_doc_list) == 1
    expected_param_doc = """    name : str
        Sample name."""
    assert splitted_param_doc_list[0] == expected_param_doc


def test__get_docstring_var_name() -> None:
    var_doc: str = """    price : int
        Sample price.
    """
    var_name: str = helper._get_docstring_var_name(var_doc=var_doc)
    assert var_name == 'price'

    var_doc = """    price
        Sample price.
    """
    var_name = helper._get_docstring_var_name(var_doc=var_doc)
    assert var_name == 'price'


def test__get_docstring_type_name() -> None:
    var_doc: str = """    price : int or None, default None, optional
        Sample price.
    """
    type_name: str = helper._get_docstring_type_name(var_doc=var_doc)
    assert type_name == 'int or None'

    var_doc = """    price, optional
        Sample price.
    """
    type_name = helper._get_docstring_type_name(var_doc=var_doc)
    assert type_name == ''


def test__get_docstring_default_value() -> None:
    var_doc: str = """    price : int
        Sample price.
    """
    default_val: str = helper._get_docstring_default_value(var_doc=var_doc)
    assert default_val == ''

    var_doc = """    price : int or None, default None, optional
        Sample price.
    """
    default_val = helper._get_docstring_default_value(var_doc=var_doc)
    assert default_val == 'None'

    var_doc = """    price : int (default 0), optional
        Sample price.
    """
    default_val = helper._get_docstring_default_value(var_doc=var_doc)
    assert default_val == '0'


def test__get_docstring_var_description() -> None:
    var_doc: str = """    price : int
        Sample price.
        Sample price.
    """
    description: str = helper._get_docstring_var_description(
        var_doc=var_doc)
    expected_description: str = """        Sample price.
        Sample price."""
    assert description == expected_description

    var_doc = """   print : int
    """
    description = helper._get_docstring_var_description(
        var_doc=var_doc)


def test_get_docstring_param_info_list() -> None:
    param_info_list: List[Dict[str, str]] = \
        helper.get_docstring_param_info_list(docstring='')
    assert param_info_list == []

    docstring: str = """
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
    schema_1: Schema = Schema(
        schema={
            helper.DOC_PARAM_INFO_KEY_ARG_NAME: 'name',
            helper.DOC_PARAM_INFO_KEY_TYPE_NAME: 'str',
            helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL: "'apple'",
            helper.DOC_PARAM_INFO_KEY_DESCRIPTION: '        Sample name.',
        },
        required=True)
    schema_1(param_info_list[0])
    schema_2: Schema = Schema(
        schema={
            helper.DOC_PARAM_INFO_KEY_ARG_NAME: 'location_id',
            helper.DOC_PARAM_INFO_KEY_TYPE_NAME: 'int or None',
            helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
            helper.DOC_PARAM_INFO_KEY_DESCRIPTION:
            '        Sample id.\n        Sample id.',
        },
        required=True)
    schema_2(param_info_list[1])

    docstring = """
    Sample docstring.

    Parameters
    ----------
    one, two : int
        Sample two argument.
    """
    param_info_list = helper.get_docstring_param_info_list(
        docstring=docstring)
    assert len(param_info_list) == 2
    expected_arg_name_list: List[str] = ['one', 'two']
    for i, expected_arg_name in enumerate(expected_arg_name_list):
        schema: Schema = Schema(
            schema={
                helper.DOC_PARAM_INFO_KEY_ARG_NAME: expected_arg_name,
                helper.DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
                helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
                helper.DOC_PARAM_INFO_KEY_DESCRIPTION:
                '        Sample two argument.',
            }, required=True)
        schema(param_info_list[i])


def test_get_func_description_from_docstring() -> None:
    func_description: str = helper.get_func_description_from_docstring(
        docstring='')
    assert func_description == ''

    func_description = helper.get_func_description_from_docstring(
        docstring='------\nSample Docstring.')
    assert func_description == ''

    docstring: str = """
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


def test__get_args_str() -> None:
    code_str: str = """
    def sample_func_1():
        print(100)


    def sample_func_2(price, location_id):
        print(200)


    def sample_func_3(price, location_id=200):
        print(300)


    def sample_func_4(price: int=100, location_id: int=200) -> str:
        print(400)


    def sample_func_5(
            price, location_id,
            season):
        print(500)


    def sample_func_6( prince = 100, location_id = 200 ):
        print(600)


    def sample_func_7
    (
        price,
        name
    ):
        pass


    def sample_func_8(dict_val: Optional[Dict[str, int]] = None):
        pass
    """
    args_str: str = helper._get_args_str(
        code_str=code_str, func_name='sample_func_1')
    assert args_str == ''

    args_str = helper._get_args_str(
        code_str=code_str, func_name='sample_func_2')
    assert args_str == 'price, location_id'

    args_str = helper._get_args_str(
        code_str=code_str, func_name='sample_func_3')
    assert args_str == 'price, location_id=200'

    args_str = helper._get_args_str(
        code_str=code_str, func_name='sample_func_4')
    assert args_str == 'price: int=100, location_id: int=200'

    args_str = helper._get_args_str(
        code_str=code_str, func_name='sample_func_5')
    assert args_str == 'price, location_id, season'

    args_str = helper._get_args_str(
        code_str=code_str, func_name='sample_func_6')
    assert args_str == 'prince = 100, location_id = 200'

    args_str = helper._get_args_str(
        code_str=code_str, func_name='sample_func_7')
    assert args_str == 'price, name'


def test_get_arg_default_val_info_dict() -> None:
    py_module_str: str = """
    def sample_func_1():
        print(100)


    def sample_func_2(price, location_id=100, season=3):
        print(200)


    def sample_func_3(
            price: int, location_id: int=100) -> str:
        print(300)


    def sample_func_4(
            price: int = 100, name: str = 'apple') -> str:
        print(300)


    def sample_func_5(name: str = "apple") -> str:
        print(300)


    def sample_func_6(dict_value: Optional[Dict[str, int]] = None) -> str:
        print(300)
    """
    default_val_info_dict: Dict[str, str] = \
        helper.get_arg_default_val_info_dict(
            py_module_str=py_module_str, func_name='sample_func_1')
    assert default_val_info_dict == {}

    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=py_module_str, func_name='sample_func_2')
    expected_dict: Dict[str, str] = {
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

    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=py_module_str, func_name='sample_func_4')
    expected_dict = {
        'price': '100',
        'name': "'apple'",
    }
    assert default_val_info_dict == expected_dict

    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=py_module_str, func_name='sample_func_5')
    expected_dict = {
        'name': '"apple"',
    }
    assert default_val_info_dict == expected_dict

    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=py_module_str, func_name='sample_func_6')
    expected_dict = {
        'dict_value': 'None',
    }
    assert default_val_info_dict == expected_dict


def test__get_return_value_docstring() -> None:
    docstring: str = """
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
    return_value_docstring: str = helper._get_return_value_docstring(
        docstring=docstring)
    expected_return_value_docstring: str = """    name : str
        Sample name.
    location_id : int
        Sample location id."""
    assert return_value_docstring, expected_return_value_docstring

    docstring = """
    Sample docstring.

    Returns
    -------
    price : int
    """
    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring)
    expected_return_value_docstring = """    price : int"""
    assert return_value_docstring == expected_return_value_docstring

    docstring = """
    Sample docstring.

    Returns
    -------
    x : int
        Sample value.
    y : int
    """
    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring)
    expected_return_value_docstring = """    x : int
        Sample value.
    y : int"""
    assert return_value_docstring == expected_return_value_docstring

    docstring = """
    Sample docstring.

    Returns
    -------
    x : int
        Sample value.
    y : int
        Sample value.
    """
    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring)
    expected_return_value_docstring = """    x : int
        Sample value.
    y : int
        Sample value."""
    assert return_value_docstring == expected_return_value_docstring

    docstring = """
    Returns sample values.

    Parameters
    ----------
    price : int
        Sample price.

    Returns
    -------
    x : int
        Sample value.
    y : int
        Sample value.
    """
    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring)
    expected_return_value_docstring = """    x : int
        Sample value.
    y : int
        Sample value."""
    assert return_value_docstring == expected_return_value_docstring

    docstring = """
    Sample docstring.

    Returns
    -------
    x : int
        Sample value.

    .. deprecated:: 0.0.1
    """
    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring, drop_additional_info=False)
    expected_return_value_docstring = """    x : int
        Sample value.

    .. deprecated:: 0.0.1"""
    assert return_value_docstring == expected_return_value_docstring

    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring, drop_additional_info=True)
    expected_return_value_docstring = """    x : int
        Sample value."""
    assert return_value_docstring == expected_return_value_docstring

    docstring = """
    Sample docstring.

    Parameters
    ----------
    x : int
        Sample value.

        .. deprecated:: 0.0.1

    Returns
    -------
    price : int
        Sample price.
    """
    return_value_docstring = helper._get_return_value_docstring(
        docstring=docstring, drop_additional_info=True)
    expected_return_value_docstring = """    price : int
        Sample price."""
    assert return_value_docstring == expected_return_value_docstring


def test_append_return_value_info_unit_dict() -> None:
    expected_name: str = 'sample_name'
    expected_type_name: str = 'str'
    expected_description: str = '        Sample description.'
    return_val_info_list = helper._append_return_value_info_unit_dict(
        name=expected_name,
        type_name=expected_type_name,
        description=expected_description,
        return_val_info_list=[])
    assert len(return_val_info_list) == 1
    schema: Schema = Schema(
        schema={
            helper.DOC_RETURN_INFO_KEY_NAME: expected_name,
            helper.DOC_RETURN_INFO_KEY_TYPE_NAME: expected_type_name,
            helper.DOC_RETURN_INFO_KEY_DESCRIPTION: expected_description,
        },
        required=True)
    schema(return_val_info_list[0])


def test__get_return_value_name_from_line() -> None:
    line_str: str = '        price : int'
    return_value_name: str = helper._get_return_value_name_from_line(
        line_str=line_str)
    assert return_value_name == 'price'

    line_str = '    DataFrame'
    return_value_name = helper._get_return_value_name_from_line(
        line_str=line_str)
    assert return_value_name == ''


def test__get_return_value_type_name_from_line() -> None:
    line_str: str = '        price : int'
    return_value_type_name: str = \
        helper._get_return_value_type_name_from_line(
            line_str=line_str)
    assert return_value_type_name == 'int'

    line_str = '    DataFrame'
    return_value_type_name = helper._get_return_value_type_name_from_line(
        line_str=line_str)
    assert return_value_type_name == 'DataFrame'


def test_get_docstring_return_val_info_list() -> None:
    docstring: str = """
    Sample docstring.

    Paramters
    ---------
    price : int
        Sample price.
    """
    return_val_info_list: List[Dict[str, str]] = \
        helper.get_docstring_return_val_info_list(
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
    expected_description: str = """        Sample name.
        Sample text."""
    schema_1: Schema = Schema(
        schema={
            helper.DOC_RETURN_INFO_KEY_NAME: 'name',
            helper.DOC_RETURN_INFO_KEY_TYPE_NAME: 'str',
            helper.DOC_RETURN_INFO_KEY_DESCRIPTION: expected_description,
        },
        required=True)
    schema_1(return_val_info_list[0])
    schema_2: Schema = Schema(
        schema={
            helper.DOC_RETURN_INFO_KEY_NAME: 'location_id',
            helper.DOC_RETURN_INFO_KEY_TYPE_NAME: 'int or None',
            helper.DOC_RETURN_INFO_KEY_DESCRIPTION:
            '        Sample location id.',
        }, required=True)
    schema_2(return_val_info_list[1])

    docstring = """
    Sample docstring.

    Returns
    -------
    name : str
        Sample name.

    .. versionadded::0.0.1
    """
    return_val_info_list = helper.get_docstring_return_val_info_list(
        docstring=docstring)
    assert len(return_val_info_list) == 1
    return_val_name: str = return_val_info_list[
        0][helper.DOC_RETURN_INFO_KEY_NAME]
    assert return_val_name == 'name'


def test_get_func_str() -> None:
    func_str: str = helper.get_func_str(
        module_str='', func_name='sample_func')
    assert func_str == ''

    module_str: str = '''
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


    def sample_func_3(
            price,
            name
    ):
        a = 1
        return a


sample_str = 'apple'
    '''
    func_str = helper.get_func_str(
        module_str=module_str,
        func_name='sample_func_1')
    expected_func_str: str = '''def sample_func_1(price):
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

    func_str = helper.get_func_str(
        module_str=module_str, func_name='sample_func_3')
    expected_func_str = """    def sample_func_3(
            price,
            name
    ):
        a = 1
        return a"""
    assert func_str == expected_func_str


def test_return_val_exists_in_func() -> None:
    module_str: str = '''
sample_int = 100


def sample_func_1(price):
    """
    Sample func.

    Parameters
    ----------
    price : int
        Sample price.
    """
    a = 1
    b = 2
    c = a + b
    return c


def sample_func_2():
    a = 1
    b = 2
    print(a + b)


def sample_func_3():
    for i in range(10):
        if i == 3:
            return


def sample_func_5():
    """
    Sample function that return sample func.
    """
    pass


class SampleClass:

    def sample_func_6():
        """
        Sample function that return sample func.
        """
        pass


def sample_func_7():

    def sample_func_8():
        return 100

    pass

def sample_func_9():
    popen = sp.Popen(
        command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    stdout_bytes: bytes = popen.communicate()[0]
    if popen.returncode == 0:
        return
    '''
    result_bool: bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_1')
    assert result_bool

    result_bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_2')
    assert not result_bool

    result_bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_3')
    assert not result_bool

    result_bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_4')
    assert not result_bool

    result_bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_5')
    assert not result_bool

    result_bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_6')
    assert not result_bool

    result_bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_7')
    assert not result_bool

    result_bool = helper.return_val_exists_in_func(
        module_str=module_str, func_name='sample_func_9')
    assert not result_bool


def test__parameters_exists_in_docstring() -> None:
    docstring: str = """
    Sample docstring.

    Parameters
    ----------
    price : int
        Sample price.

    Returns
    -------
    name : str
        Sample name.
    """
    result_bool: bool = helper._parameters_exists_in_docstring(
        docstring=docstring)
    assert result_bool

    docstring = """
    Sample docstring.

    Returns
    -------
    name : str
        Sample name.
    """
    result_bool = helper._parameters_exists_in_docstring(
        docstring=docstring)
    assert not result_bool


def test_get_optional_arg_name_list() -> None:
    optional_arg_name_list: List[str] = helper.get_optional_arg_name_list(
        docstring='')
    assert optional_arg_name_list == []

    docstring: str = """
    Sample docstring.

    Returns
    -------
    price : int
        Sample price.
    """
    optional_arg_name_list = helper.get_optional_arg_name_list(
        docstring=docstring)
    assert optional_arg_name_list == []

    docstring = """
    Sample docstring.

    Parameters
    ----------
    price : int, optional
        Sample price.
    name : str
        Sample name.
    location_id : int, optional
        Sample location id.
    """
    optional_arg_name_list = helper.get_optional_arg_name_list(
        docstring=docstring)
    assert len(optional_arg_name_list) == 2
    assert 'price' in optional_arg_name_list
    assert 'location_id' in optional_arg_name_list


def test__remove_docstring_from_func_str() -> None:
    module_str: str = '''
def sample_func_1(price):
    """
    Sample func.

    Parameters
    ----------
    price : int
        Sample price
    """
    pass


def sample_func_2(price):
    \'\'\'
    Sample func.

    Parameters
    ----------
    price : int
        Sample price
    \'\'\'
    pass


class SampleClass:

    def sample_func_3(name):
        """
        Sample func.

        Parameters
        ----------
        name : str
            Sample name.
        """
        pass

    def sample_func_4(name):
        \'\'\'
        Sample func.

        Parameters
        ----------
        name : str
            Sample name.
        \'\'\'
        pass

def sample_func_5(price):
    """Sample func.

    Parameters
    ----------
    price : int
        Sample price
    """
    pass
    '''

    func_str: str = helper.get_func_str(
        module_str=module_str, func_name='sample_func_1')
    func_str = helper._remove_docstring_from_func_str(
        func_str=func_str,
        module_str=module_str,
        func_name='sample_func_1')
    expected_func_str: str = """def sample_func_1(price):
    pass"""
    assert func_str == expected_func_str

    func_str = helper.get_func_str(
        module_str=module_str, func_name='sample_func_2')
    func_str = helper._remove_docstring_from_func_str(
        func_str=func_str,
        module_str=module_str,
        func_name='sample_func_2')
    expected_func_str = """def sample_func_2(price):
    pass"""
    assert func_str == expected_func_str

    func_str = helper.get_func_str(
        module_str=module_str, func_name='sample_func_3')
    func_str = helper._remove_docstring_from_func_str(
        func_str=func_str,
        module_str=module_str,
        func_name='sample_func_3')
    expected_func_str = """    def sample_func_3(name):
        pass"""
    assert func_str == expected_func_str

    func_str = helper.get_func_str(
        module_str=module_str, func_name='sample_func_4')
    func_str = helper._remove_docstring_from_func_str(
        func_str=func_str,
        module_str=module_str,
        func_name='sample_func_4')
    expected_func_str = """    def sample_func_4(name):
        pass"""
    assert func_str == expected_func_str

    func_str = helper.get_func_str(
        module_str=module_str, func_name='sample_func_5')
    func_str = helper._remove_docstring_from_func_str(
        func_str=func_str,
        module_str=module_str,
        func_name='sample_func_5')
    expected_func_str = """def sample_func_5(price):
    pass"""
    assert func_str == expected_func_str


def test_kwargs_exists() -> None:
    py_module_str: str = """
def sample_func_1(price, **kwargs):
    pass


def sample_func_2(price):
    pass
    """

    result_bool: bool = helper.kwargs_exists(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert result_bool

    result_bool = helper.kwargs_exists(
        py_module_str=py_module_str, func_name='sample_func_2')
    assert not result_bool


def test_args_or_kwargs_str_in_param_name() -> None:
    result_bool: bool = helper.args_or_kwargs_str_in_param_name(
        param_arg_name='price')
    assert not result_bool

    result_bool = helper.args_or_kwargs_str_in_param_name(
        param_arg_name='*args')
    assert result_bool

    result_bool = helper.args_or_kwargs_str_in_param_name(
        param_arg_name='**kwargs')
    assert result_bool

    result_bool = helper.args_or_kwargs_str_in_param_name(
        param_arg_name='**kwargs, a')
    assert result_bool


def test__append_param_info_to_list() -> None:
    param_info_list: List[Dict[str, str]] = helper._append_param_info_to_list(
        param_info_list=[],
        arg_name='price',
        type_name='int',
        default_val='',
        description='Sample price.')
    assert len(param_info_list) == 1
    schema: Schema = Schema(
        schema={
            helper.DOC_PARAM_INFO_KEY_ARG_NAME: 'price',
            helper.DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
            helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
            helper.DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample price.'
        },
        required=True)
    schema(param_info_list[0])

    param_info_list = helper._append_param_info_to_list(
        param_info_list=[],
        arg_name='one, two',
        type_name='int',
        default_val='',
        description='Sample arguments.')
    assert len(param_info_list) == 2
    expected_arg_name_list: List[str] = ['one', 'two']
    for i, expected_arg_name in enumerate(expected_arg_name_list):
        schema = Schema(
            schema={
                helper.DOC_PARAM_INFO_KEY_ARG_NAME: expected_arg_name,
                helper.DOC_PARAM_INFO_KEY_TYPE_NAME: 'int',
                helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL: '',
                helper.DOC_PARAM_INFO_KEY_DESCRIPTION: 'Sample arguments.'
            },
            required=True)
        schema(param_info_list[i])


def test__hyphens_exists_next_line() -> None:
    line_splitted_list: List[str] = [
        'Sample docstring',
        '',
        'Parameters',
        '----------',
    ]

    result_bool: bool = helper._hyphens_exists_next_line(
        line_splitted_list=line_splitted_list,
        next_line_idx=4)
    assert not result_bool

    result_bool = helper._hyphens_exists_next_line(
        line_splitted_list=line_splitted_list,
        next_line_idx=1)
    assert not result_bool

    result_bool = helper._hyphens_exists_next_line(
        line_splitted_list=line_splitted_list,
        next_line_idx=3)
    assert result_bool


def test__get_func_start_line_index() -> None:
    line_splitted_list: List[str] = [
        'price = 100',
        'def sample_func_1():',
        '    return 100',
        '',
        'def sample_func_2():',
        '    return 200',
        '',
        'def sample_func():',
        '    pass'
    ]

    func_start_line_index: int = helper._get_func_start_line_index(
        line_splitted_list=line_splitted_list,
        func_name='sample_func_1')
    assert func_start_line_index == 1

    func_start_line_index = helper._get_func_start_line_index(
        line_splitted_list=line_splitted_list,
        func_name='sample_func_2')
    assert func_start_line_index == 4

    func_start_line_index = helper._get_func_start_line_index(
        line_splitted_list=line_splitted_list,
        func_name='sample_func')
    assert func_start_line_index == 7

    func_start_line_index = helper._get_func_start_line_index(
        line_splitted_list=line_splitted_list,
        func_name='sample_func_3')
    assert func_start_line_index == -1


def test_get_decorator_names() -> None:
    py_module_str: str = """
price = 100


def sample_func_1(price=100):
    return 100


@Substitution('')
@Appender
def sample_func_2(price=100):
    return 200


@Appender(
    sample_value_1=100,
    sample_value_2=200,
    sample_value_3=(
        100, 200,
    ),
)
@Substitution('')
def sample_func_3(price):
    pass
    """

    decorator_names: List[str] = helper.get_decorator_names(
        py_module_str=py_module_str, func_name='sample_func_1')
    assert decorator_names == []

    decorator_names = helper.get_decorator_names(
        py_module_str=py_module_str, func_name='sample_func_2')
    assert len(decorator_names) == 2
    assert "@Substitution('')" in decorator_names
    assert '@Appender' in decorator_names

    decorator_names = helper.get_decorator_names(
        py_module_str=py_module_str, func_name='sample_func_3')
    assert len(decorator_names) == 2
    assert '@Appender(' in decorator_names
    assert "@Substitution('')" in decorator_names


def test__get_func_match() -> None:
    py_module_str: str = """
price = 100


def sample_func_1():
    pass


def sample_func_2
(
    price,
    name
):
    pass


def sample_func
(
    price
):
    pass
    """

    match: Optional[re.Match] = helper._get_func_match(
        py_module_str=py_module_str, func_name='sample_func_1')
    start_idx: int = match.start()
    expected_func_str: str = 'def sample_func_1():'
    assert py_module_str[start_idx:start_idx + 20] == expected_func_str

    match = helper._get_func_match(
        py_module_str=py_module_str, func_name='sample_func_2')
    start_idx = match.start()
    expected_func_str = 'def sample_func_2\n('
    assert py_module_str[start_idx:start_idx + 19] == expected_func_str

    match = helper._get_func_match(
        py_module_str=py_module_str, func_name='sample_func')
    start_idx = match.start()
    expected_func_str = 'def sample_func\n('
    assert py_module_str[start_idx:start_idx + 17] == expected_func_str


def test__is_additional_info_str() -> None:
    result_bool = helper._is_additional_info_str(
        target_str='    .. versionadded::0.0.1')
    assert result_bool

    result_bool = helper._is_additional_info_str(target_str='price')
    assert not result_bool


def test_is_interactive_shell_example_line() -> None:
    py_module_str: str = '''
    def sample_func_1():
        """
        Sample function.

        Examples
        --------
        >>> def sample_func_2():
        ...     pass
        >>> sample_value = 100
        ... def sample_func_3():
        ...     pass
        """
        pass
    '''

    result_bool: bool = helper.is_interactive_shell_example_line(
        func_start_index=5, py_module_str=py_module_str)
    assert not result_bool

    result_bool = helper.is_interactive_shell_example_line(
        func_start_index=110, py_module_str=py_module_str)

    result_bool = helper.is_interactive_shell_example_line(
        func_start_index=195, py_module_str=py_module_str)
    assert result_bool


def test__remove_type_str_from_arg_str() -> None:
    after_arg_str: str = helper._remove_type_str_from_arg_str(
        arg_str='price')
    assert after_arg_str == 'price'

    after_arg_str = helper._remove_type_str_from_arg_str(
        arg_str='price: int')
    assert after_arg_str == 'price'

    after_arg_str = helper._remove_type_str_from_arg_str(
        arg_str=' price: int=100 ')
    assert after_arg_str == 'price=100'

    after_arg_str = helper._remove_type_str_from_arg_str(
        arg_str=' price: int = 100 ')
    assert after_arg_str == 'price=100'


def test__remove_nested_func_str() -> None:
    func_str: str = """
def sample_func_1():

    def sample_func_2():
        print(100)

        def sample_func_3():
            return 300

        return 200

    def sample_func_4(
        price=200
    ):
        return price

    print(200)
    """
    removed_func_str: str = helper._remove_nested_func_str(
        func_str=func_str, func_indent_num=1)
    expected_removed_func_str: str = """def sample_func_1():

    print(200)
    """
    assert removed_func_str == expected_removed_func_str

    func_str = """
    def sample_func_2():
        print(100)

        def sample_func_3():
            return 300

        return 200
    """
    removed_func_str = helper._remove_nested_func_str(
        func_str=func_str, func_indent_num=2)
    expected_removed_func_str = """    def sample_func_2():
        print(100)

        return 200
    """
    assert removed_func_str == expected_removed_func_str


def test__add_line_str() -> None:
    target_str: str = helper._add_line_str(target_str='', line_str='abc')
    assert target_str == 'abc'
    target_str = helper._add_line_str(target_str='abc', line_str='def')
    assert target_str == 'abc\ndef'


def test__type_anotation_comment_exists() -> None:
    result: bool = helper._type_anotation_comment_exists(
        line_str='def sample_func():')
    assert not result

    result = helper._type_anotation_comment_exists(
        line_str='    # type: (int) -> str')
    assert result


def test__remove_type_bracket_block_from_args_str() -> None:
    args_str: str = (
        'dict_val: Optional[Dict[str, int]] = None,'
        ' tuple_val: Optional[Tuple[int, str, int]]=None'
    )
    result_str: str = helper._remove_type_bracket_block_from_args_str(
        args_str=args_str)
    expected_str: str = (
        'dict_val: Optional = None, tuple_val: Optional=None'
    )
    assert result_str == expected_str

    args_str = (
        'list_val_1: List[int],'
        ' list_val_2: Optional[List[int]] = [100, 200]'
    )
    result_str = helper._remove_type_bracket_block_from_args_str(
        args_str=args_str)
    expected_str = (
        'list_val_1: List, list_val_2: Optional = [100, 200]'
    )
    assert result_str == expected_str
