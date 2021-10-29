# g2-sdk-python


## Develop

The following instructions are used when modifying and building the Docker image.

### Prerequisites for development

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:
    1. [git](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-git.md)
    1. [make](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-make.md)
    1. [pip](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-pip.md)

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


### Build python packages

1. XXX
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make package
    ```

### Install

1. xxx.
   Example:

    ```console
    pip3 install --index-url https://test.pypi.org/simple/ --no-deps senzing
    ```

### Test

1. xxx.
   Example:

    ```console
    make test
    ```

### Uninstall

1. xxx.
   Example:

    ```console
    pip3 uninstall senzing
    ```

## References

1. [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
