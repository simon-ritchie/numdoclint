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
    return info_list


def check_python_module_recursively(dir_path):
    """
    Check Python module docstring recursively.

    Parameters
    ----------
    dir_path : str
        Target directory path.

    Returns
    -------
    info_list : list of dicts
        A list containing information on check results.
        The following values are set in the dictionary key:
        - module_path : str -> Path of target module.
        - func_name : str -> Target function name.
        - info_id : int -> Identification number of which information.
        - info : str -> Information of check result.
    """
    info_list = _check_python_module_recursively(
        dir_path=dir_path, info_list=[])
    return info_list


def _check_python_module_recursively(dir_path, info_list):
    """
    Check Python module docstring recursively.

    Parameters
    ----------
    dir_path : str
        Target directory path.
    info_list : list of dicts
        List to add check results to.

    Returns
    -------
    info_list : list of dicts
        A list containing information on check results.
        The following values are set in the dictionary key:
        - module_path : str -> Path of target module.
        - func_name : str -> Target function name.
        - info_id : int -> Identification number of which information.
        - info : str -> Information of check result.
    """
    file_or_folder_name_list = os.listdir(dir_path)
    if not file_or_folder_name_list:
        return info_list
    for file_or_folder_name in file_or_folder_name_list:
        path = os.path.join(dir_path, file_or_folder_name)
        path = path.replace('\\', '/')
        if os.path.isdir(path):
            info_list = _check_python_module_recursively(
                dir_path=path, info_list=info_list)
            continue
        if not path.endswith('.py'):
            continue
        unit_info_list = check_python_module(
            py_module_path=path)
        info_list.extend(unit_info_list)
    return info_list


INFO_ID_LACKED_ARGUMENT = 1
INFO_ID_LACKED_DOCSTRING_PARAM = 2
INFO_ID_LACKED_DOCSTRING_PARAM_TYPE = 3
INFO_ID_LACKED_DOCSTRING_PARAM_DESCRIPTION = 4
INFO_ID_DIFFERENT_PARAM_ORDER = 5
INFO_ID_LACKED_FUNC_DESCRIPTION = 6
INFO_ID_LACKED_ARG_DEFAULT_VALUE = 7
INFO_ID_LACKED_DOC_DEFAULT_VALUE = 8
INFO_ID_LACKED_DOCSTRING_RETURN = 9
INFO_ID_LACKED_DOCSTRING_RETURN_TYPE = 10
INFO_ID_LACKED_DOCSTRING_RETURN_DESCRIPTION = 11
INFO_ID_LACKED_RETURN_VAL = 12

INFO_KEY_MODULE_PATH = 'module_path'
INFO_KEY_FUNC_NAME = 'func_name'
INFO_KEY_INFO_ID = 'info_id'
INFO_KEY_INFO = 'info'


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
    docstring = helper.get_func_overall_docstring(
        py_module_str=module_str, func_name=func_name)
    arg_name_list = helper.get_arg_name_list(
        py_module_str=module_str, func_name=func_name)
    default_val_info_dict = helper.get_arg_default_val_info_dict(
        py_module_str=module_str, func_name=func_name)
    param_info_list = helper.get_docstring_param_info_list(
        docstring=docstring)
    return_val_info_list = helper.get_docstring_return_val_info_list(
        docstring=docstring)
    return_val_exists_in_func = helper.return_val_exists_in_func(
        module_str=module_str, func_name=func_name)

    unit_info_list = _check_func_description(
        module_path=module_path, func_name=func_name,
        docstring=docstring)
    info_list.extend(unit_info_list)

    unit_info_list = _check_lacked_param(
        module_path=module_path, func_name=func_name,
        arg_name_list=arg_name_list, param_info_list=param_info_list)
    info_list.extend(unit_info_list)

    unit_info_list = _check_lacked_docstring_param_type(
        module_path=module_path, func_name=func_name,
        param_info_list=param_info_list)
    info_list.extend(unit_info_list)

    unit_info_list = _check_lacked_docstring_param_description(
        module_path=module_path, func_name=func_name,
        param_info_list=param_info_list)
    info_list.extend(unit_info_list)

    unit_info_list = _check_docstring_param_order(
        module_path=module_path, func_name=func_name,
        arg_name_list=arg_name_list, param_info_list=param_info_list)
    info_list.extend(unit_info_list)

    unit_info_list = _check_lacked_default_value(
        module_path=module_path, func_name=func_name,
        param_info_list=param_info_list,
        default_val_info_dict=default_val_info_dict)
    info_list.extend(unit_info_list)

    unit_info_list = _check_lacked_return(
        module_path=module_path, func_name=func_name,
        return_val_info_list=return_val_info_list,
        return_val_exists_in_func=return_val_exists_in_func)
    info_list.extend(unit_info_list)

    unit_info_list = _check_lacked_return_docstring_type(
        module_path=module_path, func_name=func_name,
        return_val_info_list=return_val_info_list)
    info_list.extend(unit_info_list)

    unit_info_list = _check_lacked_return_docstring_description(
        module_path=module_path, func_name=func_name,
        return_val_info_list=return_val_info_list)
    info_list.extend(unit_info_list)

    return info_list


