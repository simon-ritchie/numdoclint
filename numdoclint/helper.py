"""A module that defines common helper functions etc.
"""

import re


def read_file_str(file_path):
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
    with open(file_path, 'r') as f:
        file_str = f.read()
    return file_str


def get_func_name_list(py_module_str):
    """
    Get a list of function names in the Python module.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.

    Returns
    -------
    func_name_list : list of str
        List containing function names.
    """
    search_pattern = r'def .*\(.*\)'
    searched_result_list = re.findall(
        pattern=search_pattern, string=py_module_str)
    func_name_list = []
    for searched_result_str in searched_result_list:
        func_name = searched_result_str.replace('def ', '')
        func_name = func_name.split('(')[0]
        func_name_list.append(func_name)
    return func_name_list


def _get_args_str(py_module_str, func_name):
    """
    Get the string of the arguments.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    args_str : str
        String of arguments. e.g., 'location_id, price=100'
    """
    search_pattern = 'def %s' % func_name
    search_pattern = search_pattern + r'.*\(.*\)'
    py_module_str = re.sub(pattern=r'\n', repl='', string=py_module_str)
    searched_result_list = re.findall(
        pattern=search_pattern, string=py_module_str)
    searched_result_str = searched_result_list[0]

    args_str = searched_result_str.split('def ')[1]
    args_str = args_str.split('(')[1]
    args_str = args_str.split(')')[0]
    args_str = args_str.strip()
    while args_str.find('  ') != -1:
        args_str = args_str.replace('  ', ' ')
    return args_str


def get_arg_name_list(py_module_str, func_name):
    """
    Get a list of argument names of the target function.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    arg_name_list : list of str
        List of argument names of target function.
    """
    args_str = _get_args_str(
        py_module_str=py_module_str, func_name=func_name)
    splitted_arg_name_list = args_str.split(',')
    arg_name_list = []
    for arg_name in splitted_arg_name_list:
        arg_name = arg_name.replace(' ', '')
        arg_name = arg_name.split(':')[0]
        arg_name = arg_name.split('=')[0]
        if arg_name == '':
            continue
        arg_name_list.append(arg_name)
    return arg_name_list


def get_func_indent_num(py_module_str, func_name):
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
    pattern = 'def %s' % func_name
    pattern = r'\n.*' + pattern
    match = re.search(pattern=pattern, string=py_module_str)
    if match is None:
        err_msg = 'Target function not found: %s' % func_name
        raise ValueError(err_msg)
    start_idx = match.start()
    func_str = py_module_str[start_idx:]
    func_str = func_str.replace('\n', '')
    space_num = 0
    for func_char in func_str:
        if func_char != ' ':
            break
        space_num += 1
    indent_num = space_num // 4 + 1
    return indent_num


def get_line_indent_num(line_str):
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
    space_num = 0
    for line_char in line_str:
        if line_char != ' ':
            break
        space_num += 1
    line_indent_num = space_num // 4
    return line_indent_num


def get_func_overall_docstring(py_module_str, func_name):
    """
    Get the target docstring fo the target function.

    Parameters
    ----------
    py_module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    docstring : str
        Target docstring string.
    """
    match = re.search('def %s' % func_name, py_module_str)
    if match is None:
        return ''
    func_indent_num = get_func_indent_num(
        py_module_str=py_module_str,
        func_name=func_name)
    start_idx = match.start()
    func_str = py_module_str[start_idx:]
    line_splitted_list = func_str.split('\n')
    indent_num = get_func_indent_num(
        py_module_str=py_module_str,
        func_name=func_name,
    )
    func_str = ''
    for index, line_str in enumerate(line_splitted_list):
        if index == 0:
            func_str += line_str
            continue
        line_indent_num = get_line_indent_num(line_str=line_str)
        if line_indent_num < indent_num and line_str != '':
            break
        func_str += '\n%s' % line_str

    double_quote_doc_exists = '"""' in func_str
    single_quote_doc_exists = "'''" in func_str
    if not double_quote_doc_exists and not single_quote_doc_exists:
        return ''

    if double_quote_doc_exists:
        match = re.search(
            pattern=r'""".*?"""',
            string=func_str, flags=re.DOTALL)
        docstring = match.group()
        docstring = docstring.replace('"""', '')
    if single_quote_doc_exists:
        match = re.search(
            pattern=r"'''.*?'''",
            string=func_str, flags=re.DOTALL)
        docstring = match.group()
        docstring = docstring.replace("'''", '')
    docstring = docstring.strip()
    if not docstring.startswith('    '):
        docstring = '    ' * func_indent_num + docstring
    docstring = _set_docstring_indent_number_to_one(
        docstring=docstring,
        indent_num=func_indent_num,
    )
    return docstring


