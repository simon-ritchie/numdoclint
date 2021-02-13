# Numdoc Lint

Numdoc Lint provides features such as NumPy style docstring checking in Python code.

# What is NumPy-style docstring?

Descriptions of Python functions, modules, or classes written in the following format.

```py
def sample_func(sample_arg_1, sample_arg_2=100, sample_arg_3='Apple'):
    """
    Sample function description.

    Parameters
    ----------
    sample_arg_1 : int
        First sample argument description.
    sample_arg_2 : int, default 100
        Second sample argument description.
    sample_arg_3 : str, default 'Apple'
        Third sample argument description.

    Returns
    ----------
    sample_return_value : int
        Sample return value.
    """
    return 100
```

For more details, please see [A Guide to NumPy/SciPy Documentation](https://docs.scipy.org/doc/numpy/docs/howto_document.html).

# Main features

- Check lacked docstring description.
- Check arguments and docstring `Parameters` section mismatching.
    - Also will be checked argument default value and docstring optionally.
- Check arguments order.
- Check return value and docstring `Returns` section mismatching.
- Check Jupyter notebook's docstring also.

# Dependencies

## Python version

- Python 3.6 or later.

## Libraries

- six

# Installing

```
$ pip install numdoclint
```

# Examples

## Python interface

### Check single module

A single module will be checked with the `check_python_module` function.

```py
>>> import numdoclint
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='../pandas/pandas/core/arrays/array_.py')
```

Then Lint results will be displayed on standard output, as followed:

```
../pandas/pandas/core/arrays/array_.py::array
The function description is not set to docstring.

../pandas/pandas/core/arrays/array_.py::array
There is an argument whose explanation does not exist in docstring.
Target argument name: data

...
```

List of dicts will be returned, as followed:

```py
>>> lint_info_list

[{'module_path': '../pandas/pandas/core/arrays/array_.py',
  'func_name': 'array',
  'info_id': 6,
  'info': 'The function description is not set to docstring.'},
 {'module_path': '../pandas/pandas/core/arrays/array_.py',
  'func_name': 'array',
  'info_id': 2,
  'info': 'There is an argument whose explanation does not exist in docstring.\nTarget argument name: data'},
...
```

### Check modules recursively

If execute `check_python_module_recursively` function, then Numdoc Lint will check target directory recursively.

```py
>>> import numdoclint

>>> lint_info_list = numdoclint.check_python_module_recursively(
...     dir_path='../numpy/')
```

```py
>>> import pandas as pd
>>> df = pd.DataFrame(data=lint_info_list)
>>> df.head(n=3)
```

<table border="1" class="dataframe"><thead><tr style="text-align: right;"><th></th><th>func_name</th><th>info</th><th>info_id</th><th>module_path</th></tr></thead><tbody><tr><th>0</th><td>setup</td><td>The function description is not set to docstring.</td><td>6</td><td>../numpy/benchmarks/benchmarks/bench_app.py</td></tr><tr><th>1</th><td>setup</td><td>There is an argument whose explanation does no...</td><td>2</td><td>../numpy/benchmarks/benchmarks/bench_app.py</td></tr><tr><th>2</th><td>setup</td><td>While the return value exists in the function,...</td><td>9</td><td>../numpy/benchmarks/benchmarks/bench_app.py</td></tr></tbody></table>

```py
>>> df[100:103]
```

<table border="1" class="dataframe"><thead><tr style="text-align: right;"><th></th><th>func_name</th><th>info</th><th>info_id</th><th>module_path</th></tr></thead><tbody><tr><th>100</th><td>time_bincount</td><td>The function description is not set to docstring.</td><td>6</td><td>../numpy/benchmarks/benchmarks/bench_function_...</td></tr><tr><th>101</th><td>time_weights</td><td>The function description is not set to docstring.</td><td>6</td><td>../numpy/benchmarks/benchmarks/bench_function_...</td></tr><tr><th>102</th><td>setup</td><td>The function description is not set to docstring.</td><td>6</td><td>../numpy/benchmarks/benchmarks/bench_function_...</td></tr></tbody></table>

### Verbose setting

If you only need lint result list, and not necessary standard output, then set verbose argument to 0 and stdout will be disabled.

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='../pandas/pandas/core/arrays/array_.py',
...     verbose=0)
```

### Ignore specified functions

If you want to skip functions with a specific prefix, set prefix names to the `skip_decorator_name_list` argument (default is `[test_]`).

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='../pandas/pandas/core/arrays/array_.py',
...     ignore_func_name_prefix_list=['test_', '_main', '__init__'])
```