def _check_lacked_return_docstring_description(
        module_path, func_name, return_val_info_list):
    """
    Check if the docstring description for the return value is lacked.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    return_val_info_list : list of dicts
        List containing return value information.
        Values are set in the dictionary with the following keys.
        - helper.DOC_RETURN_INFO_KEY_NAME : str -> Return value name.
        - helper.DOC_RETURN_INFO_KEY_TYPE_NAME : str -> Type name of
            return value.
        - helper.DOC_RETURN_INFO_KEY_DESCRIPTION : str ->
            Description of the return value.

    Returns
    ----------
    info_list : list
        A list of check results for one function.
        The following keys are set in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str
    """
    if not return_val_info_list:
        return []
    info_list = []
    for return_val_info_dict in return_val_info_list:
        name = return_val_info_dict[helper.DOC_RETURN_INFO_KEY_NAME]
        description = return_val_info_dict[
            helper.DOC_RETURN_INFO_KEY_DESCRIPTION]
        if description != '':
            continue
        info = 'Docstring description of return value is missing.'
        info += '\nReturn value name: %s' % name
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_LACKED_DOCSTRING_RETURN_DESCRIPTION,
            info=info)
        info_list.append(info_dict)
    return info_list


def _check_lacked_docstring_param_description(
        module_path, func_name, param_info_list):
    """
    Check that the docstring argument description is not lacked.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    param_info_list : list of dicts
        A list containing argument information of docstring.
        The dictionary needs a key with the following constants:
        - helper.DOC_PARAM_INFO_KEY_ARG_NAME : str
        - helper.DOC_PARAM_INFO_KEY_TYPE_NAME : str
        - helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL : str
        - helper.DOC_PARAM_INFO_KEY_DESCRIPTION : str

    Returns
    -------
    info_list : list
        A list of check results for one function.
        The following keys are set in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str
    """
    if not param_info_list:
        return []

    info_list = []
    for param_info_dict in param_info_list:
        arg_name = param_info_dict[helper.DOC_PARAM_INFO_KEY_ARG_NAME]
        description = param_info_dict[
            helper.DOC_PARAM_INFO_KEY_DESCRIPTION]
        if description != '':
            continue
        info = 'Missing docstring argument information.'
        info += '\nArgument name: %s' % arg_name
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_LACKED_DOCSTRING_PARAM_DESCRIPTION,
            info=info)
        info_list.append(info_dict)
    return info_list


def _check_lacked_return_docstring_type(
        module_path, func_name, return_val_info_list):
    """
    Check that the type specification is not lacked in the
    return value's docstring.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    return_val_info_list : list of dicts
        List containing return value information.
        Values are set in the dictionary with the following keys.
        - helper.DOC_RETURN_INFO_KEY_NAME : str -> Return value name.
        - helper.DOC_RETURN_INFO_KEY_TYPE_NAME : str -> Type name of
            return value.
        - helper.DOC_RETURN_INFO_KEY_DESCRIPTION : str ->
            Description of the return value.

    Returns
    -------
    info_list : list
        A list of check results for one function.
        The following keys are set in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str
    """
    if not return_val_info_list:
        return []
    info_list = []
    for return_val_info_dict in return_val_info_list:
        return_value_name = return_val_info_dict[
            helper.DOC_RETURN_INFO_KEY_NAME]
        type_name = return_val_info_dict[
            helper.DOC_RETURN_INFO_KEY_TYPE_NAME]
        if type_name != '':
            continue
        info = 'Missing docstring type information.'
        info += 'Return value name: %s' % return_value_name
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_LACKED_DOCSTRING_RETURN_TYPE,
            info=info)
        info_list.append(info_dict)
    return info_list


