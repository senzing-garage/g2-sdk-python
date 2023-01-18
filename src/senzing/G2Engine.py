from ctypes import *
import threading
import json
import os
import functools
import warnings

from csv import reader as csvreader

from .G2Exception import TranslateG2ModuleException, G2ModuleNotInitialized, G2ModuleGenericException
from .G2EngineFlags import G2EngineFlags

__all__ = ['G2Engine']
SENZING_PRODUCT_ID = "5027"  # See https://github.com/Senzing/knowledge-base/blob/main/lists/senzing-product-ids.md


class MyBuffer(threading.local):

    def __init__(self):
        self.buf = create_string_buffer(65535)
        self.bufSize = sizeof(self.buf)
        # print("Created new Buffer {} of type {}".format(self.buf,type(self.buf)))


tls_var = MyBuffer()
tls_var3 = MyBuffer()


class MyBuffer2(threading.local):

    def __init__(self, g2_engine, size=65535):
        self.bufSize = c_size_t(size)
        g2_engine._lib_handle.G2_malloc.restype = c_void_p
        self.buf = g2_engine._lib_handle.G2_malloc(self.bufSize)
        # print("Created new Buffer {} of type {}".format(self.buf,type(self.buf)))


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


def resize_return_buffer3(buf_, size_):
    """  callback function that resizes return buffer when it is too small
    Args:
    size_: size the return buffer needs to be
    """
    try:
        if not tls_var3.buf:
            # print("New RESIZE_RETURN_BUF {}:{}".format(buf_,size_))
            tls_var3.buf = create_string_buffer(size_)
            tls_var3.bufSize = size_
        elif (tls_var3.bufSize < size_):
            # print("RESIZE_RETURN_BUF {}:{}/{}".format(buf_,size_,tls_var3.bufSize))
            foo = tls_var3.buf
            tls_var3.buf = create_string_buffer(size_)
            tls_var3.bufSize = size_
            memmove(tls_var3.buf, foo, sizeof(foo))
    except AttributeError:
        # print("AttributeError RESIZE_RETURN_BUF {}:{}".format(buf_,size_))
        tls_var3.buf = create_string_buffer(size_)
        # print("Created new Buffer {}".format(tls_var3.buf))
        tls_var3.bufSize = size_
    return addressof(tls_var3.buf)


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
# G2Engine class
# -----------------------------------------------------------------------------


