# coding: utf-8
from setuptools import setup, find_packages

NAME = "emnify-python-sdk"
VERSION = "0.0.4"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = []

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name=NAME,
    version=VERSION,
    description="Supply your swarm of IoT Devices with cloud connectivity by EMnify. Automate your routines with this SDK for Python.",
    author="EMnify",
    author_email="",
    url="https://github.com/EMnify/emnify-sdk-python",
    keywords=["Swagger", "EMnify Python SDK", "IoT"],
    project_urls={
        "Bug Tracker": "https://github.com/EMnify/emnify-sdk-python",
    },
    install_requires=REQUIRES,
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
