# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing

import re
from setuptools import setup


def get_long_description():
    desc = ''
    with open('./README.md') as f:
        desc = f.read()
    return desc


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))

setup(
    name='pipconflictchecker',
    version=get_version(),
    description='A tool that checks installed packages against all package requirements for version conflicts.',
    long_description=get_long_description(),
    classifiers=[
      'Topic :: Utilities',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.0',
      'Programming Language :: Python :: 3.1',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
    ],
    keywords='python pip dependencies conflicts versions checker',
    author='Ambition',
    author_email='opensource@ambition.com',
    url='https://github.com/ambitioninc/pip-conflict-checker',
    license='MIT',
    install_requires=['pip>=1.4.1'],
    packages=['pipconflictchecker'],
    entry_points={
        'console_scripts': [
            'pipconflictchecker = pipconflictchecker.checker:main'
        ]
    },
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose>=1.3.0', 'mock>=1.0.1'],
)