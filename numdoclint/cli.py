"""Module for command line interface.
"""

import os
import argparse

import numdoclint
from numdoclint import py_module


def _get_list_of_str_from_csv(csv):
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


def _validate_args(path, ignore_info_id_list, check_recursively):
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
        err_msg = 'A path is not specified in the argument.'\
                  'Please set the `-p` or `--path` argument.'
        raise Exception(err_msg)
    info_id_list = py_module.get_info_id_list()
    for ignore_info_id in ignore_info_id_list:
        is_in = ignore_info_id in info_id_list
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


def _get_list_of_int_from_csv(csv):
    """
    Get a list of integer from one line CSV.

    Parameters
    ----------
    csv : str
        One line CSV string.

    Returns
    -------
    result_list : list of str
        List of splitted integer.
    """
    if csv == '':
        return []
    ignore_info_id_list = csv.split(',')
    for i, info_id in enumerate(ignore_info_id_list):
        ignore_info_id_list[i] = int(info_id)
    return ignore_info_id_list


def main():
    """The function of command line entry point.
    """
    description = 'NumPy style docstring checking in Python code.'
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        '-p', '--path', type=str,
        help='Python module file path, Jupyter notebook path, '
             'or directory path.')
    parser.add_argument(
        '-r', '--check_recursively',
        action='store_true',
        help='If specified, check files recursively.'
             'In that case, you need to specify the directory '
             'in the path argument.')
    parser.add_argument(
        '-j', '--is_jupyter',
        action='store_true',
        help='If specified, check target will become jupyter notebook. '
             'If not, Python module will be checked.')
    parser.add_argument(
        '-f', '--ignore_func_name_suffix_list',
        type=_get_list_of_str_from_csv,
        default='',
        help='A suffix list of function name conditions to ignore.'
             '\ne.g., test_,sample_'
             '\nComma separated string is acceptable.')
    parser.add_argument(
        '-i', '--ignore_info_id_list',
        type=_get_list_of_int_from_csv,
        default='',
        help='List of IDs to ignore lint checking.'
             '\ne.g, 1,2,3'
             '\nComma separated integer is acceptable.')
    parser.add_argument(
        '-o', '--enable_default_or_optional_doc_check',
        action='store_true',
        help='If specified, the `default` and `optional` string'
             'in docstring will be checked.')
    parser.add_argument(
        '-d', '--skip_decorator_name_list',
        type=_get_list_of_str_from_csv,
        default='',
        help='If a decorator name in this list is set to function, '
             'that function will not be checked. Specify if '
             'necessary for docstring-related decorators.')

    args = parser.parse_args()
    print('type:', type(args))
    print('path:', args.path)
    print('is_jupyter:', args.is_jupyter)
    print('ignore_func_name_suffix_list:', args.ignore_func_name_suffix_list)
    print('ignore_info_id_list:', args.ignore_info_id_list)
    print(
        'enable_default_or_optional_doc_check:',
        args.enable_default_or_optional_doc_check)
    print('skip_decorator_name_list:', args.skip_decorator_name_list)

    _validate_args(
        path=args.path,
        ignore_info_id_list=args.ignore_info_id_list,
        check_recursively=args.check_recursively)