def _set_docstring_indent_number_to_one(docstring, indent_num):
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


DOC_PARAM_INFO_KEY_ARG_NAME = 'arg_name'
DOC_PARAM_INFO_KEY_TYPE_NAME = 'type_name'
DOC_PARAM_INFO_KEY_DEFAULT_VAL = 'default_value'
DOC_PARAM_INFO_KEY_DESCRIPTION = 'description'


def get_docstring_param_info_list(docstring):
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
    is_in = 'Parameters\n    ---' in docstring
    if not is_in:
        return []
    splitted_param_doc_list = get_splitted_param_doc_list(
        docstring=docstring
    )
    param_info_list = []
    for splitted_param_doc in splitted_param_doc_list:
        arg_name = _get_docstring_var_name(var_doc=splitted_param_doc)
        type_name = _get_docstring_type_name(var_doc=splitted_param_doc)
        default_val = _get_docstring_default_value(var_doc=splitted_param_doc)
        description = _get_docstring_var_description(
            var_doc=splitted_param_doc)
        param_info_dict = {
            DOC_PARAM_INFO_KEY_ARG_NAME: arg_name,
            DOC_PARAM_INFO_KEY_TYPE_NAME: type_name,
            DOC_PARAM_INFO_KEY_DEFAULT_VAL: default_val,
            DOC_PARAM_INFO_KEY_DESCRIPTION: description,
        }
        param_info_list.append(param_info_dict)
    return param_info_list


def _get_docstring_var_description(var_doc):
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
    splitted_list = var_doc.split('\n')
    if len(splitted_list) < 2:
        return ''
    description = '\n'.join(splitted_list[1:])
    description = description.rstrip()
    return description


def _get_docstring_default_value(var_doc):
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
    default_val = var_doc.split('\n')[0]
    is_in = 'default' in default_val
    if not is_in:
        return ''
    default_val = default_val.split('default')[1]
    default_val = default_val.split(',')[0]
    default_val = default_val.strip()
    return default_val


def _get_docstring_type_name(var_doc):
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
    type_name = var_doc.split('\n')[0]
    colon_exists = ':' in type_name
    if not colon_exists:
        return ''
    type_name = type_name.split(':')[1]
    type_name = type_name.split(',')[0]
    type_name = type_name.strip()
    return type_name


def _get_docstring_var_name(var_doc):
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
    var_name = var_doc.split(':')[0]
    var_name = var_name.strip()
    return var_name


def get_splitted_param_doc_list(docstring):
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
    param_docstring = get_param_docstring(docstring=docstring)
    line_splitted_param_doc_list = param_docstring.split('\n')
    single_param_doc = ''
    splitted_param_doc_list = []
    for line_str in line_splitted_param_doc_list:
        indent_num = get_line_indent_num(line_str=line_str)
        if indent_num == 1:
            if single_param_doc != '':
                splitted_param_doc_list.append(single_param_doc)
            single_param_doc = ''
        if single_param_doc != '':
            single_param_doc += '\n'
        single_param_doc += line_str
    if single_param_doc != '':
        splitted_param_doc_list.append(single_param_doc)
    return splitted_param_doc_list


def get_param_docstring(docstring):
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
    param_part_started = False
    initial_hyphen_appeared = False
    line_splitted_docstring_list = docstring.split('\n')
    param_docstring = ''
    pre_line_str = ''
    second_hyphen_exists = False
    for line_str in line_splitted_docstring_list:
        if line_str == '    Parameters':
            param_part_started = True
            continue
        is_hyphen_line = '----' in line_str
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


def get_func_description_from_docstring(docstring):
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
    last_line_num = 0
    line_splitted_list = docstring.split('\n')
    for line_str in line_splitted_list:
        is_hyphen_line = '----' in line_str
        if is_hyphen_line:
            last_line_num -= 1
            break
        last_line_num += 1
    if last_line_num <= 0:
        return ''
    func_description = '\n'.join(line_splitted_list[:last_line_num])
    func_description = func_description.strip()
    if func_description.replace(' ', '') == '':
        return ''
    if not func_description.startswith('    '):
        func_description = '    %s' % func_description
    return func_description


def get_arg_default_val_info_dict(py_module_str, func_name):
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
    args_str = _get_args_str(
        py_module_str=py_module_str, func_name=func_name)
    if args_str == '':
        return {}
    splitted_arg_list = args_str.split(',')
    default_val_info_dict = {}
    for arg_str in splitted_arg_list:
        arg_str = arg_str.replace(' ', '')
        arg_str = arg_str.split(':')[0]
        default_val_exists = '=' in arg_str
        if not default_val_exists:
            default_val_info_dict[arg_str] = ''
            continue
        name_and_default_val_list = arg_str.split('=')
        arg_name = name_and_default_val_list[0]
        default_val = name_and_default_val_list[1]
        default_val_info_dict[arg_name] = default_val
    return default_val_info_dict


