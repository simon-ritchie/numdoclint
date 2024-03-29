"""
A module that handles builds for PyPI uploads.
"""

import os
import shutil

if __name__ == '__main__':
    if os.path.exists('./build'):
        shutil.rmtree('./build', ignore_errors=True)
    if os.path.exists('./dist'):
        shutil.rmtree('./dist', ignore_errors=True)
    if os.path.exists('./numdoclint.egg-info'):
        shutil.rmtree('./numdoclint.egg-info', ignore_errors=True)

    print('running sdist command...')
    os.system('python setup.py sdist')
    print('running bdist_wheel command...')
    os.system('python setup.py bdist_wheel')
