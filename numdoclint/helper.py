"""A module that defines common helper functions etc.
"""

import re
from typing import Dict, List, Optional

ARGS_OR_KWARGS_NAME_LIST: List[str] = [
    '*args',
    '**kwds',
    '**kwargs',
    '**options',
]

ARG_NAME_LIST_TO_IGNORE: List[str] = [
    'self',
    'cls',
]
ARG_NAME_LIST_TO_IGNORE.extend(ARGS_OR_KWARGS_NAME_LIST)

ADDITIONAL_INFO_PREFIX_LIST: List[str] = [
    '.. versionadded',
    '.. deprecated',
    '.. versionchanged',
]


def read_file_str(file_path: str) -> str:
    """
    Read the target file string.

    Parameters
    ----------
    file_path : str
        Path of target file.

    Returns
    -------
    file_str : str
        The target string read.
    """
    with open(file_path, mode='r', encoding='utf-8') as f:
        file_str: str = f.read()
    return file_str


def get_func_name_list(code_str: str) -> List[str]:
    """
    Get a list of function names in the Python module.

    Parameters
    ----------
    code_str : str
        String of target Python code.

    Returns
    -------
    func_name_list : list of str
        List containing function names.
    """
    code_str = code_str.replace('\n', '')
    search_pattern: str = r'def .*?\(.*?\)'
    searched_result_list: List[str] = re.findall(
        pattern=search_pattern, string=code_str)
    func_name_list: List[str] = []
    for searched_result_str in searched_result_list:
        func_name: str = searched_result_str.replace('def ', '')
        func_name = func_name.split('(')[0]
        not_func_str: bool = False
        for char in func_name:
            if not char.isalnum() and char != '_':
                not_func_str = True
                break
        if not_func_str:
            continue
        match: Optional[re.Match] = _get_func_match(
            py_module_str=code_str, func_name=func_name)
        if match is None:
            continue
        func_name_list.append(func_name)
    return func_name_list


def _get_args_str(code_str: str, func_name: str) -> str:
    """
    Get the string of the arguments.

    Parameters
    ----------
    code_str : str
        String of target Python code.
    func_name : str
        Target function name.

    Returns
    -------
    args_str : str
        String of arguments. e.g., 'location_id, price=100'
    """
    search_pattern: str = f'def {func_name}'
    search_pattern = search_pattern + r'.*?\(.*?\)'
    code_str = re.sub(pattern=r'\n', repl='', string=code_str)
    searched_result_list: List[str] = re.findall(
        pattern=search_pattern, string=code_str)
    searched_result_str: str = ''
    for searched_str_unit in searched_result_list:
        searched_func_name: str = searched_str_unit.split('(')[0]
        searched_func_name = searched_func_name.replace(
            'def ', '')
        searched_func_name = searched_func_name.strip()
        if searched_func_name == func_name:
            searched_result_str = searched_str_unit
            break
    if searched_result_str == '':
        return searched_result_str

    args_str: str = searched_result_str.split('def ')[1]
    args_str = args_str.split('(')[1]
    args_str = args_str.split(')')[0]
    args_str = args_str.strip()
    while args_str.find('  ') != -1:
        args_str = args_str.replace('  ', ' ')
    return args_str


def get_arg_name_list(
        py_module_str: str, func_name: str,
        exclude_ignoring_args: Optional[bool] = True) -> List[str]:
    """
    Get a list of argument names of the target function.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.
    exclude_ignoring_args : bool, default True
        Whether to exclude the argument of the ignoring argument
        name setting.

    Returns
    -------
    arg_name_list : list of str
        List of argument names of target function.
    """
    args_str: str = _get_args_str(
        code_str=py_module_str, func_name=func_name)
    args_str = _remove_type_bracket_block_from_args_str(args_str=args_str)
    splitted_arg_name_list: List[str] = args_str.split(',')
    arg_name_list: List[str] = []
    for arg_name in splitted_arg_name_list:
        arg_name = arg_name.replace(' ', '')
        arg_name = arg_name.split(':')[0]
        arg_name = arg_name.split('=')[0]
        if arg_name == '':
            continue
        if exclude_ignoring_args:
            is_in: bool = arg_name in ARG_NAME_LIST_TO_IGNORE
            if is_in:
                continue
        arg_name_list.append(arg_name)
    return arg_name_list


def kwargs_exists(py_module_str: str, func_name: str) -> bool:
    """
    Get a boolean value of whether `**kwargs` exists in the arguments.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    ----------
    result_bool : bool
        If exists, True will be set.
    """
    arg_name_list: List[str] = get_arg_name_list(
        py_module_str=py_module_str,
        func_name=func_name,
        exclude_ignoring_args=False)
    is_in: bool = '**kwargs' in arg_name_list
    if is_in:
        return True
    return False


