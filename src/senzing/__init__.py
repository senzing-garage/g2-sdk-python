
# Each of the submodules must have the having an __all__ variable defined for the "*" to work.

from .G2Config import *
from .G2ConfigMgr import *
from .G2Diagnostic import *
from .G2Engine import *
from .G2Exception import *
from .G2Hasher import *
from .G2IniParams import *
from .G2Product import *

# Aggregate all of the submodules into the single package.

__all__ = (
    G2Config.__all__ +
    G2ConfigMgr._all__ +
    G2Diagnostic.__all__ +
    G2Engine.__all__ +
    G2Exception.__all__ +
    G2Hasher.__all__ +
    G2IniParams.__all__ +
    G2Product.__all__
    )