DOC_RETURN_INFO_KEY_NAME = 'name'
DOC_RETURN_INFO_KEY_TYPE_NAME = 'type_name'
DOC_RETURN_INFO_KEY_DESCRIPTION = 'description'


def get_docstring_return_val_info_list(docstring):
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
        - DOC_RETURN_INFO_KEY_TYPE_NAME : str -> Type name of
            return value.
        - DOC_RETURN_INFO_KEY_DESCRIPTION : str -> Description of
            the return value.
    """
    return_value_docstring = _get_return_value_docstring(
        docstring=docstring)
    if return_value_docstring == '':
        return []
    line_splitted_list = return_value_docstring.split('\n')
    name = ''
    type_name = ''
    description = ''
    return_val_info_list = []
    for line_str in line_splitted_list:
        if line_str.replace(' ', '') == '':
            continue
        line_indent_num = get_line_indent_num(line_str=line_str)
        if line_indent_num == 1 and name != '':
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
    if name != '':
        return_val_info_list = _append_return_value_info_unit_dict(
            name=name, type_name=type_name, description=description,
            return_val_info_list=return_val_info_list)
    return return_val_info_list


def _append_return_value_info_unit_dict(
        name, type_name, description, return_val_info_list):
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
    return_value_info_dict = {
        DOC_RETURN_INFO_KEY_NAME: name,
        DOC_RETURN_INFO_KEY_TYPE_NAME: type_name,
        DOC_RETURN_INFO_KEY_DESCRIPTION: description,
    }
    return_val_info_list.append(return_value_info_dict)
    return return_val_info_list


def _get_return_value_name_from_line(line_str):
    """
    Get the return value name from the target line string.

    Parameters
    ----------
    line_str : str
        Target line string. e.g., 'price : int'

    Returns
    -------
    return_value_name : str
        Return value name.
    """
    return_value_name = line_str.split(':')[0]
    return_value_name = return_value_name.strip()
    return return_value_name


def _get_return_value_type_name_from_line(line_str):
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
    colon_exists = ':' in line_str
    if not colon_exists:
        return ''
    return_value_type_name = line_str.split(':')[1]
    return_value_type_name = return_value_type_name.strip()
    return return_value_type_name


def _get_return_value_docstring(docstring):
    """
    Get the string of docstring's return value part.

    Parameters
    ----------
    docstring : str
        Target docstring string.

    Returns
    -------
    return_value_docstring : str
        String of docstring return value information.
    """
    if docstring == '':
        return ''
    start_line_idx = 0
    last_line_idx = 0
    line_splitted_list = docstring.split('\n')
    for i, line_str in enumerate(line_splitted_list):
        is_in = 'Returns' in line_str
        if not is_in:
            continue
        start_line_idx = i + 2
        break
    if start_line_idx == 0:
        return ''

    second_hyphen_exists = False
    for i, line_str in enumerate(line_splitted_list):
        if i < start_line_idx:
            continue
        last_line_idx = i
        is_hyphen_line = '----' in line_str
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
    if not docstring.startswith('    '):
        docstring = '    %s' % docstring
    return docstring


def get_func_str(module_str, func_name):
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
    line_splitted_list = module_str.split('\n')
    start_line_idx = None
    last_line_idx = None
    def_line_str = 'def %s' % func_name
    for i, line_str in enumerate(line_splitted_list):
        is_def_line_str = def_line_str in line_str
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
        line_indent_num = get_line_indent_num(
            line_str=line_str)
        if line_indent_num > func_indent_baseline_num:
            continue
        line_str = line_str.strip()
        if line_str == '':
            continue
        last_line_idx = i
        break

    func_str = '\n'.join(
        line_splitted_list[start_line_idx:last_line_idx])
    func_str = func_str.rstrip()
    return func_str


def return_val_exists_in_func(module_str, func_name):
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
    func_str = get_func_str(module_str=module_str, func_name=func_name)
    if func_str == '':
        return False
    line_splitted_list = func_str.split('\n')
    for line_str in line_splitted_list:
        return_statement_exists = 'return' in line_str
        if not return_statement_exists:
            continue
        return_val_str = re.sub(
            pattern=r'^.*return', repl='', string=line_str)
        return_val_str = return_val_str.strip()
        if return_val_str == '':
            continue
        return True
    return False
