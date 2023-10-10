#! /usr/bin/env python3

# Test exceptions.

# from senzing import TranslateG2ModuleException, ExceptionMessage, ExceptionCode, G2ModuleNotInitialized, G2DatabaseConnectionLostException, G2ModuleLicenseException
from senzing import *
from senzing import G2Exception

# Create error messages of different types.

error_string = "0023E|Critical Database Error '(1:could not translate host name.."
error_bytearray = bytearray(error_string, 'utf-8')

# Test string.

result = TranslateG2ModuleException(error_string)
print("TranslateG2ModuleException 1: {0}".format(result))

# Test bytearray.

result = TranslateG2ModuleException(error_bytearray)
print("TranslateG2ModuleException 2: {0}".format(result))

# Test error

result = ExceptionMessage(error_bytearray)
print("ExceptionMessage 1: {0}".format(result))

result = ExceptionCode(error_bytearray)
print("ExceptionCode 1: {0}".format(result))

# Test detailed Exception class

testname = "Detailed Exception class:"
try:
    raise TranslateG2ModuleException("0033E|..")
except G2NotFoundException as err:
    print(testname, "PASS - G2NotFoundException")
except G2BadInputException as err:
    print(testname, "FAIL - G2BadInputException")
except G2Exception as err:
    print(testname, "FAIL - G2Exception")
except Exception as err:
    print(">>> Exception")

# Test general Exception class

testname = "General Exception class:"
try:
    raise TranslateG2ModuleException("0033E|..")
except G2BadInputException as err:
    print(testname, "PASS - G2BadInputException")
except G2Exception as err:
    print(testname, "FAIL - G2Exception")
except Exception as err:
    print(testname, "FAIL - Exception")

# Test senzing Exception class

testname = "Senzing Exception class:"
try:
    raise TranslateG2ModuleException("0033E|..")
except G2Exception as err:
    print(testname, "PASS - G2Exception")
except Exception as err:
    print(testname, "FAIL - Exception")

# Test Exception class

testname = "Exception class:"
try:
    raise TranslateG2ModuleException("0033E|..")
except G2Exception as err:
    print(testname, "PASS - Exception")

result = TranslateG2ModuleException("0033E|..")
print("TranslateG2ModuleException 3: {0}".format(result))

# Test deprecation

err = G2ModuleNotInitialized("0050E|Fake G2ModuleNotInitialized exception")
err = G2ModuleLicenseException("0050E|Fake G2ModuleNotInitialized exception")
