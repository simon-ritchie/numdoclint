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