### Ignore specified IDs check

You can specify IDs to `ignore_info_id_list` argument to ignore.
The ID corresponds to the return value's `info_id`.

```py
# sample.py

def sample_func():
    """
    Sample function.

    Returns
    -------
    price : int
        Sample price
    """
    pass
```

```py
>>> import numdoclint
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py',
...     verbose=0)
>>> lint_info_list
[{'module_path': './sample.py',
  'func_name': 'sample_func',
  'info_id': 12,
  'info': 'While the return value document exists in docstring, the return value does not exist in the function.'}]

>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py',
...     ignore_info_id_list=[12],
...     verbose=0)
>>> lint_info_list
[]
```

Or you can also specify ID's constant to argument.

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py',
...     ignore_info_id_list=[
...         numdoclint.INFO_ID_LACKED_RETURN_VAL,
...     ],
...     verbose=0)
>>> lint_info_list
[]
```

### Parameters default check

By default, the following docstring `Parameters` default specification will not be checked.

```py
def sample_func(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : int, default 100
        Sample price.
    """
    pass
```

If want to check default specification (e.g., `, default 100`, `, default is 100`, `(default 100)`, or `, optional`) strictly, then set `enable_default_or_optional_doc_check` argument to True.

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='../pandas/pandas/core/frame.py',
...     enable_default_or_optional_doc_check=True)
```

```
...
../pandas/pandas/core/frame.py::to_dict
While there is no description of default value in docstring, there is a default value on the argument side.
Argument name: orient
Argument default value: "dict"
...
```

### Check Jupyter notebook

By using the `check_jupyter_notebook` and `check_jupyter_notebook_recursively` interface, you can check Jupyter notebooks as well as Python modules.

```py
check_result_list = numdoclint.check_jupyter_notebook(
    notebook_path='./sample_notebook.ipynb')
```

```py
check_result_list = numdoclint.check_jupyter_notebook_recursively(
    dir_path='./sample_dir/')
```

`ignore_func_name_prefix_list`, `ignore_info_id_list`, and `enable_default_or_optional_doc_check` arguments described above are also available.

## Command line interface

You can run the check as well with the following command:

```
$ numdoclint -p ./sample/path.py
```

The following arguments are provided. Only `--path` argument is required, other arguments are optional.

```
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Python module file path, Jupyter notebook path, or
                        directory path.
  -r, --check_recursively
                        If specified, check files recursively.In that case,
                        you need to specify the directory in the path
                        argument.
  -j, --is_jupyter      If specified, check target will become Jupyter
                        notebook. If not, Python module will be checked.
  -f IGNORE_FUNC_NAME_PREFIX_LIST, --ignore_func_name_prefix_list IGNORE_FUNC_NAME_PREFIX_LIST
                        A prefix list of function name conditions to ignore.
                        e.g., 'test_,sample_'. Comma separated string is
                        acceptable.
  -i IGNORE_INFO_ID_LIST, --ignore_info_id_list IGNORE_INFO_ID_LIST
                        List of IDs to ignore lint checking. e.g, '1,2,3'. Comma
                        separated integer is acceptable.
  -o, --enable_default_or_optional_doc_check
                        If specified, the `default` and `optional` stringin
                        docstring will be checked.
  -d SKIP_DECORATOR_NAME_LIST, --skip_decorator_name_list SKIP_DECORATOR_NAME_LIST
                        If a decorator name in this list is set to function,
                        that function will not be checked. Specify if
                        necessary for docstring-related decorators. Note: only
                        available when check Python module, not supported
                        Jupyter notebook.
```

### Example of checking Python module recursively:

```
$ numdoclint -p ./sample/dir/ -r
```

### Example of checking Jupyter notebook:

```
$ numdoclint -j -p ./sample/path.ipynb
```

### Example of checking Jupyter notebook recursively:

```
$ numdoclint -j -r -p ./sample/dir/
```

# Lint condition examples

## Lacked docstring function description

```py
# sample.py

def sample_func(price):
    """
    Parameters
    ----------
    name : str
        Sample name.
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py')

./sample.py::sample_func
The function description is not set to docstring.
```

## Lacked argument

```py
# sample.py

def sample_func(price):
    """
    Sample function.

    Parameters
    ----------
    price : int
        Sample price.
    lacked_arg : str
        Sample string.
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py')

./sample.py::sample_func
An argument exists in docstring does not exists in the actual argument.
Lacked argument name: lacked_arg
```

## Lacked docstring parameter description

```py
# sample.py

def sample_func(price, lacked_arg):
    """
    Sample function.

    Parameters
    ----------
    price : int
        Sample price.
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py')

./sample.py::sample_func
There is an argument whose explanation does not exist in docstring.
Target argument name: lacked_arg
```

## Lacked docstring parameter type information

```py
# sample.py

def sample_func(price):
    """
    Sample function.

    Parameters
    ----------
    price
        Sample price (type not specified).
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py')

./sample.py::sample_func
Missing docstring argument type information.
Target argument: price
```

## Lacked docstring parameter description

```py
# sample.py

def sample_func(price, name):
    """
    Sample function.

    Parameters
    ----------
    price : int
    name : str
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py')

./sample.py::sample_func
Missing docstring argument information.
Argument name: price

./sample.py::sample_func
Missing docstring argument information.
Argument name: name
```

## Argument and docstring parameter order mismatching

```py
# sample.py

def sample_func(price, name):
    """
    Sample function.

    Parameters
    ----------
    name : str
        Sample name.
    price : int
        Sample price.
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py')

./sample.py::sample_func
The order of the argument and docstring is different.
Order of arguments: ['price', 'name']
Order of docstring parameters: ['name', 'price']
```

## Lacked docstring default value description

Note: Only enabled when `enable_default_or_optional_doc_check=True` argument specified.

```py
# sample.py

def sample_func(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : int
        Sample price.
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py',
...     enable_default_or_optional_doc_check=True)

./sample.py::sample_func
While there is no description of default value in docstring, there is a default value on the argument side.
Argument name: price
Argument default value: 100
```

Good patterns:

1. `, default xxx` specified (mainly used in Pandas):

```py
# sample.py

def sample_func(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : int, default 100
        Sample price.
    """
    pass
```

2. `, default is xxx` specified (mainly used in NumPy):

```py
# sample.py

def sample_func(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : int, default is 100
        Sample price.
    """
    pass
```

3. `(default 100)` specified (rarely used in Pands):

```py
# sample.py

def sample_func(price=100):
    """
    Sample function.

    Parameters
    ----------
    price : int (default 100)
        Sample price.
    """
    pass
```

## Lacked argument default value, while docstring default value exists.

Note: Only enabled when `enable_default_or_optional_doc_check=True` argument specified.

```py
# sample.py

def sample_func(price):
    """
    Sample function.

    Parameters
    ----------
    price : int, default 100
        Sample price.
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py',
...     enable_default_or_optional_doc_check=True)

./sample.py::sample_func
The default value described in docstring does not exist in the actual argument.
Argment name: price
Docstring default value: 100
```

## Lacked docstring of return value

```py
# sample.py

def sample_func():
    """
    Sample function.
    """
    return 100
```

```
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py',
...     enable_default_or_optional_doc_check=True)

