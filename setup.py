"""
Build qsAPI

```
rm dist/*
./setup.py build sdist
use qsAPI-<version>.tar.gz to install on server
```
"""
import setuptools

from qsAPI import __version__


with open("README.md", "r") as fh:
    long_description = fh.read()

# long_description = "qsAPI is a client for Qlik Sense QPS and QRS interfaces"

setuptools.setup(
    name="qsAPI",
    version=__version__,
    author="Rafael Sanz",
    author_email="rafael.sanz@selab.es",
    description="qsAPI - a client for Qlik Sense QPS and QRS interfaces",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rafael-sanz/qsAPI",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests"
    ],
    extras_require={
        "ntlm": ["requests_ntlm"],
    },
    entry_points={
        'console_scripts': [
            'qsAPI = qsAPI.__main__:main'
        ]
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
