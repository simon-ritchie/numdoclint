"""A module that checks docstring in Jupyter notebook.
"""

from __future__ import print_function
import os
import json

from numdoclint import helper
from numdoclint import py_module


def check_jupyter_notebook(
        notebook_path, verbose=1, ignore_func_name_suffix_list=['test_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False):
    """
    Check docstring of single Jupyter notebook.

    Parameters
    ----------
    notebook_path : str
        Path of target Jupyter notebook.
    verbose : int, default 1
        Log settings of stdout. Specify one of the following numbers:
        - 0 -> Do not output log.
        - 1 -> Output the check result.
    ignore_func_name_suffix_list : list of str, default ['test_']
        A suffix list of function name conditions to ignore.
    ignore_info_id_list : list of int, default []
        List of IDs to ignore lint checking. A constant with a
        suffix of `INFO_ID_` can be specified.
    enable_default_or_optional_doc_check : bool, default False
        If True specified, the `default` and `optional` string
        in docstring will be checked.
        i.e., if there is an argument containing a default value,
        docstring's argument needs to describe default or optional.
        e.g., `price : int, default is 100`, `price : int, default 100`,
        `price : int, optional`.

    Returns
    -------
    info_list : list of dicts
        A list containing information on check results.
        The following values are set in the dictionary key:
        - notebook_path : str -> Path of target Jupyter notebook.
        - cell_index : int -> Notebook cell index number
            (start with zero).
        - func_name : str -> Target function name.
        - info : str -> Information of check result.

    Raises
    ------
    IOError
        - If the target notebook can not be found.
        - If the target notebook extension is not `ipynb`.
    """
    _check_notebook_exists(notebook_path=notebook_path)
    _check_notebook_extension(notebook_path=notebook_path)
    notebook_data_dict = _read_notebook_data_dict(
        notebook_path=notebook_path)
    code_cell_str_list = _get_code_cell_str_list(
        notebook_data_dict=notebook_data_dict)
    pass


def _get_code_cell_str_list(notebook_data_dict):
    """
    Get a list of code cell strings.

    Parameters
    ----------
    notebook_data_dict : dict
        A dictionary of notebook data.

    Returns
    -------
    code_str_list : list of str
        A list of code cell strings.
    """
    code_str_list = []
    has_key = 'cells' in notebook_data_dict
    if not has_key:
        return []
    cells_list = notebook_data_dict['cells']
    for cell_dict in cells_list:
        cell_type = cell_dict['cell_type']
        if cell_type != 'code':
            continue
        source_list = cell_dict['source']
        source = ''.join(source_list)
        code_str_list.append(source)
    return code_str_list


def _read_notebook_data_dict(notebook_path):
    """
    Read a dictionary of notebook data.

    Parameters
    ----------
    notebook_path : str
        Path of target notebook.

    Returns
    -------
    notebook_data_dict : dict
        A dictionary of notebook data.
    """
    with open(notebook_path, 'r') as f:
        notebook_data_str = f.read()
    notebook_data_dict = json.loads(notebook_data_str)
    return notebook_data_dict


def _check_notebook_extension(notebook_path):
    """
    Check the path extension of the notebook.

    Parameters
    ----------
    notebook_path : str
        Path of target notebook.

    Raises
    ------
    IOError
        If the extension is invalid.
    """
    extension_str = notebook_path.split('.')[-1]
    if extension_str.endswith('ipynb'):
        return
    err_msg = 'The extension is invalid. Please Specify a path of '\
              '`.ipynb` extension.'
    raise IOError(err_msg)


def _check_notebook_exists(notebook_path):
    """
    Check that the target Jupyter notebook exists.

    Parameters
    ----------
    notebook_path : str
        Path of target notebook.

    Raises
    ------
    IOError
        If the target module can not be found.
    """
    if os.path.exists(notebook_path):
        return
    err_msg = 'The target notebook could not be found.'
    err_msg += '\nNotebook path: %s' % notebook_path
    raise IOError(err_msg)
