# 
#   Function
#   Copyright © 2023 NatML Inc. All Rights Reserved.
#

from setuptools import find_packages, setup

# Get readme
with open("README.md", "r") as readme:
    long_description = readme.read()

# Get version
with open("fxn/version.py") as version_source:
    gvars = {}
    exec(version_source.read(), gvars)
    version = gvars["__version__"]

# Setup
setup(
    name="fxn",
    version=version,
    author="NatML Inc.",
    author_email="hi@fxn.ai",
    description="Run on-device and cloud AI prediction functions in Python. Register at https://fxn.ai.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache License 2.0",
	python_requires=">=3.7",
    install_requires=[
        "filetype",
        "numpy",
        "pillow",
        "requests",
        "rich",
        "typer"
    ],
    url="https://fxn.ai",
    packages=find_packages(
        include=["fxn", "fxn.*"],
        exclude=["test", "examples"]
    ),
    entry_points={
        "console_scripts": [
            "fxn=fxn.cli.__init__:app"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Software Development :: Libraries",
    ],
    project_urls={
        "Documentation": "https://docs.fxn.ai",
        "Source": "https://github.com/fxnai/fxn"
    },
)