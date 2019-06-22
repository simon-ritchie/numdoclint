"""A module that checks docstrings in Python files.
"""

import os


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
    """
    _check_module_exists(py_module_path=py_module_path)
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
