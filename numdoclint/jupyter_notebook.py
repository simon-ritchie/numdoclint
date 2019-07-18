"""A module that checks docstring in Jupyter notebook.
"""

from __future__ import print_function

import json
import os

from numdoclint import helper, py_module

INFO_KEY_NOTEBOOK_PATH = 'notebook_path'
INFO_KEY_CODE_CELL_INDEX = 'code_cell_index'
INFO_KEY_FUNC_NAME = py_module.INFO_KEY_FUNC_NAME
INFO_KEY_INFO_ID = py_module.INFO_KEY_INFO_ID
INFO_KEY_INFO = py_module.INFO_KEY_INFO

VERBOSE_ENABLED = py_module.VERBOSE_ENABLED
VERBOSE_DISABLED = py_module.VERBOSE_DISABLED


def check_jupyter_notebook(
        notebook_path, verbose=1, ignore_func_name_prefix_list=['test_'],
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
    ignore_func_name_prefix_list : list of str, default ['test_']
        A prefix list of function name conditions to ignore.
    ignore_info_id_list : list of int, default []
        List of IDs to ignore lint checking. A constant with a
        prefix of `INFO_ID_` can be specified.
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
        - code_cell_index : int -> Notebook code cell index number
            (start with zero). Not include markdown cells.
        - func_name : str -> Target function name.
        - info_id : int -> Identification number of which information.
        - info : str -> Information of check result.

    Raises
    ------
    IOError
        - If the target notebook can not be found.
        - If the target notebook extension is not `ipynb`.
    """
    is_checkpoint_in = '.ipynb_checkpoints' in notebook_path
    if is_checkpoint_in:
        return []
    _check_notebook_exists(notebook_path=notebook_path)
    _check_notebook_extension(notebook_path=notebook_path)
    notebook_data_dict = _read_notebook_data_dict(
        notebook_path=notebook_path)
    code_cell_str_list = _get_code_cell_str_list(
        notebook_data_dict=notebook_data_dict)
    if not code_cell_str_list:
        return []
    info_list = []
    enable_def_or_opt_check = enable_default_or_optional_doc_check
    for i, code_cell_str in enumerate(code_cell_str_list):
        info_list_unit = _check_unit_code_cell_str(
            notebook_path=notebook_path,
            code_cell_idx=i,
            code_cell_str=code_cell_str,
            ignore_func_name_prefix_list=ignore_func_name_prefix_list,
            ignore_info_id_list=ignore_info_id_list,
            enable_default_or_optional_doc_check=enable_def_or_opt_check)
        info_list.extend(info_list_unit)
    _print_info_list(info_list=info_list, verbose=verbose)
    return info_list


def check_jupyter_notebook_recursively(
        dir_path, verbose=1, ignore_func_name_prefix_list=['test_'],
        ignore_info_id_list=[],
        enable_default_or_optional_doc_check=False):
    """
    Check docstring of Jupyter notebook recursively.

    Parameters
    ----------
    dir_path : str
        Target directory path.
    verbose : int, default 1
        Log settings of stdout. Specify one of the following numbers:
        - 0 -> Do not output log.
        - 1 -> Output the check result.
    ignore_func_name_prefix_list : list of str, default ['test_']
        A prefix list of function name conditions to ignore.
    ignore_info_id_list : list of int, default []
        List of IDs to ignore lint checking. A constant with a
        prefix of `INFO_ID_` can be specified.
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
        - code_cell_index : int -> Notebook code cell index number
            (start with zero). Not include markdown cells.
        - func_name : str -> Target function name.
        - info_id : int -> Identification number of which information.
        - info : str -> Information of check result.
    """
    enable_def_or_opt_check = enable_default_or_optional_doc_check
    info_list = _check_jupyter_notebook_recursively(
        dir_path=dir_path,
        info_list=[],
        verbose=verbose,
        ignore_func_name_prefix_list=ignore_func_name_prefix_list,
        ignore_info_id_list=ignore_info_id_list,
        enable_default_or_optional_doc_check=enable_def_or_opt_check)
    return info_list


def _check_jupyter_notebook_recursively(
        dir_path, info_list, verbose,
        ignore_func_name_prefix_list, ignore_info_id_list,
        enable_default_or_optional_doc_check):
    """
    Check docstring of Jupyter notebook recursively.

    Parameters
    ----------
    dir_path : str
        Target directory path.
    info_list : list of dicts
        A list containing information on check results.
    verbose : int
        Log settings of stdout. Specify one of the following numbers:
        - 0 -> Do not output log.
        - 1 -> Output the check result.
    ignore_func_name_prefix_list : list of str
        A prefix list of function name conditions to ignore.
    ignore_info_id_list : list of int
        List of IDs to ignore lint checking. A constant with a
        prefix of `INFO_ID_` can be specified.
    enable_default_or_optional_doc_check : bool
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
    """
    file_or_folder_name_list = os.listdir(dir_path)
    if not file_or_folder_name_list:
        return info_list
    enable_def_or_opt_check = enable_default_or_optional_doc_check
    for file_or_folder_name in file_or_folder_name_list:
        path = os.path.join(dir_path, file_or_folder_name)
        path = path.replace('\\', '/')
        if os.path.isdir(path):
            info_list = _check_jupyter_notebook_recursively(
                dir_path=path,
                info_list=info_list,
                verbose=verbose,
                ignore_func_name_prefix_list=ignore_func_name_prefix_list,
                ignore_info_id_list=ignore_info_id_list,
                enable_default_or_optional_doc_check=enable_def_or_opt_check)
            continue
        if not path.endswith('.ipynb'):
            continue
        unit_info_list = check_jupyter_notebook(
            notebook_path=path,
            verbose=verbose,
            ignore_func_name_prefix_list=ignore_func_name_prefix_list,
            ignore_info_id_list=ignore_info_id_list,
            enable_default_or_optional_doc_check=enable_def_or_opt_check)
        info_list.extend(unit_info_list)
    return info_list


def _print_info_list(info_list, verbose):
    """
    Print check result.

    Parameters
    ----------
    info_list : list of dicts
        A list containing information on check results.
        The following values are necessary in the dictionary key:
        - notebook_path : str
        - code_cell_index : int
        - func_name : str
        - info_id : int
        - info : str
    verbose : int
        Log settings of stdout.

    Returns
    -------
    printed_str : str
        Printed string.
    """
    if not info_list:
        return ''
    if verbose != VERBOSE_ENABLED:
        return ''
    printed_str = ''
    for info_dict in info_list:
        if printed_str != '':
            printed_str += '\n'
        printed_str += '{notebook_path}::code cell index:{code_cell_index}'\
            '::{func_name}\n{info}\n'.format(
                notebook_path=info_dict['notebook_path'],
                code_cell_index=info_dict['code_cell_index'],
                func_name=info_dict['func_name'],
                info=info_dict['info'])
    print(printed_str)
    return printed_str


def _check_unit_code_cell_str(
        notebook_path, code_cell_idx, code_cell_str,
        ignore_func_name_prefix_list, ignore_info_id_list,
        enable_default_or_optional_doc_check):
    """
    Check the single code cell.

    Parameters
    ----------
    notebook_path : str
        Path of target Jupyter notebook.
    code_cell_idx : int
        Index of target code cell.
    code_cell_str : str
        Code string of target cell.
    ignore_func_name_prefix_list : list of str
        A prefix list of function name conditions to ignore.
    ignore_info_id_list : list of int
        List of IDs to ignore lint checking. A constant with a
        prefix of `INFO_ID_` can be specified.
    enable_default_or_optional_doc_check : bool
        If True specified, the `default` and `optional` string
        in docstring will be checked.

    Returns
    -------
    info_list : list of dicts
        A list containing information on check results.
        The following values are set in the dictionary key:
        - notebook_path : str -> Path of target Jupyter notebook.
        - code_cell_index : int -> Notebook code cell index number
            (start with zero). Not include markdown cells.
        - func_name : str -> Target function name.
        - info_id : int -> Identification number of which information.
        - info : str -> Information of check result.
    """
    func_name_list = helper.get_func_name_list(
        code_str=code_cell_str)
    if not func_name_list:
        return []
    info_list = []
    enable_def_or_opt_check = enable_default_or_optional_doc_check
    for func_name in func_name_list:
        is_func_name_to_ignore = py_module.is_func_name_to_ignore(
            func_name=func_name,
            ignore_func_name_prefix_list=ignore_func_name_prefix_list)
        if is_func_name_to_ignore:
            continue
        single_func_info_list = py_module.get_single_func_info_list(
            path=notebook_path,
            code_str=code_cell_str,
            func_name=func_name,
            enable_default_or_optional_doc_check=enable_def_or_opt_check,
            skip_decorator_name_list=[],
            ignore_info_id_list=ignore_info_id_list)
        info_list.extend(single_func_info_list)
    info_list = _rename_dict_key(info_list=info_list)
    info_list = _add_code_cell_index(
        info_list=info_list, code_cell_idx=code_cell_idx)
    return info_list


def _add_code_cell_index(info_list, code_cell_idx):
    """
    Add cell index value to the dictionaries in the list.

    Parameters
    ----------
    info_list : list of dicts
        A list containing information on check results.
    code_cell_idx : int
        A code cell index to be set.

    Returns
    -------
    info_list : list of dicts
        A list containing a dictionary with the following
        added key.
        - code_cell_index : int
    """
    for info_dict in info_list:
        info_dict[INFO_KEY_CODE_CELL_INDEX] = code_cell_idx
    return info_list


def _rename_dict_key(info_list):
    """
    Rename dictionary key names in the list.

    Parameters
    ----------
    info_list : list of dict
        A list of check results. The following keys are necessary
        in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str

    Returns
    -------
    info_list : list of dicts
        A list containing the renamed dictionary.
        The following keys will be set.
        - notebook_path : str
        - func_name : str
        - info_id : int
        - info : str
    """
    for info_dict in info_list:
        path_str = info_dict[py_module.INFO_KEY_MODULE_PATH]
        info_dict[INFO_KEY_NOTEBOOK_PATH] = path_str
        del info_dict[py_module.INFO_KEY_MODULE_PATH]
    return info_list


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