def get_func_indent_num(py_module_str: str, func_name: str) -> int:
    """
    Get the baseline number of the target function's indents.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    indent_num : int
        If the function is written at the top-level indent, 1 will
        be set. If it is a class method etc., 2 will be set.

    Raises
    ------
    ValueError
        If the target function can not be found.
    """
    match: Optional[re.Match] = _get_func_match(
        py_module_str=py_module_str, func_name=func_name)
    if match is None:
        err_msg = 'Target function not found: %s' % func_name
        raise ValueError(err_msg)
    start_idx: int = match.start()
    space_num: int = 0
    current_idx: int = start_idx - 1
    while True:
        if current_idx < 0:
            break
        target_char: str = py_module_str[current_idx]
        if target_char != ' ':
            break
        space_num += 1
        current_idx -= 1
    indent_num: int = space_num // 4 + 1
    return indent_num


def get_line_indent_num(line_str: str) -> int:
    """
    Get the number of indents of the target line.

    Parameters
    ----------
    line_str : str
        String of target line.

    Returns
    -------
    line_indent_num : int
        Number of indents.
    """
    space_num: int = 0
    for line_char in line_str:
        if line_char != ' ':
            break
        space_num += 1
    line_indent_num: int = space_num // 4
    return line_indent_num


def get_func_overall_docstring(
        py_module_str: str, func_name: str,
        set_indent_to_1: bool = True) -> str:
    """
    Get the target docstring of the target function.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.
    set_indent_to_1 : bool, default True
        Whether set indent to one.

    Returns
    -------
    docstring : str
        Target docstring string.
    """
    match: Optional[re.Match] = _get_func_match(
        py_module_str=py_module_str, func_name=func_name)
    if match is None:
        return ''
    func_indent_num: int = get_func_indent_num(
        py_module_str=py_module_str,
        func_name=func_name)
    start_idx: int = match.start()
    func_str: str = py_module_str[start_idx:]
    func_str = func_str.replace('\\\n', '')
    line_splitted_list: List[str] = func_str.split('\n')
    indent_num: int = get_func_indent_num(
        py_module_str=py_module_str,
        func_name=func_name,
    )
    func_str = ''
    is_docstring_line: bool = False
    for index, line_str in enumerate(line_splitted_list):
        is_docstring_last_line = False
        if index == 0:
            func_str += line_str
            continue
        if _type_anotation_comment_exists(line_str=line_str):
            continue
        if (('"""' in line_str or "'''" in line_str)
                and (not is_docstring_line)):
            is_docstring_line = True
        elif (('"""' in line_str or "'''" in line_str)
                and (is_docstring_line)):
            is_docstring_line = False
            is_docstring_last_line = True
        line_indent_num = get_line_indent_num(line_str=line_str)
        if (line_indent_num < indent_num and line_str != ''
                and line_str.strip() != '):'
                and not is_docstring_line
                and not is_docstring_last_line):
            break
        func_str += '\n%s' % line_str

    stripped_func_str = func_str.replace(' ', '')
    stripped_func_str = stripped_func_str.replace('\n', '')
    double_quote_doc_exists: bool = (
        ':"""' in stripped_func_str
        or ':r"""' in stripped_func_str)
    single_quote_doc_exists: bool = (
        ":'''" in stripped_func_str
        or ":r'''" in stripped_func_str)
    if not double_quote_doc_exists and not single_quote_doc_exists:
        return ''

    docstring: str = ''
    if double_quote_doc_exists:
        match = re.search(
            pattern=r'""".*?"""',
            string=func_str, flags=re.DOTALL)
        docstring = match.group()
        docstring = docstring.replace('"""', '')
    elif single_quote_doc_exists:
        match = re.search(
            pattern=r"'''.*?'''",
            string=func_str, flags=re.DOTALL)
        docstring = match.group()
        docstring = docstring.replace("'''", '')
    docstring = docstring.strip()
    if not docstring.startswith('    '):
        docstring = '    ' * func_indent_num + docstring
    if set_indent_to_1:
        docstring = _set_docstring_indent_number_to_one(
            docstring=docstring,
            indent_num=func_indent_num,
        )
    return docstring


def _type_anotation_comment_exists(line_str: str) -> bool:
    """
    Get a boolean value whether type annotation comment exists
    in line or not.

    Parameters
    ----------
    line_str : str
        The target line string.

    Returns
    -------
    result : bool
        If exists, True will be set.
    """
    result: bool = '# type: ' in line_str
    return result


def _get_func_match(py_module_str: str, func_name: str) -> Optional[re.Match]:
    """
    Get a Match object of search result of target function.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    match : Match or None
        Search result. If not found, None will be set.
    """
    pattern: str = f'def {func_name}'
    for match in re.finditer(pattern=pattern, string=py_module_str):
        match_start_idx: int = match.start()
        match_end_idx: int = match.end()

        is_interactive_shell_example_line_: bool = \
            is_interactive_shell_example_line(
                func_start_index=match_start_idx,
                py_module_str=py_module_str
            )
        if is_interactive_shell_example_line_:
            continue

        func_str: str = py_module_str[match_start_idx:match_end_idx + 10]
        func_str = func_str.replace('\n', '')
        is_in: bool = f'def {func_name}(' in func_str
        if not is_in:
            continue
        return match
    return None