def _check_lacked_return(
        module_path, func_name, return_val_info_list,
        return_val_exists_in_func):
    """
    Check if the return value or docstring is lacked.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    return_val_info_list : list of dicts
        List containing return value information.
        Values are set in the dictionary with the following keys.
        - helper.DOC_RETURN_INFO_KEY_NAME : str -> Return value name.
        - helper.DOC_RETURN_INFO_KEY_TYPE_NAME : str -> Type name of
            return value.
        - helper.DOC_RETURN_INFO_KEY_DESCRIPTION : str ->
            Description of the return value.
    return_val_exists_in_func : bool
        Boolean value whether the return value exists in the function.

    Returns
    -------
    info_list : list
        A list of check results for one function.
        The following keys are set in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str
    """
    if not return_val_exists_in_func and not return_val_info_list:
        return []

    if return_val_exists_in_func and return_val_info_list:
        return []

    if return_val_exists_in_func and not return_val_info_list:
        info = 'While the return value exists in the function, the return value document does not exist in docstring.'
        info_dict = _make_info_dict(
            module_path=module_path, func_name=func_name,
            info_id=INFO_ID_LACKED_DOCSTRING_RETURN,
            info=info)
        return [info_dict]

    if not return_val_exists_in_func and return_val_info_list:
        info = 'While the return value document exists in docstring, the return value does not exist in the function.'
        info_dict = _make_info_dict(
            module_path=module_path, func_name=func_name,
            info_id=INFO_ID_LACKED_RETURN_VAL,
            info=info)
        return [info_dict]

    return []


def _check_lacked_default_value(
        module_path, func_name, param_info_list, default_val_info_dict):
    """
    Check that the default value of the argument is not missing.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    param_info_list : list of dicts
        A list containing argument information of docstring.
        The dictionary needs a key with the following constants:
        - helper.DOC_PARAM_INFO_KEY_ARG_NAME : str
        - helper.DOC_PARAM_INFO_KEY_TYPE_NAME : str
        - helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL : str
        - helper.DOC_PARAM_INFO_KEY_DESCRIPTION : str
    default_val_info_dict : dict
        A dctionary that stores argument names in keys and default
        values in values.

    Returns
    -------
    info_list : list
        A list of check results for one function.
        The following keys are set in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str
    """
    info_list = []
    for param_info_dict in param_info_list:
        param_info_arg_name = param_info_dict[
            helper.DOC_PARAM_INFO_KEY_ARG_NAME]
        param_info_default_val = param_info_dict[
            helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL]
        has_key = param_info_arg_name in default_val_info_dict
        if not has_key:
            continue

        if param_info_default_val == '':
            if default_val_info_dict[param_info_arg_name] == '':
                continue
            info = 'While there is no description of default value in docstring, there is a default value on the argument side.'
            info += '\nArgument name: %s' % param_info_arg_name
            info += '\nArgument default value: %s' \
                % default_val_info_dict[param_info_arg_name]
            info_dict = _make_info_dict(
                module_path=module_path,
                func_name=func_name,
                info_id=INFO_ID_LACKED_DOC_DEFAULT_VALUE,
                info=info)
            info_list.append(info_dict)
            continue

        if default_val_info_dict[param_info_arg_name] != '':
            continue
        info = 'The default value described in docstring does not exist in the actual argument.'
        info += '\nArgment name: %s' % param_info_arg_name
        info += '\nDocstring default value: %s' % param_info_default_val
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_LACKED_ARG_DEFAULT_VALUE,
            info=info)
        info_list.append(info_dict)
    return info_list


def _check_func_description(module_path, func_name, docstring):
    """
    Check that the target docstring has a function description.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    docstring : str
        Docstring to be checked.

    Returns
    -------
    info_list : list of dict
        A list of check results for one function.
        The following keys are set in the dictionary:
        - module_path : str
        - func_name : str
        - info_id : int
        - info : str

    Notes
    -----
    Test function will not be checked.
    """
    if func_name.startswith('test_'):
        return []
    func_description = helper.get_func_description_from_docstring(
        docstring=docstring)
    if func_description != '':
        return []
    info = 'The function description is not set to docstring.'
    info_dict = _make_info_dict(
        module_path=module_path,
        func_name=func_name,
        info_id=INFO_ID_LACKED_FUNC_DESCRIPTION,
        info=info)
    return [info_dict]


