#! /usr/bin/env python3

from senzing import G2RetryTimeoutExceeded

try:
    print("do something")
except G2RetryTimeoutExceeded as err:
    print("error: ", err)
