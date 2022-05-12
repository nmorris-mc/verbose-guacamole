#!/usr/bin/env python
from setuptools import find_packages, setup
from setuptools.package_index import safe_name

setup(
    # safe_name() ensures the published package filename does not contain
    # "discouraged" or illegal characters such as underscore, which can cause
    # issues at pip-compile or "pip install" time.
    name=safe_name('{{cookiecutter.package_name}}'),
    packages=find_packages()
)