def is_interactive_shell_example_line(
        func_start_index: int, py_module_str: str) -> bool:
    """
    Get a boolean value of whether the target function is
    docstring of interactive shell string (e.g., `>>> def sample():`).

    Parameters
    ----------
    func_start_index : int
        The index of the string at the start of the function.
    py_module_str : str
        String of target module.

    Returns
    -------
    result_bool : bool
        If the target function is a interactive shell docstring string,
        True will be set.
    """
    pre_str: str = py_module_str[func_start_index - 20:func_start_index]
    pre_str = pre_str.split('\n')[-1]
    is_in: bool = '>>> ' in pre_str
    if is_in:
        return True
    is_in = '... ' in pre_str
    if is_in:
        return True
    return False


def _set_docstring_indent_number_to_one(
        docstring: str, indent_num: int) -> str:
    """
    Set the number of indents in docstring to one.

    Parameters
    ----------
    docstring : str
        Target docstring.
    indent_num : int
        Indent's baseline number of the target function.

    Returns
    -------
    docstring : str
        Docstring after adjusting the number of indents.
    """
    if indent_num == 1:
        return docstring
    while indent_num > 1:
        docstring = re.sub(
            pattern=r'^    ', repl='', string=docstring,
            flags=re.MULTILINE)
        indent_num -= 1
    return docstring


DOC_PARAM_INFO_KEY_ARG_NAME: str = 'arg_name'
DOC_PARAM_INFO_KEY_TYPE_NAME: str = 'type_name'
DOC_PARAM_INFO_KEY_DEFAULT_VAL: str = 'default_value'
DOC_PARAM_INFO_KEY_DESCRIPTION: str = 'description'


def get_docstring_param_info_list(docstring: str) -> List[Dict[str, str]]:
    """
    Get a list of argument information in docstring.

    Parameters
    ----------
    docstring : str
        Target docstring string.

    Returns
    -------
    param_info_list : list of dicts
        List containing argument information.
        Values are set in the dictionary with the following keys.
        - DOC_PARAM_INFO_KEY_ARG_NAME : str -> Argument name.
        - DOC_PARAM_INFO_KEY_TYPE_NAME : str -> Name of the type.
        - DOC_PARAM_INFO_KEY_DEFAULT_VAL : str -> Description of the
            default value.
        - DOC_PARAM_INFO_KEY_DESCRIPTION : str -> Description of the
            argument.
    """
    if docstring == '':
        return []
    if not _parameters_exists_in_docstring(docstring=docstring):
        return []
    splitted_param_doc_list: List[str] = get_splitted_param_doc_list(
        docstring=docstring
    )
    param_info_list: List[Dict[str, str]] = []
    for splitted_param_doc in splitted_param_doc_list:
        arg_name: str = _get_docstring_var_name(var_doc=splitted_param_doc)
        type_name: str = _get_docstring_type_name(var_doc=splitted_param_doc)
        default_val: str = _get_docstring_default_value(
            var_doc=splitted_param_doc)
        description: str = _get_docstring_var_description(
            var_doc=splitted_param_doc)
        param_info_list = _append_param_info_to_list(
            param_info_list=param_info_list,
            arg_name=arg_name,
            type_name=type_name,
            default_val=default_val,
            description=description)
    return param_info_list


def _append_param_info_to_list(
        param_info_list: List[Dict[str, str]], arg_name: str, type_name: str,
        default_val: str, description: str) -> List[Dict[str, str]]:
    """
    Add docstring argument information to the list.

    Notes
    -----
    If the argument name contains a comma, it will be split
    and add to the list.

    Parameters
    ----------
    param_info_list : list of dicts
        The list to add to.
    arg_name : str
        Target argument name.
    type_name : str
        Target type name.
    default_val : str
        Target default value.
    description : str
        Argument description.

    Returns
    ----------
    param_info_list : list of dicts
        List after dict addition.
    """
    comma_exists: bool = ',' in arg_name
    if not comma_exists:
        param_info_list.append({
            DOC_PARAM_INFO_KEY_ARG_NAME: arg_name,
            DOC_PARAM_INFO_KEY_TYPE_NAME: type_name,
            DOC_PARAM_INFO_KEY_DEFAULT_VAL: default_val,
            DOC_PARAM_INFO_KEY_DESCRIPTION: description,
        })
        return param_info_list
    arg_name_list: List[str] = arg_name.split(',')
    for arg_name in arg_name_list:
        arg_name = arg_name.strip()
        param_info_list.append({
            DOC_PARAM_INFO_KEY_ARG_NAME: arg_name,
            DOC_PARAM_INFO_KEY_TYPE_NAME: type_name,
            DOC_PARAM_INFO_KEY_DEFAULT_VAL: default_val,
            DOC_PARAM_INFO_KEY_DESCRIPTION: description,
        })
    return param_info_list


def _parameters_exists_in_docstring(docstring: str) -> bool:
    """
    Get boolean of whether Parater part exists in docstring
    or not.

    Parameters
    ----------
    docstring : str
        Docstring to be checked.

    Returns
    -------
    result_bool : bool
        If exists, True will be set.
    """
    is_in: bool = 'Parameters\n    ---' in docstring
    if not is_in:
        return False
    return True


