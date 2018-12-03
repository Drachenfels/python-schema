import os

from setuptools import setup, find_packages


def get_version():
    file_path = os.path.join(os.path.dirname(__file__), 'VERSION')

    with open(file_path) as fpl:
        return fpl.read()


def get_readme():
    file_path = os.path.join(os.path.dirname(__file__), 'README.md')

    with open(file_path) as fpl:
        return fpl.read()


def get_requirements():
    with open('config/pip/requirements.txt') as fpl:
        lines = fpl.readlines()

    return [line.strip() for line in lines if not line.startswith('-')]


requirements = get_requirements()


setup(
    name='python_schema',
    version=get_version(),
    description='Simple but not simplistic schema for data-validation',
    long_description=get_readme(),
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development',
    ],
    keywords='schema',
    url='https://github.com/Drachenfels/python-schema',
    packages=find_packages('.', exclude=['tests*']),
    license="MIT",
    author=(
        'Drachenfels <drachenfels@protonmail.com>'
    ),
    author_email=(
        "dariusz.wiatrak@essenceglobal.com, "
    ),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False
)
