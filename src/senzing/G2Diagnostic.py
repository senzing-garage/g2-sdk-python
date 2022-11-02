from ctypes import *
import threading
import json
import os
import functools
import warnings
from csv import reader as csvreader

from .G2Exception import TranslateG2ModuleException, G2ModuleNotInitialized, G2ModuleGenericException

__all__ = ['G2Diagnostic']
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
# G2Diagnostic class
# -----------------------------------------------------------------------------


class G2Diagnostic(object):
    """G2 diagnostic module access library

    Attributes:
        _lib_handle: A boolean indicating if we like SPAM or not.
        _resize_func_def: resize function definiton
        _resize_func: resize function pointer
        _module_name: CME module name
        _ini_file_name: name and location of .ini file
    """

    def __init__(self, *args, **kwargs):
        # type: (str, str, bool) -> None
        """ G2Diagnostic class initialization
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

    def prepareBooleanArgument(self, booleanToPrepare):
        booleanValue = 0
        if booleanToPrepare:
            booleanValue = 1
        return booleanToPrepare

    def prepareIntArgument(self, valueToPrepare):
        # type: (str) -> int
        """ Internal processing function """
        """ This converts many types of values to an integer """

        # handle null string
        if valueToPrepare is None:
            return 0
        # if string is unicode, transcode to utf-8 str
        if type(valueToPrepare) == str:
            return int(valueToPrepare.encode('utf-8'))
        # if input is bytearray, assumt utf-8 and convert to str
        elif type(valueToPrepare) == bytearray:
            return int(valueToPrepare)
        elif type(valueToPrepare) == bytes:
            return int(valueToPrepare)
        # input is already an int
        return valueToPrepare

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

    @deprecated(1201)
    def initV2(self, module_name_, ini_params_, debug_=False):
        self.init(module_name_, ini_params_, debug_)

    def init(self, module_name_, ini_params_, debug_=False, *args, **kwargs):

        self._module_name = self.prepareStringArgument(module_name_)
        self._ini_params = self.prepareStringArgument(ini_params_)
        self._debug = debug_

        if self._debug:
            print("Initializing G2 diagnostic module")

        self._lib_handle.G2Diagnostic_init.argtypes = [c_char_p, c_char_p, c_int]
        ret_code = self._lib_handle.G2Diagnostic_init(self._module_name, self._ini_params, self._debug)

        if self._debug:
            print("Initialization Status: " + str(ret_code))

        if ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    @deprecated(1202)
    def initWithConfigIDV2(self, engine_name_, ini_params_, initConfigID_, debug_):
        self.initWithConfigID(engine_name_, ini_params_, initConfigID_, debug_)

    def initWithConfigID(self, engine_name_, ini_params_, initConfigID_, debug_, *args, **kwargs):

        configIDValue = self.prepareIntArgument(initConfigID_)

        self._engine_name = self.prepareStringArgument(engine_name_)
        self._ini_params = self.prepareStringArgument(ini_params_)
        self._debug = debug_
        if self._debug:
            print("Initializing G2 diagnostic module")

        self._lib_handle.G2Diagnostic_initWithConfigID.argtypes = [c_char_p, c_char_p, c_longlong, c_int]
        ret_code = self._lib_handle.G2Diagnostic_initWithConfigID(self._engine_name, self._ini_params, configIDValue, self._debug)
        if self._debug:
            print("Initialization Status: " + str(ret_code))

        if ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    @deprecated(1203)
    def reinitV2(self, initConfigID_):
        self.reinit(initConfigID_)

    def reinit(self, initConfigID, *args, **kwargs):

        configIDValue = int(self.prepareStringArgument(initConfigID))

        self._lib_handle.G2Diagnostic_reinit.argtypes = [c_longlong]
        ret_code = self._lib_handle.G2Diagnostic_reinit(configIDValue)

        if ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def getEntityDetails(self, entityID, includeInternalFeatures, response, *args, **kwargs):
        # type: (int) -> str
        """ Get the details for the resolved entity
        Args:
            entityID: The entity ID to get results for
            includeInternalFeatures: boolean value indicating whether to include internal features
        """

        _includeInternalFeatures = self.prepareBooleanArgument(includeInternalFeatures)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getEntityDetails.argtypes = [c_longlong, c_int, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getEntityDetails(entityID, _includeInternalFeatures, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getRelationshipDetails(self, relationshipID, includeInternalFeatures, response, *args, **kwargs):
        # type: (int) -> str
        """ Get the details for the resolved entity relationship
        Args:
            relationshipID: The relationshp ID to get results for
            includeInternalFeatures: boolean value indicating whether to include internal features
        """

        _includeInternalFeatures = self.prepareBooleanArgument(includeInternalFeatures)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getRelationshipDetails.argtypes = [c_longlong, c_int, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getRelationshipDetails(relationshipID, _includeInternalFeatures, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getEntityResume(self, entityID, response, *args, **kwargs):
        # type: (int) -> str
        """ Get the related records for the resolved entity
        Args:
            entityID: The entity ID to get results for
        """

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getEntityResume.argtypes = [c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getEntityResume(entityID, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getEntityListBySize(self, entitySize, *args, **kwargs):
        """ Generate a list of resolved entities of a particular size

        Args:
            entitySize: The size of the resolved entity (observed entity count)
        """
        self._lib_handle.G2Diagnostic_getEntityListBySize.restype = c_int
        self._lib_handle.G2Diagnostic_getEntityListBySize.argtypes = [c_ulonglong, POINTER(c_void_p)]
        sizedEntityHandle = c_void_p(0)
        ret_code = self._lib_handle.G2Diagnostic_getEntityListBySize(entitySize, byref(sizedEntityHandle))

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        return sizedEntityHandle.value

    def fetchNextEntityBySize(self, sizedEntityHandle, response, *args, **kwargs):
        response[::] = b''
        self._lib_handle.G2Diagnostic_fetchNextEntityBySize.restype = c_int
        self._lib_handle.G2Diagnostic_fetchNextEntityBySize.argtypes = [c_void_p, c_char_p, c_size_t]
        resultValue = self._lib_handle.G2Diagnostic_fetchNextEntityBySize(c_void_p(sizedEntityHandle), tls_var.buf, sizeof(tls_var.buf))
        while resultValue != 0:

            if resultValue == -1:
                raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
            elif resultValue < 0:
                self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
                raise TranslateG2ModuleException(tls_var.buf.value)

            response += tls_var.buf.value
            if (response.decode())[-1] == '\n':
                break
            else:
                resultValue = self._lib_handle.G2Diagnostic_fetchNextEntityBySize(c_void_p(sizedEntityHandle), tls_var.buf, sizeof(tls_var.buf))
        return response

    def closeEntityListBySize(self, sizedEntityHandle, *args, **kwargs):
        self._lib_handle.G2Diagnostic_closeEntityListBySize.restype = c_int
        self._lib_handle.G2Diagnostic_closeEntityListBySize.argtypes = [c_void_p]
        self._lib_handle.G2Diagnostic_closeEntityListBySize(c_void_p(sizedEntityHandle))

    def checkDBPerf(self, secondsToRun, response, *args, **kwargs):
        # type: () -> object,int
        """ Retrieve JSON of DB performance test
        """

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_checkDBPerf.argtypes = [c_int, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_checkDBPerf(secondsToRun, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getDBInfo(self, response, *args, **kwargs):
        # type: () -> object,int
        """ Retrieve JSON of DB information
        """

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getDBInfo.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getDBInfo(pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getDataSourceCounts(self, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve record counts by data source and entity type.
        """

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getDataSourceCounts.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getDataSourceCounts(pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getMappingStatistics(self, includeInternalFeatures, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve data source mapping statistics.
        Args:
            includeInternalFeatures: boolean value indicating whether to include derived features
        """

        _includeInternalFeatures = self.prepareBooleanArgument(includeInternalFeatures)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getMappingStatistics.argtypes = [c_int, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getMappingStatistics(_includeInternalFeatures, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getGenericFeatures(self, featureType, maximumEstimatedCount, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve generic features.
        Args:
            featureType: the feature type to find generics for
            maximumEstimatedCount: the maximum estimated count for the generics to find
        """

        _featureType = self.prepareStringArgument(featureType)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getGenericFeatures.argtypes = [c_char_p, c_size_t, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getGenericFeatures(_featureType, maximumEstimatedCount, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getEntitySizeBreakdown(self, minimumEntitySize, includeInternalFeatures, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve data source mapping statistics.
        Args:
            minimumEntitySize: the minimum entity size to report on
            includeInternalFeatures: boolean value indicating whether to include derived features
        """

        _includeInternalFeatures = self.prepareBooleanArgument(includeInternalFeatures)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getEntitySizeBreakdown.argtypes = [c_size_t, c_int, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getEntitySizeBreakdown(minimumEntitySize, _includeInternalFeatures, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getFeature(self, libFeatID, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve feature information.
        Args:
            libFeatID: the feature ID to report on
        """

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getFeature.restype = c_int
        self._lib_handle.G2Diagnostic_getFeature.argtypes = [c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getFeature(
                                            libFeatID,
                                            pointer(responseBuf),
                                            pointer(responseSize),
                                            self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getResolutionStatistics(self, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve resolution statistics.
        """

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_getResolutionStatistics.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_getResolutionStatistics(pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def destroy(self, *args, **kwargs):
        """ Uninitializes the engine
        This should be done once per process after init(...) is called.
        After it is called the engine will no longer function.

        Args:

        Return:
            None
        """

        self._lib_handle.G2Diagnostic_destroy()

    def getPhysicalCores(self, *args, **kwargs):
        # type: () -> object
        """ Retrieve number of physical CPU cores

        Return:
            int: number of cores
        """

        self._lib_handle.G2Diagnostic_getPhysicalCores.argtypes = []
        return self._lib_handle.G2Diagnostic_getPhysicalCores()

    def getLogicalCores(self, *args, **kwargs):
        # type: () -> object
        """ Retrieve number of logical CPU cores

        Return:
            int: number of cores
        """

        self._lib_handle.G2Diagnostic_getLogicalCores.argtypes = []
        return self._lib_handle.G2Diagnostic_getLogicalCores()

    def getTotalSystemMemory(self, *args, **kwargs):
        # type: () -> object
        """ Retrieve total system memory

        Return:
            int: number of bytes
        """

        self._lib_handle.G2Diagnostic_getTotalSystemMemory.argtypes = []
        self._lib_handle.G2Diagnostic_getTotalSystemMemory.restype = c_longlong
        return self._lib_handle.G2Diagnostic_getTotalSystemMemory()

    def getAvailableMemory(self, *args, **kwargs):
        # type: () -> object
        """ Retrieve available memory

        Return:
            int: number of bytes
        """

        self._lib_handle.G2Diagnostic_getAvailableMemory.argtypes = []
        self._lib_handle.G2Diagnostic_getAvailableMemory.restype = c_longlong
        return self._lib_handle.G2Diagnostic_getAvailableMemory()

    @deprecated(1204)
    def clearLastException(self, *args, **kwargs):
        """ Clears the last exception
        """

        self._lib_handle.G2Diagnostic_clearLastException.restype = None
        self._lib_handle.G2Diagnostic_clearLastException.argtypes = []
        self._lib_handle.G2Diagnostic_clearLastException()

    @deprecated(1205)
    def getLastException(self, *args, **kwargs):
        """ Gets the last exception
        """

        self._lib_handle.G2Diagnostic_getLastException.restype = c_int
        self._lib_handle.G2Diagnostic_getLastException.argtypes = [c_char_p, c_size_t]
        self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
        resultString = tls_var.buf.value.decode('utf-8')
        return resultString

    @deprecated(1206)
    def getLastExceptionCode(self, *args, **kwargs):
        """ Gets the last exception code
        """

        self._lib_handle.G2Diagnostic_getLastExceptionCode.restype = c_int
        self._lib_handle.G2Diagnostic_getLastExceptionCode.argtypes = []
        exception_code = self._lib_handle.G2Diagnostic_getLastExceptionCode()
        return exception_code

    def findEntitiesByFeatureIDs(self, features, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve entities based on supplied features.
        Args:
            features: Json document containing an entity id (one to exclude) and list of features.
        """

        _features = self.prepareStringArgument(features)

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2Diagnostic_findEntitiesByFeatureIDs.argtypes = [c_char_p, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2Diagnostic_findEntitiesByFeatureIDs(_features, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Diagnostic has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2Diagnostic_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value
