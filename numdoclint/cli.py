"""Module for command line interface.
"""

import argparse
import os
from typing import List, Optional

import numdoclint
from numdoclint import py_module


def _get_list_of_str_from_csv(csv: str) -> List[str]:
    """
    Get a list of strings from one line CSV.

    Parameters
    ----------
    csv : str
        One line CSV string.

    Returns
    -------
    result_list : list of str
        List of splitted string.
    """
    if csv == '':
        return []
    return csv.split(',')


def _validate_args(
        path: str, ignore_info_id_list: List[int],
        check_recursively: bool) -> None:
    """
    Check whether the specified argument is valid or not.

    Parameters
    ----------
    path : str
        Specified path argument.
    ignore_info_id_list : list of int
        List of specified information IDs to ignore.
    check_recursively : bool
        A boolean value of whether to check recursively.

    Raises
    ------
    Exception
        - If the path argument is None.
        - If specified invalid information id.
        - If specified `-r` and a path is not directory.
    """
    if path is None:
        err_msg: str = 'A path is not specified in the argument. '\
            'Please set the `-p` or `--path` argument.'
        raise Exception(err_msg)
    info_id_list = py_module.get_info_id_list()
    for ignore_info_id in ignore_info_id_list:
        is_in: bool = ignore_info_id in info_id_list
        if is_in:
            continue
        err_msg = 'Invalid information id is specified to '\
            '`-i` or `--ignore_info_id_list` argument : %s' \
            % ignore_info_id
        raise Exception(err_msg)
    if check_recursively:
        if not os.path.isdir(path):
            err_msg = 'If the `-r` or `--check_recursively`'\
                ' argument is specified, the path argument'\
                ' must specify a directory.'
            raise Exception(err_msg)


def _get_list_of_int_from_csv(csv: str) -> List[int]:
    """
    Get a list of integer from one line CSV.

    Parameters
    ----------
    csv : str
        One line CSV string.

    Returns
    -------
    result_list : list of int
        List of splitted integer.
    """
    if csv == '':
        return []
    ignore_info_id_list: List[str] = csv.split(',')
    result_list: List[int] = []
    for info_id in ignore_info_id_list:
        result_list.append(int(info_id))
    return result_list


def _exec_numdoclint(
        path: str,
        check_recursively: bool,
        is_jupyter: bool,
        ignore_func_name_prefix_list: List[str],
        ignore_info_id_list: List[int],
        enable_default_or_optional_doc_check: bool,
        skip_decorator_name_list: List[str]) -> List[dict]:
    """
    Execute Numdoc Lint function.

    Parameters
    ----------
    path : str
        Python module file path, Jupyter notebook path, or
        directory path.
    check_recursively : bool
        If True, check files recursively.
    is_jupyter : bool
        If True, check target will become Jupyter notebook.
        If not, Python module will be checked.
    ignore_func_name_prefix_list : list of str
        A prefix list of function name conditions to ignore.
    ignore_info_id_list : list of int
        List of IDs to ignore lint checking.
    enable_default_or_optional_doc_check : bool
        If True, the `default` and `optional` string in
        docstring will be checked.
    skip_decorator_name_list : list of str
        If a decorator name in this list is set to function,
        that function will not bo checked.

    Returns
    -------
    info_list : list of dicts
        List of check results.
    """
    enable_def_or_opt_check: bool = enable_default_or_optional_doc_check
    if not is_jupyter:
        if not check_recursively:
            info_list: List[dict] = numdoclint.check_python_module(
                py_module_path=path,
                ignore_func_name_prefix_list=ignore_func_name_prefix_list,
                ignore_info_id_list=ignore_info_id_list,
                enable_default_or_optional_doc_check=enable_def_or_opt_check,
                skip_decorator_name_list=skip_decorator_name_list)
            return info_list
        info_list = numdoclint.check_python_module_recursively(
            dir_path=path,
            ignore_func_name_prefix_list=ignore_func_name_prefix_list,
            ignore_info_id_list=ignore_info_id_list,
            enable_default_or_optional_doc_check=enable_def_or_opt_check,
            skip_decorator_name_list=skip_decorator_name_list)
        return info_list

    if not check_recursively:
        info_list = numdoclint.check_jupyter_notebook(
            notebook_path=path,
            ignore_func_name_prefix_list=ignore_func_name_prefix_list,
            ignore_info_id_list=ignore_info_id_list,
            enable_default_or_optional_doc_check=enable_def_or_opt_check)
        return info_list
    info_list = numdoclint.check_jupyter_notebook_recursively(
        dir_path=path,
        ignore_func_name_prefix_list=ignore_func_name_prefix_list,
        ignore_info_id_list=ignore_info_id_list,
        enable_default_or_optional_doc_check=enable_def_or_opt_check)
    return info_list


def main(
        args: Optional[argparse.Namespace] = None,
        return_list: bool = False) -> List[dict]:
    """
    The function of command line entry point.

    Parameters
    ----------
    args : argparse.Namespace or None, default None
        Object that stores data of argument. Specify `None`
        when not testing.
    return_list : bool, default False
        Whether to return list value. Specify `False`
        except when testing.

    Returns
    -------
    info_list : list of dicts
        List of check results.
    """
    description: str = 'NumPy style docstring checking in Python code.'
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description=description)

    parser.add_argument(
        '-p', '--path', type=str,
        help='Python module file path, Jupyter notebook path, '
             'or directory path.')
    parser.add_argument(
        '-r', '--check_recursively',
        action='store_true',
        help='If specified, check files recursively. '
             'In that case, you need to specify the directory '
             'in the path argument.')
    parser.add_argument(
        '-j', '--is_jupyter',
        action='store_true',
        help='If specified, check target will become Jupyter notebook. '
             'If not, Python module will be checked.')
    parser.add_argument(
        '-f', '--ignore_func_name_prefix_list',
        type=_get_list_of_str_from_csv,
        default='',
        help='A prefix list of function name conditions to ignore.'
             '\ne.g., test_,sample_.'
             '\nComma separated string is acceptable.')
    parser.add_argument(
        '-i', '--ignore_info_id_list',
        type=_get_list_of_int_from_csv,
        default='',
        help='List of IDs to ignore lint checking.'
             '\ne.g, 1,2,3.'
             '\nComma separated integer is acceptable.')
    parser.add_argument(
        '-o', '--enable_default_or_optional_doc_check',
        action='store_true',
        help='If specified, the `default` and `optional` string '
             'in docstring will be checked.')
    parser.add_argument(
        '-d', '--skip_decorator_name_list',
        type=_get_list_of_str_from_csv,
        default='',
        help='If a decorator name in this list is set to function, '
             'that function will not be checked. Specify if '
             'necessary for docstring-related decorators. '
             'Note: only available when check Python module, '
             'not supported Jupyter notebook.')

    if args is None:
        args = parser.parse_args()

    _validate_args(
        path=args.path,
        ignore_info_id_list=args.ignore_info_id_list,
        check_recursively=args.check_recursively)

    enable_def_or_opt_check: bool = args.enable_default_or_optional_doc_check
    info_list: List[dict] = _exec_numdoclint(
        path=args.path,
        check_recursively=args.check_recursively,
        is_jupyter=args.is_jupyter,
        ignore_func_name_prefix_list=args.ignore_func_name_prefix_list,
        ignore_info_id_list=args.ignore_info_id_list,
        enable_default_or_optional_doc_check=enable_def_or_opt_check,
        skip_decorator_name_list=args.skip_decorator_name_list,
    )
    return info_list
