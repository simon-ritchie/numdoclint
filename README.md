# Numdoc Lint

Numdoc Lint provides features such as NumPy style docstring checking.

# Main features

# Installing

# Examples

# Testing and Lint

The following library modules are used for testing and lint.

- pytest==4.3.1
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
$ pytest -s -vv
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
