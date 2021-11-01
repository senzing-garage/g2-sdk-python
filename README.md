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

1. Build pip package using `python3 -m build`.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make package
    ```

### Publish

1. Publish to <https://test.pypi.org>.
   Example:

    ```console
    cd ${GIT_REPOSITORY_DIR}
    make test-publish
    ```

### Install from test.pypi.org

1. Install using `pip`.
   Example:

    ```console
    pip3 install \
      --index-url https://test.pypi.org/simple/ \
      --no-deps \
      senzing
    ```

### Test

1. Run testcases found in `tests` directory.
   Example:

    ```console
    make test
    ```

### Uninstall

1. Remove senzing.
   Example:

    ```console
    pip3 uninstall senzing
    ```

1. Verify.
   Example:

    ```console
    ls ~/.local/lib/python3.8/site-packages | grep senzing
    ```

    ```console
    ls /usr/local/lib/python3.8/dist-packages | grep senzing
    ```

## References

1. [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