class G2Engine(object):
    """G2 engine access library

    Attributes:
        _lib_handle: A boolean indicating if we like SPAM or not.
        _resize_func_def: resize function definiton
        _resize_func: resize function pointer
        _engine_name: CME engine name
        _ini_file_name: name and location of .ini file
    """

    def __init__(self, *args, **kwargs):
        # type: () -> None
        """ G2Engine class initialization
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
        self._resize_func_def3 = CFUNCTYPE(c_char_p, c_char_p, c_size_t)
        self._resize_func3 = self._resize_func_def(resize_return_buffer3)
        self._resize_func_def2 = CFUNCTYPE(c_void_p, c_void_p, c_size_t)
        self._resize_func2 = self._resize_func_def2(self._lib_handle.G2_realloc)

        self.tls_var2 = MyBuffer2(self)
        self.info_buf = MyBuffer2(self)

# -----------------------------------------------------------------------------
# Internal helper methods
# -----------------------------------------------------------------------------

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

    @deprecated(1001)
    def initV2(self, engine_name_, ini_params_, debug_=False):
        self.init(engine_name_, ini_params_, debug_)

    def init(self, engine_name_, ini_params_, debug_=False, *args, **kwargs):

        self._engine_name = self.prepareStringArgument(engine_name_)
        self._ini_params = self.prepareStringArgument(ini_params_)
        self._debug = debug_
        if self._debug:
            print("Initializing G2 engine")

        self._lib_handle.G2_init.argtypes = [c_char_p, c_char_p, c_int]
        ret_code = self._lib_handle.G2_init(self._engine_name, self._ini_params, self._debug)

        if self._debug:
            print("Initialization Status: " + str(ret_code))

        if ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    @deprecated(1002)
    def initWithConfigIDV2(self, engine_name_, ini_params_, initConfigID_, debug_):
        self.initWithConfigID(engine_name_, ini_params_, initConfigID_, debug_)

    def initWithConfigID(self, engine_name_, ini_params_, initConfigID_, debug_, *args, **kwargs):

        configIDValue = self.prepareIntArgument(initConfigID_)

        self._engine_name = self.prepareStringArgument(engine_name_)
        self._ini_params = self.prepareStringArgument(ini_params_)
        self._debug = debug_
        if self._debug:
            print("Initializing G2 engine")

        self._lib_handle.G2_initWithConfigID.argtypes = [c_char_p, c_char_p, c_longlong, c_int]
        ret_code = self._lib_handle.G2_initWithConfigID(self._engine_name, self._ini_params, configIDValue, self._debug)

        if self._debug:
            print("Initialization Status: " + str(ret_code))

        if ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    @deprecated(1003)
    def reinitV2(self, initConfigID_):
        self.reinit(initConfigID_)

    def reinit(self, initConfigID_, *args, **kwargs):

        configIDValue = self.prepareIntArgument(initConfigID_)

        self._lib_handle.G2_reinit.argtypes = [c_longlong]
        ret_code = self._lib_handle.G2_reinit(configIDValue)

        if ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    @deprecated(1022)
    def clearLastException(self, *args, **kwargs):
        """ Clears the last exception
        """

        self._lib_handle.G2_clearLastException.restype = None
        self._lib_handle.G2_clearLastException.argtypes = []
        self._lib_handle.G2_clearLastException()

    @deprecated(1023)
    def getLastException(self, *args, **kwargs):
        """ Gets the last exception
        """

        self._lib_handle.G2_getLastException.restype = c_int
        self._lib_handle.G2_getLastException.argtypes = [c_char_p, c_size_t]
        self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
        resultString = tls_var.buf.value.decode('utf-8')
        return resultString

    @deprecated(1024)
    def getLastExceptionCode(self, *args, **kwargs):
        """ Gets the last exception code
        """

        self._lib_handle.G2_getLastExceptionCode.restype = c_int
        self._lib_handle.G2_getLastExceptionCode.argtypes = []
        exception_code = self._lib_handle.G2_getLastExceptionCode()
        return exception_code

    def primeEngine(self, *args, **kwargs):
        ret_code = self._lib_handle.G2_primeEngine()
        if self._debug:
            print("Initialization Status: " + str(ret_code))

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def process(self, input_umf_, *args, **kwargs):
        # type: (str) -> None
        """ Generic process function without return
        This method will send a record for processing in g2.

        Args:
            record: An input record to be processed. Contains the data and control info.

        Return:
            None
        """

        input_umf_string = self.prepareStringArgument(input_umf_)
        self._lib_handle.G2_process.argtypes = [c_char_p]
        self._lib_handle.G2_process.restype = c_int
        ret_code = self._lib_handle.G2_process(input_umf_string)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def processWithInfo(self, input_umf_, response, flags=0, *args, **kwargs):
        # type: (str, str, int) -> int
        """ Generic process function without return
        This method will send a record for processing in g2.

        Args:
            record: An input record to be processed. Contains the data and control info.
            response: Json document with info about the modified resolved entities
            flags: reserved for future use

        Return:
            None
        """

        input_umf_string = self.prepareStringArgument(input_umf_)
        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_processWithInfo.argtypes = [c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_processWithInfo(input_umf_string, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    def processWithResponse(self, input_umf_, response, *args, **kwargs):
        """ Generic process function that returns results
        This method will send a record for processing in g2. It is a synchronous
        call, i.e. it will wait until g2 actually processes the record, and then
        optionally return any response message.

        Args:
            record: An input record to be processed. Contains the data and control info.
            response: If there is a response to the message it will be returned here.
                    Note there are performance benefits of calling the process method
                    that doesn't need a response message.
        """

        # type: (str) -> str
        """  resolves an entity synchronously
        Args:
            input_umf_: G2 style JSON
        """

        input_umf_string = self.prepareStringArgument(input_umf_)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_processWithResponseResize.argtypes = [c_char_p, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_processWithResponseResize(input_umf_string, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += responseBuf.value

    def checkRecord(self, input_umf_, recordQueryList, response, *args, **kwargs):
        # type: (str,str,str) -> str
        """ Scores the input record against the specified one
        Args:
            input_umf_: A JSON document containing the attribute information
                for the observation.
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
        """

        _inputUmfString = self.prepareStringArgument(input_umf_)
        _recordQueryList = self.prepareStringArgument(recordQueryList)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_checkRecord.argtypes = [c_char_p, c_char_p, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_checkRecord(_inputUmfString, _recordQueryList, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += responseBuf.value

    def exportJSONEntityReport(self, flags=G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS, *args, **kwargs):
        """ Generate a JSON export
        This is used to export entity data from known entities.  This function
        returns an export-handle that can be read from to get the export data
        in the requested format.  The export-handle should be read using the "G2_fetchNext"
        function, and closed when work is complete.
        """
        self._lib_handle.G2_exportJSONEntityReport.restype = c_int
        self._lib_handle.G2_exportJSONEntityReport.argtypes = [c_longlong, POINTER(c_void_p)]
        exportHandle = c_void_p(0)
        ret_code = self._lib_handle.G2_exportJSONEntityReport(flags, byref(exportHandle))

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        return exportHandle.value

    def exportCSVEntityReport(self, headersForCSV, flags=G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS, *args, **kwargs):
        """ Generate a CSV export
        This is used to export entity data from known entities.  This function
        returns an export-handle that can be read from to get the export data
        in the requested format.  The export-handle should be read using the "G2_fetchNext"
        function, and closed when work is complete.  Tthe first output row returned
        by the export-handle contains the CSV column headers as a string.  Each
        following row contains the exported entity data.
        """
        _headersForCSV = self.prepareStringArgument(headersForCSV)
        self._lib_handle.G2_exportCSVEntityReport.restype = c_int
        self._lib_handle.G2_exportCSVEntityReport.argtypes = [c_char_p, c_longlong, POINTER(c_void_p)]
        exportHandle = c_void_p(0)
        ret_code = self._lib_handle.G2_exportCSVEntityReport(_headersForCSV, flags, byref(exportHandle))

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        return exportHandle.value

    def fetchNext(self, exportHandle, response, *args, **kwargs):
        """ Fetch a record from an export
        Args:
            exportHandle: handle from generated export

        Returns:
            str: Record fetched, empty if there is no more data
        """
        response[::] = b''
        self._lib_handle.G2_fetchNext.restype = c_int
        self._lib_handle.G2_fetchNext.argtypes = [c_void_p, c_char_p, c_size_t]
        resultValue = self._lib_handle.G2_fetchNext(c_void_p(exportHandle), tls_var.buf, sizeof(tls_var.buf))
        while resultValue != 0:

            if resultValue == -1:
                raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
            elif resultValue < 0:
                self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
                raise TranslateG2ModuleException(tls_var.buf.value)

            response += tls_var.buf.value
            if (response)[-1] == 0x0a:
                break
            else:
                resultValue = self._lib_handle.G2_fetchNext(c_void_p(exportHandle), tls_var.buf, sizeof(tls_var.buf))
        return response

    def closeExport(self, exportHandle, *args, **kwargs):
        self._lib_handle.G2_closeExport.restype = c_int
        self._lib_handle.G2_closeExport.argtypes = [c_void_p]
        self._lib_handle.G2_closeExport(c_void_p(exportHandle))

    def addRecord(self, dataSourceCode, recordId, jsonData, load_id=None, *args, **kwargs):
        # type: (str,str,str,str) -> int
        """ Loads the JSON record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            jsonData: A JSON document containing the attribute information
                for the observation.
            load_id: The observation load ID for the record, can be null and will default to dataSourceCode
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _load_id = self.prepareStringArgument(load_id)
        _recordId = self.prepareStringArgument(recordId)
        _jsonData = self.prepareStringArgument(jsonData)
        self._lib_handle.G2_addRecord.restype = c_int
        self._lib_handle.G2_addRecord.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        ret_code = self._lib_handle.G2_addRecord(_dataSourceCode, _recordId, _jsonData, _load_id)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def addRecordWithReturnedRecordID(self, dataSourceCode, recordID, jsonData, load_id=None, *args, **kwargs):
        # type: (str,str,str,str) -> int
        """ Loads the JSON record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: A memory buffer for returning the recordID
            jsonData: A JSON document containing the attribute information
                for the observation.
            load_id: The observation load ID for the record, can be null and will default to dataSourceCode
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _jsonData = self.prepareStringArgument(jsonData)
        _load_id = self.prepareStringArgument(load_id)
        recordID[::] = b''
        self._lib_handle.G2_addRecordWithReturnedRecordID.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_size_t]
        ret_code = self._lib_handle.G2_addRecordWithReturnedRecordID(_dataSourceCode, _jsonData, _load_id, tls_var.buf, sizeof(tls_var.buf))

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        recordID += tls_var.buf.value

    def addRecordWithInfo(self, dataSourceCode, recordId, jsonData, response, load_id=None, flags=0, *args, **kwargs):
        # type: (str,str,str,str,str,int) -> str
        """ Loads the JSON record and returns info about the load
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            jsonData: A JSON document containing the attribute information
                for the observation.
            response: Json document with info about the modified resolved entities
            load_id: The observation load ID for the record, can be null and will default to dataSourceCode
            flags: reserved for future use
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _load_id = self.prepareStringArgument(load_id)
        _recordId = self.prepareStringArgument(recordId)
        _jsonData = self.prepareStringArgument(jsonData)
        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_addRecordWithInfo.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_addRecordWithInfo(_dataSourceCode, _recordId, _jsonData, _load_id, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    def addRecordWithInfoWithReturnedRecordID(self, dataSourceCode, jsonData, recordID, info, load_id=None, flags=0, *args, **kwargs):
        """ Loads the JSON record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: A memory buffer for returning the recordID
            jsonData: A JSON document containing the attribute information
                for the observation.
            info: Json document with info about the modified resolved entities
            load_id: The observation load ID for the record, can be null and will default to dataSourceCode
            flags: reserved for future use
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _jsonData = self.prepareStringArgument(jsonData)
        _load_id = self.prepareStringArgument(load_id)

        recordID[::] = b''

        info[::] = b''
        infoBuf = c_char_p(addressof(tls_var3.buf))
        infoBufSize = c_size_t(tls_var3.bufSize)

        self._lib_handle.G2_addRecordWithInfoWithReturnedRecordID.restype = c_int
        self._lib_handle.G2_addRecordWithInfoWithReturnedRecordID.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_char_p, c_size_t, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def3]
        ret_code = self._lib_handle.G2_addRecordWithInfoWithReturnedRecordID(_dataSourceCode, _jsonData, _load_id, flags, tls_var.buf, sizeof(tls_var.buf), pointer(infoBuf), pointer(infoBufSize), self._resize_func3)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        recordID += tls_var.buf.value
        info += tls_var3.buf.value

    def replaceRecord(self, dataSourceCode, recordId, jsonData, load_id=None, *args, **kwargs):
        # type: (str,str,str,str) -> int
        """ Replace the JSON record, loads if doesn't exist
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            jsonData: A JSON document containing the attribute information
                for the observation.
            load_id: The load ID for the record, can be null and will default to dataSourceCode
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _load_id = self.prepareStringArgument(load_id)
        _recordId = self.prepareStringArgument(recordId)
        _jsonData = self.prepareStringArgument(jsonData)
        ret_code = self._lib_handle.G2_replaceRecord(_dataSourceCode, _recordId, _jsonData, _load_id)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def replaceRecordWithInfo(self, dataSourceCode, recordId, jsonData, response, load_id=None, flags=0, *args, **kwargs):
        # type: (str,str,str,str) -> int
        """ Replace the JSON record, loads if doesn't exist
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            jsonData: A JSON document containing the attribute information
                for the observation.
            response: Json document with info about the modified resolved entities
            load_id: The load ID for the record, can be null and will default to dataSourceCode
            flags: reserved for future use
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _load_id = self.prepareStringArgument(load_id)
        _recordId = self.prepareStringArgument(recordId)
        _jsonData = self.prepareStringArgument(jsonData)
        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_replaceRecordWithInfo.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_replaceRecordWithInfo(_dataSourceCode, _recordId, _jsonData, _load_id, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    def deleteRecord(self, dataSourceCode, recordId, load_id=None, *args, **kwargs):
        # type: (str,str,str) -> int
        """ Delete the record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            load_id: The load ID for the record, can be null and will default to dataSourceCode
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _load_id = self.prepareStringArgument(load_id)
        _recordId = self.prepareStringArgument(recordId)
        ret_code = self._lib_handle.G2_deleteRecord(_dataSourceCode, _recordId, _load_id)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def deleteRecordWithInfo(self, dataSourceCode, recordId, response, load_id=None, flags=0, *args, **kwargs):
        # type: (str,str,str,str,int) -> int
        """ Delete the record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here
            load_id: The load ID for the record, can be null and will default to dataSourceCode
            flags: reserved for future use
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _load_id = self.prepareStringArgument(load_id)
        _recordId = self.prepareStringArgument(recordId)
        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_deleteRecordWithInfo.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_deleteRecordWithInfo(_dataSourceCode, _recordId, _load_id, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    def reevaluateRecord(self, dataSourceCode, recordId, flags=0, *args, **kwargs):
        # type: (str,str,int) -> int
        """ Reevaluate the JSON record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            flags: Bitwise control flags
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _recordId = self.prepareStringArgument(recordId)
        self._lib_handle.G2_reevaluateRecord.restype = c_int
        self._lib_handle.G2_reevaluateRecord.argtypes = [c_char_p, c_char_p, c_longlong]
        ret_code = self._lib_handle.G2_reevaluateRecord(_dataSourceCode, _recordId, flags)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def reevaluateRecordWithInfo(self, dataSourceCode, recordId, response, flags=0, *args, **kwargs):
        # type: (str,str,str,int) -> int
        """ Reevaluate the JSON record and return modified resolved entities
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            response: json document with modified resolved entities
            flags: Bitwise control flags
        """

        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _recordId = self.prepareStringArgument(recordId)
        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_reevaluateRecordWithInfo.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_reevaluateRecordWithInfo(_dataSourceCode, _recordId, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    def reevaluateEntity(self, entityID, flags=0, *args, **kwargs):
        # type: (int,int) -> int
        """ Reevaluate the JSON record
        Args:
            entityID: The entity ID to reevaluate.
            flags: Bitwise control flags
        """

        self._lib_handle.G2_reevaluateEntity.argtypes = [c_longlong, c_longlong]
        ret_code = self._lib_handle.G2_reevaluateEntity(entityID, flags)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def reevaluateEntityWithInfo(self, entityID, response, flags=0, *args, **kwargs):
        # type: (int,int,str) -> int
        """ Reevaluate the JSON record and return the modified resolved entities
        Args:
            entityID: The entity ID to reevaluate.

            response: json document with modified resolved entities
            flags: Bitwise control flags
        """

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_reevaluateEntityWithInfo.argtypes = [c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_reevaluateEntityWithInfo(entityID, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    @deprecated(1004)
    def searchByAttributesV2(self, jsonData, flags, response):
        self.searchByAttributes(jsonData, response, flags)

    def searchByAttributes(self, jsonData, response, flags=G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS, *args, **kwargs):
        # type: (str,bytearray) -> int
        """ Find records matching the provided attributes
        Args:
            jsonData: A JSON document containing the attribute information to search.
            flags: control flags.
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """
        response[::] = b''
        _jsonData = self.prepareStringArgument(jsonData)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_searchByAttributes_V2.argtypes = [c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_searchByAttributes_V2(_jsonData, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1005)
    def findPathByEntityIDV2(self, startEntityID, endEntityID, maxDegree, flags, response):
        self.findPathByEntityID(startEntityID, endEntityID, maxDegree, response, flags)

    def findPathByEntityID(self, startEntityID, endEntityID, maxDegree, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (int) -> str
        """ Find a path between two entities in the system.
        Args:
            startEntityID: The entity ID you want to find the path from
            endEntityID: The entity ID you want to find the path to
            maxDegree: The maximum path length to search for
            flags: control flags.
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findPathByEntityID_V2.restype = c_int
        self._lib_handle.G2_findPathByEntityID_V2.argtypes = [c_longlong, c_longlong, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findPathByEntityID_V2(startEntityID, endEntityID, maxDegree, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1006)
    def findNetworkByEntityIDV2(self, entityList, maxDegree, buildOutDegree, maxEntities, flags, response):
        self.findNetworkByEntityID(entityList, maxDegree, buildOutDegree, maxEntities, response, flags)

    def findNetworkByEntityID(self, entityList, maxDegree, buildOutDegree, maxEntities, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (int) -> str
        """ Find a network between entities in the system.
        Args:
            entityList: The entities to search for the network of
            maxDegree: The maximum path length to search for between entities
            buildOutDegree: The number of degrees to build out the surrounding network
            maxEntities: The maximum number of entities to include in the result
            flags: control flags.
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        _entityList = self.prepareStringArgument(entityList)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findNetworkByEntityID_V2.restype = c_int
        self._lib_handle.G2_findNetworkByEntityID_V2.argtypes = [c_char_p, c_int, c_int, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findNetworkByEntityID_V2(_entityList, maxDegree, buildOutDegree, maxEntities, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1007)
    def findPathByRecordIDV2(self, startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, flags, response):
        self.findPathByRecordID(startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, response, flags)

    def findPathByRecordID(self, startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (str,str) -> str
        """ Find a path between two records in the system.
        Args:
            startDataSourceCode: The data source for the record you want to find the path from
            startRecordID: The ID for the record you want to find the path from
            endDataSourceCode: The data source for the record you want to find the path to
            endRecordID: The ID for the record you want to find the path to
            maxDegree: The maximum path length to search for
            flags: control flags.
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        _startDsrcCode = self.prepareStringArgument(startDsrcCode)
        _startRecordId = self.prepareStringArgument(startRecordId)
        _endDsrcCode = self.prepareStringArgument(endDsrcCode)
        _endRecordId = self.prepareStringArgument(endRecordId)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findPathByRecordID_V2.restype = c_int
        self._lib_handle.G2_findPathByRecordID_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findPathByRecordID_V2(_startDsrcCode, _startRecordId, _endDsrcCode, _endRecordId, maxDegree, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1008)
    def findNetworkByRecordIDV2(self, recordList, maxDegree, buildOutDegree, maxEntities, flags, response):
        self.findNetworkByRecordID(recordList, maxDegree, buildOutDegree, maxEntities, response, flags)

    def findNetworkByRecordID(self, recordList, maxDegree, buildOutDegree, maxEntities, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (str,str) -> str
        """ Find a network between entities in the system.
        Args:
            recordList: The records to search for the network of
            maxDegree: The maximum path length to search for between entities
            buildOutDegree: The number of degrees to build out the surrounding network
            maxEntities: The maximum number of entities to include in the result
            flags: control flags.
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        _recordList = self.prepareStringArgument(recordList)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findNetworkByRecordID_V2.restype = c_int
        self._lib_handle.G2_findNetworkByRecordID_V2.argtypes = [c_char_p, c_int, c_int, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findNetworkByRecordID_V2(_recordList, maxDegree, buildOutDegree, maxEntities, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1009)
    def whyEntityByRecordIDV2(self, dataSourceCode, recordID, flags, response):
        self.whyEntityByRecordID(dataSourceCode, recordID, response, flags)

    def whyEntityByRecordID(self, dataSourceCode, recordID, response, flags=G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS, *args, **kwargs):

        response[::] = b''
        _dataSourceCode = self.prepareStringArgument(dataSourceCode)
        _recordID = self.prepareStringArgument(recordID)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_whyEntityByRecordID_V2.restype = c_int
        self._lib_handle.G2_whyEntityByRecordID_V2.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_whyEntityByRecordID_V2(_dataSourceCode, _recordID, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1010)
    def whyEntityByEntityIDV2(self, entityID, flags, response):
        self.whyEntityByEntityID(entityID, response, flags)

    def whyEntityByEntityID(self, entityID, response, flags=G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS, *args, **kwargs):

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_whyEntityByEntityID_V2.restype = c_int
        self._lib_handle.G2_whyEntityByEntityID_V2.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_whyEntityByEntityID_V2(entityID, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1011)
    def howEntityByEntityIDV2(self, entityID, flags, response):
        self.howEntityByEntityID(entityID, response, flags)

    def howEntityByEntityID(self, entityID, response, flags=G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS, *args, **kwargs):

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_howEntityByEntityID_V2.restype = c_int
        self._lib_handle.G2_howEntityByEntityID_V2.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_howEntityByEntityID_V2(entityID, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1012)
    def getVirtualEntityByRecordIDV2(self, recordList, flags, response):
        self.getVirtualEntityByRecordID(recordList, response, flags)

    def getVirtualEntityByRecordID(self, recordList, response, flags=G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS, *args, **kwargs):

        response[::] = b''
        _recordList = self.prepareStringArgument(recordList)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_getVirtualEntityByRecordID_V2.restype = c_int
        self._lib_handle.G2_getVirtualEntityByRecordID_V2.argtypes = [c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_getVirtualEntityByRecordID_V2(_recordList, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1013)
    def whyEntitiesV2(self, entityID1, entityID2, flags, response):
        self.whyEntities(entityID1, entityID2, response, flags)

    def whyEntities(self, entityID1, entityID2, response, flags=G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS, *args, **kwargs):

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_whyEntities_V2.restype = c_int
        self._lib_handle.G2_whyEntities_V2.argtypes = [c_longlong, c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_whyEntities_V2(entityID1, entityID2, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1014)
    def whyRecordsV2(self, dataSourceCode1, recordID1, dataSourceCode2, recordID2, flags, response):
        self.whyRecords(dataSourceCode1, recordID1, dataSourceCode2, recordID2, response, flags)

    def whyRecords(self, dataSourceCode1, recordID1, dataSourceCode2, recordID2, response, flags=G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS, *args, **kwargs):

        response[::] = b''
        _dataSourceCode1 = self.prepareStringArgument(dataSourceCode1)
        _recordID1 = self.prepareStringArgument(recordID1)
        _dataSourceCode2 = self.prepareStringArgument(dataSourceCode2)
        _recordID2 = self.prepareStringArgument(recordID2)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_whyRecords_V2.restype = c_int
        self._lib_handle.G2_whyRecords_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_whyRecords_V2(_dataSourceCode1, _recordID1, _dataSourceCode2, _recordID2, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1015)
    def findPathExcludingByEntityIDV2(self, startEntityID, endEntityID, maxDegree, excludedEntities, flags, response):
        self.findPathExcludingByEntityID(startEntityID, endEntityID, maxDegree, excludedEntities, response, flags)

    def findPathExcludingByEntityID(self, startEntityID, endEntityID, maxDegree, excludedEntities, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (int) -> str
        """ Find a path between two entities in the system.
        Args:
            startEntityID: The entity ID you want to find the path from
            endEntityID: The entity ID you want to find the path to
            maxDegree: The maximum path length to search for
            excludedEntities: JSON document containing entities to exclude
            flags: control flags
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        _excludedEntities = self.prepareStringArgument(excludedEntities)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findPathExcludingByEntityID_V2.restype = c_int
        self._lib_handle.G2_findPathExcludingByEntityID_V2.argtypes = [c_longlong, c_longlong, c_int, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findPathExcludingByEntityID_V2(startEntityID, endEntityID, maxDegree, _excludedEntities, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1016)
    def findPathIncludingSourceByEntityIDV2(self, startEntityID, endEntityID, maxDegree, excludedEntities, requiredDsrcs, flags, response):
        self.findPathIncludingSourceByEntityID(startEntityID, endEntityID, maxDegree, excludedEntities, requiredDsrcs, response, flags)

    def findPathIncludingSourceByEntityID(self, startEntityID, endEntityID, maxDegree, excludedEntities, requiredDsrcs, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (int) -> str
        """ Find a path between two entities in the system.
        Args:
            startEntityID: The entity ID you want to find the path from
            endEntityID: The entity ID you want to find the path to
            maxDegree: The maximum path length to search for
            excludedEntities: JSON document containing entities to exclude
            requiredDsrcs: JSON document containing data sources to require
            flags: control flags
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        _excludedEntities = self.prepareStringArgument(excludedEntities)
        _requiredDsrcs = self.prepareStringArgument(requiredDsrcs)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findPathIncludingSourceByEntityID_V2.restype = c_int
        self._lib_handle.G2_findPathIncludingSourceByEntityID_V2.argtypes = [c_longlong, c_longlong, c_int, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findPathIncludingSourceByEntityID_V2(startEntityID, endEntityID, maxDegree, _excludedEntities, _requiredDsrcs, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1017)
    def findPathExcludingByRecordIDV2(self, startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, excludedEntities, flags, response):
        self.findPathExcludingByRecordID(startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, excludedEntities, response, flags)

    def findPathExcludingByRecordID(self, startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, excludedEntities, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (str,str) -> str
        """ Find a path between two records in the system.
        Args:
            startDataSourceCode: The data source for the record you want to find the path from
            startRecordID: The ID for the record you want to find the path from
            endDataSourceCode: The data source for the record you want to find the path to
            endRecordID: The ID for the record you want to find the path to
            maxDegree: The maximum path length to search for
            excludedEntities: JSON document containing entities to exclude
            flags: control flags
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        _startDsrcCode = self.prepareStringArgument(startDsrcCode)
        _startRecordId = self.prepareStringArgument(startRecordId)
        _endDsrcCode = self.prepareStringArgument(endDsrcCode)
        _endRecordId = self.prepareStringArgument(endRecordId)
        _excludedEntities = self.prepareStringArgument(excludedEntities)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findPathExcludingByRecordID_V2.restype = c_int
        self._lib_handle.G2_findPathExcludingByRecordID_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findPathExcludingByRecordID_V2(_startDsrcCode, _startRecordId, _endDsrcCode, _endRecordId, maxDegree, _excludedEntities, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1018)
    def findPathIncludingSourceByRecordIDV2(self, startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, excludedEntities, requiredDsrcs, flags, response):
        self.findPathIncludingSourceByRecordID(startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, excludedEntities, requiredDsrcs, response, flags)

    def findPathIncludingSourceByRecordID(self, startDsrcCode, startRecordId, endDsrcCode, endRecordId, maxDegree, excludedEntities, requiredDsrcs, response, flags=G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS, *args, **kwargs):
        # type: (str,str) -> str
        """ Find a path between two records in the system.
        Args:
            startDataSourceCode: The data source for the record you want to find the path from
            startRecordID: The ID for the record you want to find the path from
            endDataSourceCode: The data source for the record you want to find the path to
            endRecordID: The ID for the record you want to find the path to
            maxDegree: The maximum path length to search for
            excludedEntities: JSON document containing entities to exclude
            requiredDsrcs: JSON document containing data sources to require
            flags: control flags
            response: A bytearray for returning the response document.
        """

        response[::] = b''
        _startDsrcCode = self.prepareStringArgument(startDsrcCode)
        _startRecordId = self.prepareStringArgument(startRecordId)
        _endDsrcCode = self.prepareStringArgument(endDsrcCode)
        _endRecordId = self.prepareStringArgument(endRecordId)
        _excludedEntities = self.prepareStringArgument(excludedEntities)
        _requiredDsrcs = self.prepareStringArgument(requiredDsrcs)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findPathIncludingSourceByRecordID_V2.restype = c_int
        self._lib_handle.G2_findPathIncludingSourceByRecordID_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findPathIncludingSourceByRecordID_V2(_startDsrcCode, _startRecordId, _endDsrcCode, _endRecordId, maxDegree, _excludedEntities, _requiredDsrcs, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    @deprecated(1019)
    def getEntityByEntityIDV2(self, entityID, flags, response):
        self.getEntityByEntityID(entityID, response, flags)

    def getEntityByEntityID(self, entityID, response, flags=G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS, *args, **kwargs):
        # type: (int,bytearray) -> int
        """ Find the entity with the given ID
        Args:
            entityID: The entity ID you want returned.  Typically referred to as
                    ENTITY_ID in JSON results.
            flags: control flags.
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_getEntityByEntityID_V2.restype = c_int
        self._lib_handle.G2_getEntityByEntityID_V2.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_getEntityByEntityID_V2(entityID, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    @deprecated(1020)
    def getEntityByRecordIDV2(self, dsrcCode, recordId, flags, response):
        self.getEntityByRecordID(dsrcCode, recordId, response, flags)

    def getEntityByRecordID(self, dsrcCode, recordId, response, flags=G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS, *args, **kwargs):
        # type: (str,str,bytearray) -> int
        """ Get the entity containing the specified record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            flags: control flags.
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        _dsrcCode = self.prepareStringArgument(dsrcCode)
        _recordId = self.prepareStringArgument(recordId)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_getEntityByRecordID_V2.restype = c_int
        self._lib_handle.G2_getEntityByRecordID_V2.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_getEntityByRecordID_V2(_dsrcCode, _recordId, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def findInterestingEntitiesByEntityID(self, entityID, response, flags=0, *args, **kwargs):
        # type: (int,bytearray) -> int
        """ Find interesting entities close to the entity with the given ID
        Args:
            entityID: The entity ID you want to search around.
            flags: control flags.
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findInterestingEntitiesByEntityID.restype = c_int
        self._lib_handle.G2_findInterestingEntitiesByEntityID.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findInterestingEntitiesByEntityID(entityID, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        # Add the bytes to the response bytearray from calling function
        response += tls_var.buf.value

    def findInterestingEntitiesByRecordID(self, dsrcCode, recordId, response, flags=0, *args, **kwargs):
        # type: (str,str,bytearray) -> int
        """ Find interesting entities close to the entity with the specified record
        Args:
            dataSourceCode: The data source for the observation to search around.
            recordID: The ID for the record to search around.
            flags: control flags.
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        _dsrcCode = self.prepareStringArgument(dsrcCode)
        _recordId = self.prepareStringArgument(recordId)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_findInterestingEntitiesByRecordID.restype = c_int
        self._lib_handle.G2_findInterestingEntitiesByRecordID.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_findInterestingEntitiesByRecordID(_dsrcCode, _recordId, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def getRedoRecord(self, response, *args, **kwargs):
        # type: (bytearray) -> int
        """ Get the next Redo record
        Args:
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_getRedoRecord.restype = c_int
        self._lib_handle.G2_getRedoRecord.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_getRedoRecord(pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += responseBuf.value

    def processRedoRecord(self, response, flags=0, *args, **kwargs):
        # type: (bytearray) -> int
        """ Process the next Redo record
        Args:
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_processRedoRecord.restype = c_int
        self._lib_handle.G2_processRedoRecord.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_processRedoRecord(pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += responseBuf.value

    def processRedoRecordWithInfo(self, response, info, flags=0, *args, **kwargs):
        # type: (bytearray) -> int
        """ Process the next Redo record
        Args:
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
            response: A bytearray for returning the info about changed resolved entities
        """

        response[::] = b''
        info[::] = b''
        responseBuf = c_char_p(self.tls_var2.buf)
        infoBuf = c_char_p(self.info_buf.buf)

        self._lib_handle.G2_processRedoRecordWithInfo.restype = c_int
        self._lib_handle.G2_processRedoRecordWithInfo.argtypes = [c_longlong, POINTER(c_char_p), POINTER(c_size_t), POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def2]
        ret_code = self._lib_handle.G2_processRedoRecordWithInfo(flags, pointer(responseBuf), pointer(self.tls_var2.bufSize), pointer(infoBuf), pointer(self.info_buf.bufSize), self._resize_func2)
        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += responseBuf.value
        info += infoBuf.value

    def countRedoRecords(self, *args, **kwargs):
        # type: () -> int
        """ Get the redo records left
        Args:

        Return:
            int: the number of redo records in the queue.
        """

        ret_code = self._lib_handle.G2_countRedoRecords()

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        return ret_code

    @deprecated(1021)
    def getRecordV2(self, dsrcCode, recordId, flags, response):
        self.getRecord(dsrcCode, recordId, response, flags)

    def getRecord(self, dsrcCode, recordId, response, flags=G2EngineFlags.G2_RECORD_DEFAULT_FLAGS, *args, **kwargs):
        # type: (str,str,bytearray) -> int
        """ Get the specified record
        Args:
            dataSourceCode: The data source for the observation.
            recordID: The ID for the record
            flags: control flags.
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        _dsrcCode = self.prepareStringArgument(dsrcCode)
        _recordId = self.prepareStringArgument(recordId)
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_getRecord_V2.restype = c_int
        self._lib_handle.G2_getRecord_V2.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_getRecord_V2(_dsrcCode, _recordId, flags, pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def stats(self, response, *args, **kwargs):
        # type: () -> object
        """ Retrieve the workload statistics for the current process.
        Resets them after retrieved.

        Args:

        """

        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_stats.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_stats(pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

    def exportConfig(self, response, configID, *args, **kwargs):
        # type: (bytearray) -> int
        """ Retrieve the G2 engine configuration

        Args:
            response: A bytearray for returning the response document; if an error occurred, an error response is stored here.
        """

        response[::] = b''
        responseBuf = c_char_p(addressof(tls_var.buf))
        responseSize = c_size_t(tls_var.bufSize)
        self._lib_handle.G2_exportConfig.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        ret_code = self._lib_handle.G2_exportConfig(pointer(responseBuf), pointer(responseSize), self._resize_func)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        response += tls_var.buf.value

        if type(configID) == bytearray:
            configID[::] = b''
            cID = c_longlong(0)
            self._lib_handle.G2_getActiveConfigID.argtypes = [POINTER(c_longlong)]
            ret_code2 = self._lib_handle.G2_getActiveConfigID(cID)

            if ret_code2 == -1:
                raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
            elif ret_code2 < 0:
                self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
                raise TranslateG2ModuleException(tls_var.buf.value)

            configID += (str(cID.value).encode())

    def getActiveConfigID(self, configID, *args, **kwargs):
        # type: (bytearray) -> object
        """ Retrieve the active config ID for the G2 engine

        Args:
            configID: A bytearray for returning the identifier value for the config
        """

        configID[::] = b''
        cID = c_longlong(0)
        self._lib_handle.G2_getActiveConfigID.argtypes = [POINTER(c_longlong)]
        ret_code = self._lib_handle.G2_getActiveConfigID(cID)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        configID += (str(cID.value).encode())

    def getRepositoryLastModifiedTime(self, lastModifiedTime, *args, **kwargs):
        # type: (bytearray) -> object
        """ Retrieve the last modified time stamp of the entity store repository

        Args:
            lastModifiedTime: A bytearray for returning the last modified time of the data repository
        """

        lastModifiedTime[::] = b''
        lastModifiedTimeStamp = c_longlong(0)
        self._lib_handle.G2_getRepositoryLastModifiedTime.argtypes = [POINTER(c_longlong)]
        ret_code = self._lib_handle.G2_getRepositoryLastModifiedTime(lastModifiedTimeStamp)

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

        lastModifiedTime += (str(lastModifiedTimeStamp.value).encode())

    def purgeRepository(self, reset_resolver_=True, *args, **kwargs):
        # type: (bool) -> None
        """ Purges the G2 repository

        Args:
            reset_resolver: Re-initializes the engine.  Should be left True.

        Return:
            None
        """

        ret_code = self._lib_handle.G2_purgeRepository()

        if ret_code == -1:
            raise G2ModuleNotInitialized('G2Engine has not been successfully initialized')
        elif ret_code < 0:
            self._lib_handle.G2_getLastException(tls_var.buf, sizeof(tls_var.buf))
            raise TranslateG2ModuleException(tls_var.buf.value)

    def destroy(self, *args, **kwargs):
        """ Uninitializes the engine
        This should be done once per process after init(...) is called.
        After it is called the engine will no longer function.

        Args:

        Return:
            None
        """

        self._lib_handle.G2_destroy()
