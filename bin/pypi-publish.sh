#!/usr/bin/env bash

rm -rf build/
rm -rf dist/
rm -rf python_schema.egg-info/

python3 setup.py clean
python3 setup.py sdist bdist_wheel
twine upload dist/*
