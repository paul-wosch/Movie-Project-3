"""Configure the myapp package for installation and distribution.

It uses setuptools to package the application located in
the src/ directory.
"""

from setuptools import setup, find_packages

setup(
    name="myapp",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