def _check_docstring_param_order(
        module_path, func_name, arg_name_list, param_info_list):
    """
    Check that the order of arguments and docstring is the same.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    arg_name_list : list of str
        List of argument names.
    param_info_list : list of dicts
        A list containing argument information of docstring.
        The dictionary needs a key with the following constants:
        - helper.DOC_PARAM_INFO_KEY_ARG_NAME : str
        - helper.DOC_PARAM_INFO_KEY_TYPE_NAME : str
        - helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL : str
        - helper.DOC_PARAM_INFO_KEY_DESCRIPTION : str

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
    if len(arg_name_list) != len(param_info_list):
        return []
    param_info_arg_name_list = [
        param_info_dict[helper.DOC_PARAM_INFO_KEY_ARG_NAME]
            for param_info_dict in param_info_list]
    info_list = []
    for i, arg_name in enumerate(arg_name_list):
        param_info_arg_name = param_info_arg_name_list[i]
        if arg_name == param_info_arg_name:
            continue
        info = 'The order of the argument and docstring is different.'
        info += '\nOrder of arguments: %s' % arg_name_list
        info += '\nOrder of docstring parameters: %s' \
            % param_info_arg_name_list
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_DIFFERENT_PARAM_ORDER,
            info=info)
        info_list.append(info_dict)
        break
    return info_list


def _check_lacked_docstring_param_type(
        module_path, func_name, param_info_list):
    """
    Check that the docstring argument type is not lacked.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    param_info_list : list of dicts
        A list containing argument information of docstring.
        The dictionary needs a key with the following constants:
        - helper.DOC_PARAM_INFO_KEY_ARG_NAME : str
        - helper.DOC_PARAM_INFO_KEY_TYPE_NAME : str
        - helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL : str
        - helper.DOC_PARAM_INFO_KEY_DESCRIPTION : str

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
    for param_info_dict in param_info_list:
        arg_name = param_info_dict[helper.DOC_PARAM_INFO_KEY_ARG_NAME]
        type_name = param_info_dict[helper.DOC_PARAM_INFO_KEY_TYPE_NAME]
        if type_name != '':
            continue
        info = 'Missing docstring argument type information.'
        info = '\nTarget argument: %s' % arg_name
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_LACKED_DOCSTRING_PARAM_TYPE,
            info=info)
        info_list.append(info_dict)
    return info_list


def _check_lacked_param(
        module_path, func_name, arg_name_list, param_info_list):
    """
    Check for missing arguments between arguments and docstring.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    arg_name_list : list of str
        List of argument names.
    param_info_list : list of dicts
        A list containing argument information of docstring.
        The dictionary needs a key with the following constants:
        - helper.DOC_PARAM_INFO_KEY_ARG_NAME : str
        - helper.DOC_PARAM_INFO_KEY_TYPE_NAME : str
        - helper.DOC_PARAM_INFO_KEY_DEFAULT_VAL : str
        - helper.DOC_PARAM_INFO_KEY_DESCRIPTION : str

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
    for param_info_dict in param_info_list:
        param_arg_name = param_info_dict[
            helper.DOC_PARAM_INFO_KEY_ARG_NAME]
        is_in = param_arg_name in arg_name_list
        if is_in:
            continue
        info = 'An argument exists in docstring does not exists in the actual argument.'
        info += '\nLacked argument name: %s' % param_arg_name
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_LACKED_ARGUMENT,
            info=info,
        )
        info_list.append(info_dict)

    param_info_arg_name_list = \
        [param_dict[helper.DOC_PARAM_INFO_KEY_ARG_NAME]
            for param_dict in param_info_list]
    for arg_name in arg_name_list:
        is_in = arg_name in param_info_arg_name_list
        if is_in:
            continue
        info = 'There is an argument whose explanation does not exist in docstring.'
        info += '\nTarget argument name: %s' % arg_name
        info_dict = _make_info_dict(
            module_path=module_path,
            func_name=func_name,
            info_id=INFO_ID_LACKED_DOCSTRING_PARAM,
            info=info)
        info_list.append(info_dict)

    return info_list


def _make_info_dict(module_path, func_name, info_id, info):
    """
    Make a dictionaly of check result information.

    Parameters
    ----------
    module_path : str
        Path of target module.
    func_name : str
        Target function name.
    info_id : int
        The Id of the information defined by the constants in
        this module.
    info : str
        Information of check result.

    Returns
    -------
    info_dict : dict
        Dictionary with check results information. The keys with
        the following constants will be set.
        - INFO_KEY_MODULE_PATH : str
        - INFO_KEY_FUNC_NAME : str
        - INFO_KEY_INFO_ID : int
        - INFO_KEY_INFO : str
    """
    info_dict = {
        INFO_KEY_MODULE_PATH: module_path,
        INFO_KEY_FUNC_NAME: func_name,
        INFO_KEY_INFO_ID: info_id,
        INFO_KEY_INFO: info,
    }
    return info_dict


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
