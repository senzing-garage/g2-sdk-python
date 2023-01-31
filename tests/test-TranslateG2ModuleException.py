#! /usr/bin/env python3

# Test exceptions.

from senzing import TranslateG2ModuleException, ExceptionMessage, ExceptionCode, G2ModuleNotInitialized

# Create error messages of different types.

error_string = "0023E|Critical Database Error '(1:could not translate host name.."
error_bytearray = bytearray(error_string, 'utf-8')

# Test string.

result = TranslateG2ModuleException(error_string)
print(result)

# Test bytearray.

result = TranslateG2ModuleException(error_bytearray)
print(result)


# Test error

result = ExceptionMessage(error_bytearray)
print(result)

result = ExceptionCode(error_bytearray)
print(result)

# Test error

err = G2ModuleNotInitialized("0050E|Fake G2ModuleNotInitialized exception")

result = ExceptionMessage(err)
print(result)

result = ExceptionCode(err)
print(result)
