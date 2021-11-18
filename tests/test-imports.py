#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# Test importing libraries.
# -----------------------------------------------------------------------------

# ----- Import all - implicitly -----------------------------------------------

from senzing import *

# xx = G2Module.G2Module()

print("Test 1: Success")

# ----- Import all - explicitly -----------------------------------------------

from senzing import G2Audit, G2Config, G2Engine, G2Exception, G2Product

# xx = G2Module.G2Module("x", "y")

print("Test 2: Success")

# ----- Import from G2Exception -----------------------------------------------

from senzing.G2Exception import G2InvalidFileTypeContentsException
from senzing.G2Exception import G2InvalidFileTypeContentsException as bob
import senzing.G2Exception

print("Test 3: Success")

# ----- Epilog ----------------------------------------------------------------

print("Done.")
