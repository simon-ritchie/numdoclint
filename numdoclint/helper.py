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
    search_pattern = 'def %s' % func_name
    search_pattern = search_pattern + r'.*\(.*\)'
    py_module_str = re.sub(pattern=r'\n', repl='', string=py_module_str)
    searched_result_list = re.findall(
        pattern=search_pattern, string=py_module_str)
    searched_result_str = searched_result_list[0]

    args_str = searched_result_str.split('def ')[1]
    args_str = args_str.split('(')[1]
    args_str = args_str.split(')')[0]
    splited_arg_name_list = args_str.split(',')
    arg_name_list = []
    for arg_name in splited_arg_name_list:
        arg_name = arg_name.replace(' ', '')
        arg_name = arg_name.split(':')[0]
        if arg_name == '':
            continue
        arg_name_list.append(arg_name)
    return arg_name_list
