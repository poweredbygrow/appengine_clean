#!/usr/bin/env bash
rm -rf dist/
python3 setup.py sdist bdist_wheel
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