./sample.py::sample_func
While the return value exists in the function, the return value document does not exist in docstring.
```

## Lacked docstring return value description

```py
# sample.py

def sample_func():
    """
    Sample function.

    Returns
    -------
    price : int
    """
    return 100
```

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='./sample.py')

./sample.py::sample_func
Docstring description of return value is missing.
Return value name: price
Return value type: int
```

## Lacked return value, while `Returns` docstring section exists

```py
# sample.py

def sample_func():
    """
    Sample function.

    Returns
    -------
    price : int
        Sample price
    """
    pass
```

```py
>>> lint_info_list = numdoclint.check_python_module(
>>>     py_module_path='./sample.py')

./sample.py::sample_func
While the return value document exists in docstring, the return value does not exist in the function.
```

# Testing and Lint

The following library modules are used for testing and lint.

- pytest==4.3.1
- pytest-cov==2.7.1
- voluptuous==0.12.1
- flake8==3.7.8
- autoflake==1.3
- autopep8==1.4.4
- isort==4.3.16

Command to run overall tests and lint:

```
$ python ./run_all_tests_and_lint.py
```

Command to run the entire test:

```
$ pytest --cov=numdoclint tests/ -v
```

Command to run the autoflake:

```
$ autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r ./
```

Command to run the autopep8:

```
$ autopep8 --in-place --aggressive --aggressive --recursive ./
```

Command to run the isort:

```
$ isort -rc ./
```

Command to run the flake8:

```
$ flake8 ./
```

# PyPI

The following library are used for PyPI uploading.

- twine==1.13.0
- wheel==0.36.2

Build command:

```
$ python build.py
```

Upload to TestPyPI:

```
$ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

Install from TestPyPI:

```
$ pip install --index-url https://testpypi.python.org/simple/ numdoclint
```

Upload to PyPI:

```
$ twine upload dist/*
```