def _get_docstring_var_description(var_doc: str) -> str:
    """
    Get a description of argument or return value from docstring.

    Parameters
    ----------
    var_doc : str
        Docstring's part of argument or return value.

    Returns
    -------
    description : str
        Description of argument or return value.
    """
    var_doc = var_doc.rstrip()
    splitted_list: List[str] = var_doc.split('\n')
    if len(splitted_list) < 2:
        return ''
    description: str = '\n'.join(splitted_list[1:])
    description = description.rstrip()
    return description


def _get_docstring_default_value(var_doc: str) -> str:
    """
    Get the description of argument's default value from docstring.

    Parameters
    ----------
    var_doc : str
        Docstring's part of argument.

    Returns
    -------
    default_val : str
        Description of the defautl value.
    """
    default_val: str = var_doc.split('\n')[0]
    is_in: bool = ', default ' in default_val or '(default ' in default_val
    if not is_in:
        return ''
    default_val = default_val.split('default')[1]
    default_val = default_val.split(',')[0]
    default_val = default_val.replace(')', '')
    default_val = default_val.strip()
    return default_val


def _get_docstring_type_name(var_doc: str) -> str:
    """
    Get the string of argument or return value type's description
    from docstring.

    Parameters
    ----------
    var_doc : str
        Docstring's part of argument or return value.

    Returns
    -------
    type_name : str
        Argument or return value's type description.
    """
    type_name: str = var_doc.split('\n')[0]
    colon_exists: bool = ':' in type_name
    if not colon_exists:
        return ''
    type_name = type_name.split(':')[1]
    type_name = type_name.split(',')[0]
    type_name = type_name.strip()
    return type_name


def _get_docstring_var_name(var_doc: str) -> str:
    """
    Get the name of argument or return value from docstring.

    Parameters
    ----------
    var_doc : str
        Docstring's part of argument or return value.

    Returns
    -------
    var_name : str
        Argument or return value name.
    """
    var_name: str = var_doc.split(':')[0]
    var_name = var_name.split('\n')[0]
    var_name = var_name.strip()
    return var_name


def get_splitted_param_doc_list(docstring: str) -> List[str]:
    """
    Get docstring string splitted into each argument.

    Parameters
    ----------
    docstring : str
        Target docstring string.

    Returns
    -------
    splitted_param_doc_list : list of str
        List of splitted arugment information.
    """
    param_docstring: str = get_param_docstring(docstring=docstring)
    line_splitted_param_doc_list: List[str] = param_docstring.split('\n')
    single_param_doc: str = ''
    splitted_param_doc_list: List[str] = []
    for line_str in line_splitted_param_doc_list:
        indent_num: int = get_line_indent_num(line_str=line_str)
        if indent_num == 1:
            if single_param_doc.strip() != '':
                splitted_param_doc_list.append(single_param_doc)
            single_param_doc = ''
        if single_param_doc != '':
            single_param_doc += '\n'
        single_param_doc += line_str
    if single_param_doc.strip() != '':
        splitted_param_doc_list.append(single_param_doc)
    return splitted_param_doc_list


def get_param_docstring(docstring: str) -> str:
    """
    Get docstring of argument part.

    Parameters
    ----------
    docstring : str
        Target docstring string.

    Returns
    -------
    param_docstring : str
        Argument part docstring.
    """
    param_part_started: bool = False
    initial_hyphen_appeared: bool = False
    line_splitted_docstring_list: List[str] = docstring.split('\n')
    param_docstring: str = ''
    pre_line_str: str = ''
    second_hyphen_exists: bool = False
    for line_str in line_splitted_docstring_list:
        if line_str == '    Parameters':
            param_part_started = True
            continue
        is_hyphen_line: bool = '----' in line_str
        if (param_part_started
                and not initial_hyphen_appeared
                and is_hyphen_line):
            initial_hyphen_appeared = True
            continue
        if not initial_hyphen_appeared:
            continue
        if is_hyphen_line:
            second_hyphen_exists = True
            break

        if pre_line_str != '':
            if param_docstring != '':
                param_docstring += '\n'
            param_docstring += pre_line_str
        pre_line_str = line_str

    if not second_hyphen_exists:
        if param_docstring != '':
            param_docstring += '\n'
        param_docstring += pre_line_str
    return param_docstring


def get_func_description_from_docstring(docstring: str) -> str:
    """
    Get the string of the function's description in docstring.

    Parameters
    ----------
    docstring : str
        Target docstring.

    Returns
    ----------
    func_description : str
        Description of the function in docstring.
    """
    if docstring == '':
        return ''
    last_line_num: int = 0
    line_splitted_list: List[str] = docstring.split('\n')
    for line_str in line_splitted_list:
        is_hyphen_line: bool = '----' in line_str
        if is_hyphen_line:
            last_line_num -= 1
            break
        last_line_num += 1
    if last_line_num <= 0:
        return ''
    func_description: str = '\n'.join(line_splitted_list[:last_line_num])
    func_description = func_description.strip()
    if func_description.replace(' ', '') == '':
        return ''
    if not func_description.startswith('    '):
        func_description = '    %s' % func_description
    return func_description


