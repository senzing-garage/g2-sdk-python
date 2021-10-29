#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# Test importing libraries.
# -----------------------------------------------------------------------------


# ----- Import all - implicitly -----------------------------------------------

from senzing import *

print("Test 1: Success")

# ----- Import all - explicitly -----------------------------------------------

from senzing import CompressedFile, DumpStack, G2ConfigModule, G2ConfigTables, G2Database, G2Exception, G2Module, G2Project

print("Test 2: Success")

# ----- Import from G2Exception -----------------------------------------------

from senzing.G2Exception import G2InvalidFileTypeContentsException
from senzing.G2Exception import G2InvalidFileTypeContentsException as bob
import senzing.G2Exception

print("Test 3: Success")

# ----- Epilog ----------------------------------------------------------------

print("Done.")
