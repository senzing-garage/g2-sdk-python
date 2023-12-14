# Tricky code:
# Because the filenames are the same as class names in many instances,
# the __all__ list needs to be constructed from the files before the
# classes are imported.   For that reason, there is a 2-step process:
#   1) Use the "names" as filenames to access the "__all__" attribute.
#   2) Use the "names" as class names.

# Step 1: Import the files so that the __all__ attribute will work with the "name" (e.g. G2Config, G2ConfigMgr)

import warnings

from . import (
    G2Config,
    G2ConfigMgr,
    G2Diagnostic,
    G2Engine,
    G2EngineFlags,
    G2Exception,
    G2Hasher,
    G2Product,
)

import_lists = [
    G2Config.__all__,
    G2ConfigMgr.__all__,
    G2Diagnostic.__all__,
    G2Engine.__all__,
    G2EngineFlags.__all__,
    G2Exception.__all__,
    G2Hasher.__all__,
    G2Product.__all__,
]

__all__ = []
for import_list in import_lists:
    __all__.extend(import_list)

# Step 2: Overwrite the "name" that did point to the file in step #1 to now point to the class.
# Each of the submodules must have the having an __all__ variable defined for the "*" to work.

from .G2Config import *
from .G2ConfigMgr import *
from .G2Diagnostic import *
from .G2Engine import *
from .G2EngineFlags import *
from .G2Exception import *
from .G2Exception import DEPRECATED_CLASSES
from .G2Hasher import *
from .G2Product import *


def __getattr__(name):
    if name in DEPRECATED_CLASSES:
        replacement_class = DEPRECATED_CLASSES.get(name, G2Exception)
        replacement_class_name = replacement_class.__name__
        warnings.warn(
            f"{name} has been deprecated and replaced at runtime with"
            f" {replacement_class_name}. You can modify the code to explicitly use"
            f" {replacement_class_name} and remove this warning.",
            DeprecationWarning,
            stacklevel=2,
        )
        return replacement_class
    raise AttributeError
