# g2-sdk-python

If you are beginning your journey with [Senzing],
please start with [Senzing Quick Start guides].

You are in the [Senzing Garage] where projects are "tinkered" on.
Although this GitHub repository may help you understand an approach to using Senzing,
it's not considered to be "production ready" and is not considered to be part of the Senzing product.
Heck, it may not even be appropriate for your application of Senzing!

## Synopsis

Senzing Software Development Kit (SDK) for Python.
This SDK provide python access to the [senzingapi]

**Warning:** Using `pip install senzing-ce` will install a version of the Senzing Python SDK
that _is not_ covered by Senzing's Service Level Agreement (SLA).
To obtain a version of the Senzing Python SDK that _is_ covered, see
[Install Senzing API].

More information at [github.com/senzing-garage/g2-sdk-python]

## Overview

The git repository at [github.com/senzing-garage/g2-sdk-python]
contains the Senzing SDK for Python files in `src/senzing`.

It also contains:

- Tooling to create Python "wheel" packages
- Test suites
- Instructions for publishing to [PyPi].

### Contents

1. [Install]
1. [Develop]
   1. [Prerequisites for development]
   1. [Clone repository]
   1. [Install dependencies]
   1. [Build python packages]
   1. [Local test]
   1. [Publish]
   1. [Test]
   1. [Uninstall]
   1. [Verify Uninstall]
1. [References]

## Install

1. Use the [pip install] command to install the
   [Senzing SDK for Python] community edition.
   Example:

   ```console
   pip install senzing-ce
   ```

1. More information at [github.com/senzing-garage/g2-sdk-python]

## Develop

The following instructions are used when modifying and building the Docker image.

### Prerequisites for development

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:

   1. [git]
   1. [make]
   1. [pip]

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

For more information on environment variables, see [Environment Variables].

1. Set these environment variable values:

   ```console
   export GIT_ACCOUNT=senzing
   export GIT_REPOSITORY=g2-sdk-python
   export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
   export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
   ```

1. Using the environment variables values just set, follow steps in [clone-repository] to install the Git repository.

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

:warning: On [PyPi] and [test.pypi],
pip package versions are immutable.
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

1. [Packaging Python Projects]

[Build python packages]: #build-python-packages
[Clone repository]: #clone-repository
[clone-repository]: https://github.com/senzing-garage/knowledge-base/blob/main/HOWTO/clone-repository.md
[Develop]: #develop
[Environment Variables]: https://github.com/senzing-garage/knowledge-base/blob/main/lists/environment-variables.md
[git]: https://github.com/senzing-garage/knowledge-base/blob/main/WHATIS/git.md
[github.com/senzing-garage/g2-sdk-python]: https://github.com/senzing-garage/g2-sdk-python
[Install dependencies]: #install-dependencies
[Install Senzing API]: https://hub.senzing.com/knowledge-base/senzingapi/install
[Install]: #install
[Local test]: #local-test
[make]: https://github.com/senzing-garage/knowledge-base/blob/main/WHATIS/make.md
[Packaging Python Projects]: https://packaging.python.org/tutorials/packaging-projects/
[pip install]: https://pip.pypa.io/en/stable/cli/pip_install/
[pip]: https://github.com/senzing-garage/knowledge-base/blob/main/HOWTO/install-pip.md
[Prerequisites for development]: #prerequisites-for-development
[Publish]: #publish
[PyPi]: https://pypi.org/
[References]: #references
[Senzing Garage]: https://github.com/senzing-garage
[Senzing Quick Start guides]: https://docs.senzing.com/quickstart/
[Senzing SDK for Python]: https://pypi.org/project/senzing/
[Senzing]: https://senzing.com/
[senzingapi]: https://senzing.com/senzing-api/
[test.pypi]: https://test.pypi.org/
[Test]: #test
[Uninstall]: #uninstall
[Verify Uninstall]: #verify-uninstall
