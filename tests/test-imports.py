#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# Test importing libraries.
# -----------------------------------------------------------------------------

# ----- Import all - implicitly -----------------------------------------------

from senzing import *

# g2_config = G2Config()
# g2_config_mgr = G2ConfigMgr()
# g2_diagnostic = G2Diagnostic()
# g2_engine = G2Engine()
g2_hasher = G2Hasher()
# g2_product = G2Product()

an_exception_class = G2ModuleException
an_exception_object = G2ModuleException("Some Error")

print("Test 1: Success")

# ----- Import all - explicitly -----------------------------------------------

from senzing import G2Config, G2ConfigMgr, G2Diagnostic, G2Engine, G2Exception, G2Hasher, G2Product

# g2_config = G2Config()
# g2_config_mgr = G2ConfigMgr()
# g2_diagnostic = G2Diagnostic()
# g2_engine = G2Engine()
g2_hasher = G2Hasher()
# g2_product = G2Product()

print("Test 2: Success")

# ----- Import from G2Exception -----------------------------------------------

from senzing.G2Exception import G2ModuleException
from senzing.G2Exception import G2ModuleException as bob
import senzing.G2Exception

print("Test 3: Success")

# ----- Epilog ----------------------------------------------------------------

print("Done.")
