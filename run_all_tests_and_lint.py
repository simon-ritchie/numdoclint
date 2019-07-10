"""Script to run each tests and lint.
"""

import logging
import os

log_format = '-----------------------------------------\n'\
             '%(levelname)s : %(asctime)s : %(message)s'
logging.basicConfig(level=logging.DEBUG, format=log_format)


def main():
    """
    Run tests and lint when executed via the command line.
    """
    logging.info('[Lint] autoflake started.')
    os.system(
        'autoflake --in-place --remove-unused-variables '
        '--remove-all-unused-imports -r ./')

    logging.info('[Lint] autopep8 started.')
    os.system('autopep8 --in-place --aggressive --aggressive --recursive ./')

    logging.info('[Lint] isort started.')
    os.system('isort -rc ./')

    logging.info('[Lint] flake8 started.')
    os.system('flake8 ./')

    logging.info('[Testing] pytest started.')
    os.system('pytest --cov=numdoclint tests/')


if __name__ == '__main__':
    main()
