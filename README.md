# g2-sdk-python

## Synopsis

Senzing Software Development Kit (SDK) for Python.

This SDK provide python access to the
[senzingapi](https://senzing.com/senzing-api/)

More information at
[github.com/Senzing/g2-sdk-python](https://github.com/Senzing/g2-sdk-python)

## Overview

The git repository  at
[github.com/Senzing/g2-sdk-python](https://github.com/Senzing/g2-sdk-python)
contains the Senzing SDK for Python files in `src/senzing`.

It also contains:

- Tooling to create Python "wheel" packages
- Test suites
- Instructions for publishing to [PyPi](https://pypi.org/).

### Contents

1. [Install](#install)
1. [Develop](#develop)
    1. [Prerequisites for development](#prerequisites-for-development)
    1. [Clone repository](#clone-repository)
    1. [Install dependencies](#install-dependencies)
    1. [Build python packages](#build-python-packages)
    1. [Local test](#local-test)
    1. [Publish](#publish)
    1. [Test](#test)
    1. [Uninstall](#uninstall)
    1. [Verify Uninstal](#verify-uninstall)
1. [References](#references)

## Install

1. Use the [pip install](https://pip.pypa.io/en/stable/cli/pip_install/)
   command to install the
   [Senzing SDK for Python](https://pypi.org/project/senzing/).
   Example:

    ```console
    pip install senzing
    ```

1. More information at
   [github.com/Senzing/g2-sdk-python](https://github.com/Senzing/g2-sdk-python)

## Develop

The following instructions are used when modifying and building the Docker image.

### Prerequisites for development

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:
    1. [git](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-git.md)
    1. [make](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-make.md)
    1. [pip](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-pip.md)

1. :pencil2: Make a `~/.pypirc` file.
   Example:

    ```console
    [pypi]
      username = __token__
      password = pypi-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

    [testpypi]
      username = __token__
      password = pypi-bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
    ```

### Clone repository

For more information on environment variables,
see [Environment Variables](https://github.com/Senzing/knowledge-base/blob/master/lists/environment-variables.md).

1. Set these environment variable values:

    ```console
    export GIT_ACCOUNT=senzing
    export GIT_REPOSITORY=g2-sdk-python
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
    ```

1. Using the environment variables values just set, follow steps in [clone-repository](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/clone-repository.md) to install the Git repository.

### Install dependencies

1. Install python tools via `Makefile`.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make install-dependencies
    ```

### Build python packages

1. Build pip package using `python3 -m build` via `Makefile`.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make package
    ```

   Output will be in the `dist` directory.

### Local test

#### Install from file

1. Install using `pip` via `Makefile`.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make install-file
    ```

#### Test local package

1. Run testcases found in `tests` directory.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make test
    ```

#### Uninstall local package

1. Remove senzing.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make uninstall
    ```

### Publish

:warning:  On [PyPi](https://pypi.org/) and
[test.pypi](https://test.pypi.org/),
pip package versions are immmutable.
They cannot be deleted nor updated.
Since only one instance of a version can be published,
be careful on what is published.

#### Publish to test.pypi.org

1. Publish to <https://test.pypi.org>.
   This is a test PyPi server.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make publish-test
    ```

#### Publish to pypi.org

1. Publish to <https://pypi.org>.
   :warning: This requires that the workstation has `gpg` enabled with
   the signing key for "Senzing, Inc."
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make publish-signed
    ```

### Test

#### Install from test.pypi.org

1. Install using `pip` via `Makefile`.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make install-test
    ```

#### Install from pypi.org

1. Install using `pip` via `Makefile`.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make install
    ```

#### Unit tests

1. Run testcases found in `tests` directory.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make test
    ```

### Uninstall

1. Remove Senzing SDK for Python.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make uninstall
    ```

### Verify Uninstall

1. :pencil2: Identify python version.
   Example:

    ```console
    export SENZING_PYTHON_VERSION=3.8
    ```

1. Verify deletion in user python repository.
   Example:

    ```console
    ls ~/.local/lib/python${SENZING_PYTHON_VERSION}/site-packages | grep senzing
    ```

   Should return nothing.

1. Verify deletion in system repository.
   Example:

    ```console
    ls /usr/local/lib/python${SENZING_PYTHON_VERSION}/dist-packages | grep senzing
    ```

   Should return nothing.

## References

1. [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
