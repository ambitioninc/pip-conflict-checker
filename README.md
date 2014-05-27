[![Build Status](https://travis-ci.org/ambitioninc/pip-conflict-checker.png)](https://travis-ci.org/ambitioninc/pip-conflict-checker)
pip-conflict-checker
====================

A tool that checks installed packages against all package requirements to ensure that there are no dependency version conflicts.

## Installation
```
pip install pip-conflict-checker
```

### Usage
Simply run the command pipconflictchecker. If any dependency conflicts are found an output dump of all conflicts will be shown,
and an exit code of 1 will be returned.
