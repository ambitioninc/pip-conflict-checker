from setuptools import setup

# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing


def get_long_description():
    desc = ''
    with open('./README.md') as f:
        desc = f.read()
    return desc


setup(
    name='pip-conflict-checker',
    version='0.5.0',
    description='A tool that checks installed packages against all package requirements for version conflicts.',
    long_description=get_long_description(),
    classifiers=[
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='python pip dependencies conflicts versions checker',
    author='Ambition',
    author_email='opensource@ambition.com',
    url='https://github.com/ambitioninc/pip-conflict-checker',
    license='MIT',
    install_requires=[
        'pip>=1.4.1',
        'nose>=1.3.0',
        'mock>=1.0.1',
        'flake8',
        'coverage'
    ],
    packages=['pipconflictchecker'],
    entry_points={
        'console_scripts': [
            'pipconflictchecker = pipconflictchecker.checker:main'
        ]
    },
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=[
        'nose>=1.3.0',
        'mock>=1.0.1',
        'flake8',
        'coverage'
    ],
)
