#! /usr/bin/env python3

# -----------------------------------------------------------------------------
# Test importing libraries.
# -----------------------------------------------------------------------------

# ----- Import all - implicitly -----------------------------------------------

from senzing import *

# g2_audit = G2Audit.G2Audit()
# g2_config = G2Config.G2Config()
# g2_config_mgr = G2ConfigMgr.G2ConfigMgr()
# g2_diagnostic = G2Diagnostic.G2Diagnostic()
# g2_engine = G2Engine.G2Engine()
g2_hasher = G2Hasher.G2Hasher()
g2_ini_params = G2IniParams.G2IniParams()
# g2_product = G2Product.G2Product()

print("Test 1: Success")

# ----- Import all - explicitly -----------------------------------------------

from senzing import G2Audit, G2Config, G2ConfigMgr, G2Diagnostic, G2Engine, G2Exception, G2Hasher, G2IniParams, G2Product

# g2_audit = G2Audit.G2Audit()
# g2_config = G2Config.G2Config()
# g2_config_mgr = G2ConfigMgr.G2ConfigMgr()
# g2_diagnostic = G2Diagnostic.G2Diagnostic()
# g2_engine = G2Engine.G2Engine()
g2_hasher = G2Hasher.G2Hasher()
g2_ini_params = G2IniParams.G2IniParams()
# g2_product = G2Product.G2Product()

print("Test 2: Success")

# ----- Import from G2Exception -----------------------------------------------

from senzing.G2Exception import G2InvalidFileTypeContentsException
from senzing.G2Exception import G2InvalidFileTypeContentsException as bob
import senzing.G2Exception

print("Test 3: Success")

# ----- Epilog ----------------------------------------------------------------

print("Done.")