def get_arg_default_val_info_dict(
        py_module_str: str, func_name: str) -> Dict[str, str]:
    """
    Get a dictionary containing information on default values
    of arguments.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    default_val_info_dict : dict
        A dctionary that stores argument names in keys and default
        values in values.

    Notes
    -----
    The default value stored in the dictionary will be set
    as a string.
    """
    args_str: str = _get_args_str(
        code_str=py_module_str, func_name=func_name)
    args_str = _remove_type_bracket_block_from_args_str(args_str=args_str)
    if args_str == '':
        return {}
    splitted_arg_list: List[str] = args_str.split(',')
    default_val_info_dict: Dict[str, str] = {}
    for arg_str in splitted_arg_list:
        arg_str = arg_str.replace(' ', '')
        arg_str = _remove_type_str_from_arg_str(arg_str=arg_str)
        default_val_exists: bool = '=' in arg_str
        if not default_val_exists:
            default_val_info_dict[arg_str] = ''
            continue
        name_and_default_val_list: List[str] = arg_str.split('=')
        arg_name: str = name_and_default_val_list[0]
        default_val: str = name_and_default_val_list[1]
        default_val_info_dict[arg_name] = default_val
    return default_val_info_dict


def _remove_type_bracket_block_from_args_str(args_str: str) -> str:
    """
    Remove type annotation block bracket from arguments string.

    Parameters
    ----------
    args_str : str
        The target arguments string.
        e.g., 'dict_val: Dict[str, int] == {}'

    Returns
    -------
    result_str : str
        The converted arguments string.
        e.g., 'dict_val: Dict == {}'
    """
    if '[' not in args_str:
        return args_str
    bracket_count: int = 0
    result_str: str = ''
    is_type_block: bool = False
    for char in args_str:
        if bracket_count == 0 and char == ':':
            is_type_block = True
        if is_type_block and char == '[':
            bracket_count += 1
            continue
        if is_type_block and char == ']':
            bracket_count -= 1
            continue
        if bracket_count == 0 and (char == ',' or char == '='):
            is_type_block = False
        if bracket_count != 0:
            continue
        result_str += char
    return result_str


def _remove_type_str_from_arg_str(arg_str: str) -> str:
    """
    Remove the string of type information from the argument string.

    Parameters
    ----------
    arg_str : str
        The target argument string.

    Returns
    -------
    after_arg_str : str
        String after type information has been removed.
    """
    arg_str = arg_str.replace(' = ', '=')
    is_in: bool = ':' in arg_str
    if not is_in:
        return arg_str
    after_arg_str: str = arg_str.split(':')[0]
    is_in = '=' in arg_str
    if is_in:
        after_arg_str += '=%s' % arg_str.split('=')[1]
    after_arg_str = after_arg_str.strip()
    return after_arg_str


DOC_RETURN_INFO_KEY_NAME: str = 'name'
DOC_RETURN_INFO_KEY_TYPE_NAME: str = 'type_name'
DOC_RETURN_INFO_KEY_DESCRIPTION: str = 'description'


def get_docstring_return_val_info_list(
        docstring: str) -> List[Dict[str, str]]:
    """
    Get a list of return value information in docstring.

    Parameters
    ----------
    docstring : str
        Target docstring string.

    Returns
    -------
    return_val_info_list : list of dicts
        List containing return value information.
        Values are set in the dictionary with the following keys.
        - DOC_RETURN_INFO_KEY_NAME : str -> Return value name.
            If the style only describes the type name, blank string
            will be set.
        - DOC_RETURN_INFO_KEY_TYPE_NAME : str -> Type name of
            return value.
        - DOC_RETURN_INFO_KEY_DESCRIPTION : str -> Description of
            the return value.
    """
    return_value_docstring: str = _get_return_value_docstring(
        docstring=docstring)
    if return_value_docstring == '':
        return []
    line_splitted_list: List[str] = return_value_docstring.split('\n')
    name: str = ''
    type_name: str = ''
    description: str = ''
    return_val_info_list: List[Dict[str, str]] = []
    for line_str in line_splitted_list:
        if line_str.replace(' ', '') == '':
            continue
        line_indent_num: int = get_line_indent_num(line_str=line_str)
        if (line_indent_num == 1
                and name != ''
                and not _is_additional_info_str(target_str=name)):
            return_val_info_list = _append_return_value_info_unit_dict(
                name=name, type_name=type_name, description=description,
                return_val_info_list=return_val_info_list)
        if line_indent_num == 1:
            name = _get_return_value_name_from_line(line_str=line_str)
            type_name = _get_return_value_type_name_from_line(
                line_str=line_str)
            description = ''
            continue
        if line_indent_num == 2:
            if description != '':
                description += '\n'
            description += line_str
            continue
    if name != '' or type_name != '' or description != '':
        if not _is_additional_info_str(target_str=name):
            return_val_info_list = _append_return_value_info_unit_dict(
                name=name, type_name=type_name, description=description,
                return_val_info_list=return_val_info_list)
    return return_val_info_list


