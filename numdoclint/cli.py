"""Module for command line interface.
"""

import argparse

import numdoclint


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
    print('path:', args.path)
    print('is_jupyter:', args.is_jupyter)
    print('ignore_func_name_suffix_list:', args.ignore_func_name_suffix_list)
    print('ignore_info_id_list:', args.ignore_info_id_list)
    print(
        'enable_default_or_optional_doc_check:',
        args.enable_default_or_optional_doc_check)
    print('skip_decorator_name_list:', args.skip_decorator_name_list)
