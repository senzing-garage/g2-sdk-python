#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# Test importing libraries.
# -----------------------------------------------------------------------------

# import senzing.G2Exception

# from senzing import CompressedFile, DumpStack, G2Database, G2Module, G2Project, G2Exception

from senzing import *

print("Test 1: Success")

from senzing import CompressedFile, DumpStack, G2ConfigModule, G2ConfigTables, G2Database, G2Exception, G2Module, G2Project

print("Test 2: Success")

from senzing.G2Exception import G2InvalidFileTypeContentsException

print("Test 3: Success")

from senzing.G2Exception import G2InvalidFileTypeContentsException as bob

print("Test 4: Success")

import senzing.G2Exception

print("Test 5: Success")
print("Done.")