def _is_additional_info_str(target_str: str) -> bool:
    """
    Get a boolean value whether the target string is additional
    infomation string (e.g., `.. versionadded:: 0.0.1`).

    Parameters
    ----------
    target_str : str
        The target string.

    Returns
    -------
    result_bool : bool
        If the target string is additional information, then True
        will be set.
    """
    target_str = target_str.strip()
    for additional_info_prefix in ADDITIONAL_INFO_PREFIX_LIST:
        if target_str.startswith(additional_info_prefix):
            return True
    return False


def _append_return_value_info_unit_dict(
        name: str, type_name: str, description: str,
        return_val_info_list: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Add a return value docstring information dictionary
    to the list.

    Parameters
    ----------
    name : str
        Return value name.
    type_name : str
        Type name of return value.
    description : str
        Description of the return value.
    return_val_info_list : list of dicts
        List containing return value information.

    Returns
    ----------
    return_val_info_list : list of dicts
        List containing return value information.
        Values are set in the dictionary with the following keys.
        - DOC_RETURN_INFO_KEY_NAME : str
        - DOC_RETURN_INFO_KEY_TYPE_NAME : str
        - DOC_RETURN_INFO_KEY_DESCRIPTION : str
    """
    return_value_info_dict: Dict[str, str] = {
        DOC_RETURN_INFO_KEY_NAME: name,
        DOC_RETURN_INFO_KEY_TYPE_NAME: type_name,
        DOC_RETURN_INFO_KEY_DESCRIPTION: description,
    }
    return_val_info_list.append(return_value_info_dict)
    return return_val_info_list


def _get_return_value_name_from_line(line_str: str) -> str:
    """
    Get the return value name from the target line string.

    Parameters
    ----------
    line_str : str
        Target line string. e.g., 'price : int'

    Returns
    -------
    return_value_name : str
        Return value name. If colon character not exists in
        line string, a blank string will be set.
    """
    colon_exists: bool = ':' in line_str
    if colon_exists:
        return_value_name: str = line_str.split(':')[0]
    else:
        return_value_name = ''
    return_value_name = return_value_name.strip()
    return return_value_name


def _get_return_value_type_name_from_line(line_str: str) -> str:
    """
    Get the type name of return value from the target line string.

    Parameters
    ----------
    line_str : str
        Target line string.

    Returns
    ----------
    return_value_type_name : str
        Type name of return value.
    """
    colon_exists: bool = ':' in line_str
    if not colon_exists:
        return_value_type_name: str = line_str.split(':')[0]
    else:
        return_value_type_name = line_str.split(':')[1]
    return_value_type_name = return_value_type_name.strip()
    return return_value_type_name


def _get_return_value_docstring(
        docstring: str, drop_additional_info: bool = True) -> str:
    """
    Get the string of docstring's return value part.

    Parameters
    ----------
    docstring : str
        Target docstring string.
    drop_additional_info : bool, default True
        Whether to drop additional information (e.g., versionadded).

    Returns
    -------
    return_value_docstring : str
        String of docstring return value information.
    """
    if docstring == '':
        return ''
    start_line_idx: int = 0
    last_line_idx: int = 0
    line_splitted_list: List[str] = docstring.split('\n')
    for i, line_str in enumerate(line_splitted_list):
        is_in: bool = 'Returns' in line_str
        if not is_in:
            continue
        hyphens_exists_next_line: bool = _hyphens_exists_next_line(
            line_splitted_list=line_splitted_list,
            next_line_idx=i + 1)
        if not hyphens_exists_next_line:
            continue
        start_line_idx = i + 2
        break
    if start_line_idx == 0:
        return ''

    second_hyphen_exists: bool = False
    for i, line_str in enumerate(line_splitted_list):
        if i < start_line_idx:
            continue
        last_line_idx = i
        is_hyphen_line: bool = '----' in line_str
        if not is_hyphen_line:
            continue
        last_line_idx -= 2
        second_hyphen_exists = True
        break
    if not second_hyphen_exists:
        last_line_idx += 1
    docstring = '\n'.join(
        line_splitted_list[start_line_idx:last_line_idx])
    docstring = docstring.strip()

    if drop_additional_info:
        for additional_info_prefix in ADDITIONAL_INFO_PREFIX_LIST:
            is_in = additional_info_prefix in docstring
            if not is_in:
                continue
            docstring = docstring.split(additional_info_prefix)[0]
            docstring = docstring.strip()

    if not docstring.startswith('    '):
        docstring = '    %s' % docstring

    return docstring


def _hyphens_exists_next_line(
        line_splitted_list: List[str], next_line_idx: int) -> bool:
    """
    Get the boolean value of whether there are multiple hyphen
    characters on the next line.

    Parameters
    ----------
    line_splitted_list : list of str
        A list containing line-by-line strings.
    next_line_idx : int
        Next line index.

    Returns
    -------
    result_bool : bool
        If exists, True will be set.
    """
    if len(line_splitted_list) < next_line_idx + 1:
        return False
    next_line_str: str = line_splitted_list[next_line_idx]
    is_in: bool = '----' in next_line_str
    if is_in:
        return True
    return False


def get_func_str(module_str: str, func_name: str) -> str:
    """
    Get the entire function string including docstring and content.

    Parameters
    ----------
    module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    func_str : str
        The entire function string including docstring and content.
    """
    if module_str == '':
        return ''
    line_splitted_list: List[str] = module_str.split('\n')
    start_line_idx: Optional[int] = None
    last_line_idx: Optional[int] = None
    def_line_str = f'def {func_name}'
    func_indent_baseline_num: int = 0
    for i, line_str in enumerate(line_splitted_list):
        is_def_line_str: bool = def_line_str in line_str
        if not is_def_line_str:
            continue
        func_indent_baseline_num = get_line_indent_num(
            line_str=line_str)
        start_line_idx = i
        break
    if start_line_idx is None:
        return ''

    for i, line_str in enumerate(line_splitted_list):
        if i <= start_line_idx:
            continue
        line_indent_num: int = get_line_indent_num(
            line_str=line_str)
        if line_indent_num > func_indent_baseline_num:
            continue
        line_str = line_str.strip()
        if line_str == '':
            continue
        if line_str.strip() == '):':
            continue
        last_line_idx = i
        break

    func_str: str = '\n'.join(
        line_splitted_list[start_line_idx:last_line_idx])
    func_str = func_str.rstrip()
    return func_str


def return_val_exists_in_func(module_str: str, func_name: str) -> bool:
    """
    Get a boolean value of whether or not there is a return
    value in the functions.

    Parameters
    ----------
    module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    ----------
    result_bool : bool
        If there is no return statement, or if the return
        statement does not return a value, False will be set.
    """
    func_str: str = get_func_str(module_str=module_str, func_name=func_name)
    func_str = _remove_docstring_from_func_str(
        func_str=func_str, module_str=module_str, func_name=func_name)
    if func_str == '':
        return False
    func_indent_num: int = get_func_indent_num(
        py_module_str=module_str,
        func_name=func_name)
    func_str = _remove_nested_func_str(
        func_str=func_str, func_indent_num=func_indent_num)
    if func_str == '':
        return False
    line_splitted_list: List[str] = func_str.split('\n')
    for line_str in line_splitted_list:
        return_statement_exists: bool = ' return ' in line_str
        if not return_statement_exists:
            continue
        return_val_str: str = re.sub(
            pattern=r'^.*return', repl='', string=line_str)
        return_val_str = return_val_str.strip()
        if return_val_str == '':
            continue
        return True
    return False


def _add_line_str(target_str: str, line_str: str) -> str:
    """
    Add target line string for string concatenation.

    Parameters
    ----------
    target_str : str
        The string to be concatenated.
    line_str : str
        String of target line.

    Returns
    -------
    target_str : str
        Concatenated string.
    """

    if target_str != '':
        target_str += '\n'
    target_str += line_str
    return target_str


def _remove_nested_func_str(func_str: str, func_indent_num: int) -> str:
    """
    Remove the string of nested function part.

    Parameters
    ----------
    func_str : str
        Target function string.
    func_indent_num : int
        Indent number of the target function (starting from 1).

    Returns
    -------
    removed_func_str : str
        The string after removed nested function part.
    """

    removed_func_str: str = ''
    line_splitted_list: List[str] = func_str.split('\n')
    is_initial_function_appeared: bool = False
    is_nested_func_line: bool = False
    for line_str in line_splitted_list:
        is_func_statement_in: bool = 'def ' in line_str
        if not is_nested_func_line:
            if not is_func_statement_in or not is_initial_function_appeared:
                removed_func_str = _add_line_str(
                    target_str=removed_func_str, line_str=line_str)
        if not is_initial_function_appeared and is_func_statement_in:
            is_initial_function_appeared = True
            continue
        if not is_initial_function_appeared:
            continue
        line_indent_num: int = get_line_indent_num(line_str=line_str)
        if is_nested_func_line:
            if line_str.strip() == '' or '):' in line_str:
                continue
            if (line_indent_num <= func_indent_num
                    and not is_func_statement_in):
                is_nested_func_line = False
                removed_func_str = _add_line_str(
                    target_str=removed_func_str, line_str=line_str)
                continue
        if is_func_statement_in and not is_nested_func_line:
            if line_indent_num < func_indent_num:
                continue
            is_nested_func_line = True
            continue
    return removed_func_str


def _remove_docstring_from_func_str(
        func_str: str, module_str: str, func_name: str) -> str:
    """
    Remove the doctring from the function string.

    Parameters
    ----------
    func_str : str
        Target function string.
    module_str : str
        String of the whole target module.
    func_name : str
        Target function name.

    Returns
    ----------
    func_str : str
        Function string after processing.
    """
    docstring: str = get_func_overall_docstring(
        py_module_str=module_str, func_name=func_name,
        set_indent_to_1=False)
    func_str = func_str.replace(docstring, '')
    func_str = func_str.replace(
        docstring.replace('    ', '', 1), '')
    line_splitted_list: List[str] = func_str.split('\n')
    if len(line_splitted_list) >= 4:
        double_quote_idx_1_exists: bool = '"""' in line_splitted_list[1]
        double_quote_idx_2_exists: bool = '"""' in line_splitted_list[2]
        double_quote_idx_3_exists: bool = '"""' in line_splitted_list[3]
        single_quote_idx_1_exists: bool = "'''" in line_splitted_list[1]
        single_quote_idx_2_exists: bool = "'''" in line_splitted_list[2]
        single_quote_idx_3_exists: bool = "'''" in line_splitted_list[3]
        pop_index_list: List[int] = []
        if ((double_quote_idx_1_exists and double_quote_idx_2_exists)
                or (single_quote_idx_1_exists and single_quote_idx_2_exists)):
            pop_index_list = [2, 1]
        if ((double_quote_idx_1_exists and double_quote_idx_3_exists)
                or (single_quote_idx_1_exists and single_quote_idx_3_exists)):
            pop_index_list = [3, 2, 1]
        for pop_index in pop_index_list:
            line_splitted_list.pop(pop_index)
    func_str = '\n'.join(line_splitted_list)
    return func_str


def get_optional_arg_name_list(docstring: str) -> List[str]:
    """
    Get a list of argument names specified as optional.

    Parameters
    ----------
    docstring : str
        Target docstring.

    Returns
    -------
    optional_arg_name_list : list of str
        A list of argument names specified as optional.
    """
    if docstring == '':
        return []
    if not _parameters_exists_in_docstring(docstring=docstring):
        return []
    splitted_param_doc_list: List[str] = get_splitted_param_doc_list(
        docstring=docstring)
    optional_arg_name_list: List[str] = []
    for splitted_param_doc in splitted_param_doc_list:
        first_line_str: str = splitted_param_doc.split('\n')[0]
        optional_str_exists: bool = 'optional' in first_line_str
        if not optional_str_exists:
            continue
        arg_name: str = _get_docstring_var_name(var_doc=splitted_param_doc)
        optional_arg_name_list.append(arg_name)
    return optional_arg_name_list


def args_or_kwargs_str_in_param_name(param_arg_name: str) -> bool:
    """
    Get a boolean value of whether the string of `*args`
    or `**kwargs` is included in the docstring argument
    name information.

    Parameters
    ----------
    param_arg_name : str
        The docstring argument name information.

    Returns
    ----------
    result_bool : bool
        If included, True will be set.
    """

    param_arg_name = param_arg_name.strip()
    for args_or_kwargs_str in ARGS_OR_KWARGS_NAME_LIST:
        is_in: bool = args_or_kwargs_str in param_arg_name
        if is_in:
            return True
    return False


def get_decorator_names(py_module_str: str, func_name: str) -> List[str]:
    """
    Get a list of decorator names set in the target function.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    decorator_names : list of str
        A list of decorator names.
    """
    line_splitted_list: List[str] = py_module_str.split('\n')
    func_start_line_index: int = _get_func_start_line_index(
        line_splitted_list=line_splitted_list, func_name=func_name)
    if func_start_line_index == -1:
        return []
    decorator_names: List[str] = []
    current_target_line_idx: int = func_start_line_index - 1

    in_bracket: bool = False
    while current_target_line_idx >= 0:
        line_str: str = line_splitted_list[current_target_line_idx]
        at_exists: bool = '@' in line_str
        if in_bracket and not at_exists:
            current_target_line_idx -= 1
            continue

        if in_bracket and at_exists:
            decorator_names.append(line_str.strip())
            current_target_line_idx -= 1
            in_bracket = False
            continue

        right_bracket_exists: bool = ')' in line_str
        if right_bracket_exists and not at_exists:
            in_bracket = True
            current_target_line_idx -= 1
            continue

        if not at_exists:
            break
        decorator_names.append(line_str.strip())
        current_target_line_idx -= 1
    return decorator_names


def _get_func_start_line_index(
        line_splitted_list: List[str], func_name: str):
    """
    Get the start line index of the target function.

    Parameters
    ----------
    line_splitted_list : list of str
        A list of strings separated by line.
    func_name : str
        Target function name.

    Returns
    -------
    func_start_line_index : int
        The start line index of the target function. If target
        function name not found, -1 will be set.
    """
    search_str: str = f'def {func_name}'
    for i, line_str in enumerate(line_splitted_list):
        is_in: bool = search_str in line_str
        if not is_in:
            continue
        if i + 1 >= len(line_splitted_list):
            continue
        next_line_str: str = line_splitted_list[i + 1]
        concatenated_str: str = line_str + next_line_str
        concatenated_str = concatenated_str.replace('\n', '')
        concatenated_str = concatenated_str.strip()
        is_in = f'def {func_name}(' in concatenated_str
        if not is_in:
            continue
        return i
    return -1
