from ctypes import *
import threading
import json
import os
import functools
import warnings

from .G2Exception import TranslateG2ModuleException, G2ModuleNotInitialized, G2ModuleGenericException

__all__ = ['G2Product']
SENZING_PRODUCT_ID = "5027"  # See https://github.com/Senzing/knowledge-base/blob/main/lists/senzing-product-ids.md


class MyBuffer(threading.local):

    def __init__(self):
        self.buf = create_string_buffer(65535)
        self.bufSize = sizeof(self.buf)
        # print("Created new Buffer {}".format(self.buf))


tls_var = MyBuffer()


def resize_return_buffer(buf_, size_):
    """  callback function that resizes return buffer when it is too small
    Args:
    size_: size the return buffer needs to be
    """
    try:
        if not tls_var.buf:
            # print("New RESIZE_RETURN_BUF {}:{}".format(buf_,size_))
            tls_var.buf = create_string_buffer(size_)
            tls_var.bufSize = size_
        elif (tls_var.bufSize < size_):
            # print("RESIZE_RETURN_BUF {}:{}/{}".format(buf_,size_,tls_var.bufSize))
            foo = tls_var.buf
            tls_var.buf = create_string_buffer(size_)
            tls_var.bufSize = size_
            memmove(tls_var.buf, foo, sizeof(foo))
    except AttributeError:
        # print("AttributeError RESIZE_RETURN_BUF {}:{}".format(buf_,size_))
        tls_var.buf = create_string_buffer(size_)
        # print("Created new Buffer {}".format(tls_var.buf))
        tls_var.bufSize = size_
    return addressof(tls_var.buf)


def deprecated(instance):

    def the_decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)  # turn off filter
            warnings.warn(
                "senzing-{0}{1:04d}W Call to deprecated function {2}.".format(SENZING_PRODUCT_ID, instance, func.__name__),
                category=DeprecationWarning,
                stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)  # reset filter
            return func(*args, **kwargs)

        return wrapper

    return the_decorator

# -----------------------------------------------------------------------------
# G2Product class
# -----------------------------------------------------------------------------


class G2Product(object):
    """G2 product module access library

    Attributes:
        _lib_handle: A boolean indicating if we like SPAM or not.
        _resize_func_def: resize function definiton
        _resize_func: resize function pointer
        _module_name: CME module name
        _ini_file_name: name and location of .ini file
    """

    def __init__(self, *args, **kwargs):
        # type: () -> None
        """ Class initialization
        """

        try:
            if os.name == 'nt':
                self._lib_handle = cdll.LoadLibrary("G2.dll")
            else:
                self._lib_handle = cdll.LoadLibrary("libG2.so")
        except OSError as ex:
            print("ERROR: Unable to load G2.  Did you remember to setup your environment by sourcing the setupEnv file?")
            print("ERROR: For more information see https://senzing.zendesk.com/hc/en-us/articles/115002408867-Introduction-G2-Quickstart")
            print("ERROR: If you are running Ubuntu or Debian please also review the ssl and crypto information at https://senzing.zendesk.com/hc/en-us/articles/115010259947-System-Requirements")
            raise G2ModuleGenericException("Failed to load the G2 library")

        self._resize_func_def = CFUNCTYPE(c_char_p, c_char_p, c_size_t)
        self._resize_func = self._resize_func_def(resize_return_buffer)

# -----------------------------------------------------------------------------
# Internal helper methods
# -----------------------------------------------------------------------------

    def prepareStringArgument(self, stringToPrepare):
        # type: (str) -> str
        """ Internal processing function """

        # handle null string
        if stringToPrepare is None:
            return b''
        # if string is unicode, transcode to utf-8 str
        if type(stringToPrepare) == str:
            return stringToPrepare.encode('utf-8')
        # if input is bytearray, assumt utf-8 and convert to str
        elif type(stringToPrepare) == bytearray:
            return stringToPrepare.decode().encode('utf-8')
        elif type(stringToPrepare) == bytes:
            return str(stringToPrepare).encode('utf-8')
        # input is already a str
        return stringToPrepare

# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------

    @deprecated(1101)
    def initV2(self, module_name_, ini_params_, debug_=False):
        self.init(module_name_, ini_params_, debug_)

    def init(self, module_name_, ini_params_, debug_=False, *args, **kwargs):

        self._module_name = self.prepareStringArgument(module_name_)
        self._ini_params = self.prepareStringArgument(ini_params_)
        self._debug = debug_

        if self._debug:
            print("Initializing G2Product")

        self._lib_handle.G2Product_init.argtypes = [c_char_p, c_char_p, c_int]
        ret_code = self._lib_handle.G2Product_init(self._module_name, self._ini_params, self._debug)

        if self._debug:
            print("Initialization Status: " + str(ret_code))

        if ret_code < 0:
            self._lib_handle.G2Product_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def license(self, *args, **kwargs):
        # type: () -> object
        """ Retrieve the G2 license details

        Args: (None)

        Return:
            object: JSON document with G2 license details
        """

        self._lib_handle.G2Product_license.restype = c_char_p
        ret = self._lib_handle.G2Product_license()
        return str(ret.decode('utf-8'))

    def validateLicenseFile(self, licenseFilePath, *args, **kwargs):
        # type: (int) -> str
        """ Validates a license file.
        Args:
            licenseFilePath: The path of the license file to validate

        Return:
            str: 0 for successful validation, 1 for failure
        """

        _licenseFilePath = self.prepareStringArgument(licenseFilePath)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Product_validateLicenseFile.restype = c_int
        self._lib_handle.G2Product_validateLicenseFile.argtypes = [c_char_p, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Product_validateLicenseFile(_licenseFilePath, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Product has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Product_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        return ret_code

    def validateLicenseStringBase64(self, licenseString, *args, **kwargs):
        # type: (int) -> str
        """ Validates a license string.
        Args:
            licenseString: The license string to validate

        Return:
            str: 0 for successful validation, 1 for failure
        """

        _licenseString = self.prepareStringArgument(licenseString)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Product_validateLicenseStringBase64.restype = c_int
        self._lib_handle.G2Product_validateLicenseStringBase64.argtypes = [c_char_p, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Product_validateLicenseStringBase64(_licenseString, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Product has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Product_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        return ret_code

    def version(self, *args, **kwargs):
        # type: () -> object
        """ Retrieve the G2 version details

        Args: (None)

        Return:
            object: JSON document with G2 version details
        """

        self._lib_handle.G2Product_version.restype = c_char_p
        ret = self._lib_handle.G2Product_version()
        return str(ret.decode('utf-8'))

    def destroy(self, *args, **kwargs):
        """ Uninitializes the engine
        This should be done once per process after init(...) is called.
        After it is called the engine will no longer function.

        Args: (None)

        """

        self._lib_handle.G2Product_destroy()

    @deprecated(1102)
    def clearLastException(self, *args, **kwargs):
        """ Clears the last exception

        """

        self._lib_handle.G2Product_clearLastException.restype = None
        self._lib_handle.G2Product_clearLastException.argtypes = []
        self._lib_handle.G2Product_clearLastException()

    @deprecated(1103)
    def getLastException(self, *args, **kwargs):
        """ Gets the last exception
        """

        self._lib_handle.G2Product_getLastException.restype = c_int
        self._lib_handle.G2Product_getLastException.argtypes = [c_char_p, c_size_t]
        self._lib_handle.G2Product_getLastException(tls_var.buf, sizeof(tls_var.buf))
        resultString = tls_var.buf.value.decode('utf-8')
        return resultString

    @deprecated(1104)
    def getLastExceptionCode(self, *args, **kwargs):
        """ Gets the last exception code
        """

        self._lib_handle.G2Product_getLastExceptionCode.restype = c_int
        self._lib_handle.G2Product_getLastExceptionCode.argtypes = []
        exception_code = self._lib_handle.G2Product_getLastExceptionCode()
        return exception_code
