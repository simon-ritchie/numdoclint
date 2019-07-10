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

If you want to skip functions with a specific suffix, set suffix names to the `skip_decorator_name_list` argument (default is `[test_]`).

```py
>>> lint_info_list = numdoclint.check_python_module(
...     py_module_path='../pandas/pandas/core/arrays/array_.py',
...     skip_decorator_name_list=['test_', '_main', '__init__'])
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

## Command line interface

Currently not implemented yet ([#2](https://github.com/simon-ritchie/numdoclint/issues/2)).

# Testing and Lint

The following library modules are used for testing and lint.

- pytest==4.3.1
- pytest-cov==2.7.1
- voluptuous==0.11.5
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
$ pytest --cov=numdoclint tests/
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
