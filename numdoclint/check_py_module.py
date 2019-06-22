"""A module that checks docstrings in Python files.
"""

import os

from numdoclint import helper


def check_python_module(py_module_path):
    """
    Check docstring of single Python module.

    Parameters
    ----------
    py_module_path : str
        Path of target module.

    Notes
    -----
    If all checks pass, an empty list will be returned.

    Returns
    -------
    info_list : list of dicts
        A list containing information on check results.
        The following values are set in the dictionary key:
        - module_path : str -> Path of target module.
        - func_name : str -> Target function name.
        - info_id : int -> Identification number of which information.
        - info : str -> Information of check result.

    Raises
    ------
    FileNotFoundError
        If the target module can not be found.

    Notes
    ------
    - Currently, if there are multiple functions with the same name
        in the module, only the first function will be checked.
    """
    _check_module_exists(py_module_path=py_module_path)
    module_str = helper.read_file_str(file_path=py_module_path)
    func_name_list = helper.get_func_name_list(py_module_str=module_str)
    if not func_name_list:
        return []
    info_list = []
    for func_name in func_name_list:
        single_func_info_list = _get_single_func_info_list(
            module_path=py_module_path,
            module_str=module_str,
            func_name=func_name,
        )
        info_list.extend(single_func_info_list)
        pass
    pass


def _get_single_func_info_list(module_path, module_str, func_name):
    """
    Get a list that stores the check result information for
    one function.

    Parameters
    ----------
    module_path : str
        Path of target module.
    module_str : str
        String of target Python module.
    func_name : str
        Target function name.

    Returns
    -------
    info_list : list of dict
        A list of check results for one function.
        The following keys are set in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str
    """
    info_list = []
    arg_name_list = helper.get_arg_name_list(
        py_module_str=module_str, func_name=func_name)
    pass


def _check_module_exists(py_module_path):
    """
    Check that the target module exists.

    Parameters
    ----------
    py_module_path : str
        Path of target module.

    Raises
    ------
    FileNotFoundError
        If the target module can not be found.
    """
    if os.path.exists(py_module_path):
        return
    err_msg = 'The target module could not be found.'
    err_msg += '\npy_module_path: %s' % py_module_path
    raise FileNotFoundError(err_msg)
