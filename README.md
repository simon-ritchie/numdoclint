# Numdoc Lint

Numdoc Lint provides features such as NumPy style docstring checking.

# Main features

# Installing

# Examples

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
