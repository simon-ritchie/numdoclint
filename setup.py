from setuptools import find_packages, setup

description = 'Numdoc Lint provides features such as '\
              'NumPy style docstring code checking.'

long_description = \
    'Numdoc Lint provides features such as NumPy style '\
    'docstring code checking.\n\nPlease see github for more detail.'\
    '\nhttps://github.com/simon-ritchie/numdoclint'

setup(
    name='numdoclint',
    version='0.0.7',
    url='https://github.com/simon-ritchie/numdoclint',
    author='simon-ritchie',
    author_email='',
    maintainer='simon-ritchie',
    maintainer_email='',
    description=description,
    long_description=long_description,
    packages=find_packages(),
    install_requires=['six'],
    include_package_data=True,
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
),
