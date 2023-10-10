__all__ = [

# -- Deprecated- -------------------------------------------------------------------------------
    'ExceptionCode',
    'ExceptionMessage',
    'G2BadInputException',
    'G2ConfigurationException',
    'G2DatabaseConnectionLost',
    'G2DatabaseException',
    'G2Exception',
    'G2IncompleteRecordException',
    'G2MalformedJsonException',
    'G2MessageBufferException',
    'G2MissingConfigurationException',
    'G2MissingDataSourceException',
    'G2ModuleEmptyMessage',
    'G2ModuleException',
    'G2ModuleGenericException',
    'G2ModuleInvalidXML',
    'G2ModuleLicenseException',
    'G2ModuleNotInitialized',
    'G2ModuleResolveMissingResEnt',
    'G2NotFoundException',
    'G2RepositoryPurgedException',
    'G2RetryableException',
    'G2RetryTimeoutExceeded',
    'G2UnacceptableJsonKeyValueException',
    'G2UnrecoverableException',
    'TranslateG2ModuleException',
    'G2UnknownDatasourceException',
    'G2LicenseException',
    'G2NotInitialized',
    'G2UnhandledException',
]

SENZING_PRODUCT_ID = "5044"  # See https://github.com/Senzing/knowledge-base/blob/main/lists/senzing-component-ids.md


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
# Base G2Exception
# -----------------------------------------------------------------------------


class G2Exception(Exception):
    """Base exception for G2 related python code."""

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        result = []
        for arg in self.args:
            message = arg
            if isinstance(arg, Exception):
                message = "{0}.{1}:".format(arg.__module__, arg.__class__.__name__)
            if message not in result:
                result.append(message)
        return " ".join(result)

# -----------------------------------------------------------------------------
# Category exceptions
# - These exceptions represent categories of actions that can be taken by
#   the calling program.
# -----------------------------------------------------------------------------


class G2BadInputException(G2Exception):
    """The user-supplied input contained an error."""


class G2ConfigurationException(G2Exception):
    """The program can provide a remedy and continue."""


class G2RetryableException(G2Exception):
    """The program can provide a remedy and continue."""


class G2UnrecoverableException(G2Exception):
    """System failure, can't continue."""

# -----------------------------------------------------------------------------
# Detail exceptions for G2BadInputException
# - Processing did not complete.
# - These exceptions are "per record" exceptions.
# - The record should be recorded as "bad".  (logged, queued as failure)
# - Processing may continue.
# -----------------------------------------------------------------------------


class G2NotFoundException(G2BadInputException):
    pass


class G2UnknownDatasourceException(G2BadInputException):
    pass


@deprecated(1010)
class G2IncompleteRecordException(G2BadInputException):
    pass


@deprecated(1011)
class G2MalformedJsonException(G2BadInputException):
    pass


@deprecated(1012)
class G2MissingConfigurationException(G2BadInputException):
    pass


@deprecated(1013)
class G2MissingDataSourceException(G2BadInputException):
    pass


@deprecated(1014)
class G2UnacceptableJsonKeyValueException(G2BadInputException):
    pass

# -----------------------------------------------------------------------------
# Detail exceptions for G2RetryableException
# - Processing did not complete.
# - These exceptions may be remedied programmatically.
# - The call to the Senzing method should be retried.
# - Processing may continue.
# -----------------------------------------------------------------------------


class G2DatabaseConnectionLost(G2RetryableException):
    pass


class G2RetryTimeoutExceeded(G2RetryableException):
    pass


@deprecated(1020)
class G2MessageBufferException(G2RetryableException):
    pass


@deprecated(1021)
class G2RepositoryPurgedException(G2RetryableException):
    pass

# -----------------------------------------------------------------------------
# Detail exceptions for G2UnrecoverableException
# - Processing did not complete.
# - These exceptions cannot be remedied programmatically.
# - Processing cannot continue.
# -----------------------------------------------------------------------------


class G2DatabaseException(G2UnrecoverableException):
    pass


class G2LicenseException(G2UnrecoverableException):
    pass


class G2NotInitialized(G2UnrecoverableException):
    pass


class G2UnhandledException(G2UnrecoverableException):
    pass


@deprecated(1030)
class G2ModuleException(G2Exception):
    """Base exception for G2 Module related python code."""


@deprecated(1031)
class G2ModuleEmptyMessage(G2UnrecoverableException):
    pass


@deprecated(1032)
class G2ModuleGenericException(G2UnrecoverableException):
    """Generic exception for non-subclassed G2 Module exception """


@deprecated(1033)
class G2ModuleInvalidXML(G2UnrecoverableException):
    pass


@deprecated(1034)
class G2ModuleLicenseException(G2UnrecoverableException):
    pass


@deprecated(1035)
class G2ModuleNotInitialized(G2UnrecoverableException):
    """G2 Module called but has not been initialized """


@deprecated(1036)
class G2ModuleResolveMissingResEnt(G2UnrecoverableException):
    pass

# -----------------------------------------------------------------------------
# Determine Exception based on Senzing reason code.
# Reference: https://senzing.zendesk.com/hc/en-us/articles/360026678133-Engine-Error-codes
# -----------------------------------------------------------------------------


exceptions_map = {
    1: G2ModuleInvalidXML,
    2: G2UnhandledException,
    7: G2ModuleEmptyMessage,
    10: G2RetryTimeoutExceeded,
    23: G2UnacceptableJsonKeyValueException,
    24: G2UnacceptableJsonKeyValueException,
    25: G2UnacceptableJsonKeyValueException,
    26: G2UnacceptableJsonKeyValueException,
    27: G2NotFoundException,
    32: G2UnacceptableJsonKeyValueException,
    33: G2NotFoundException,
    34: G2ConfigurationException,
    35: G2ConfigurationException,
    36: G2ConfigurationException,
    37: G2NotFoundException,
    47: G2ModuleGenericException,
    48: G2ModuleNotInitialized,
    49: G2ModuleNotInitialized,
    50: G2ModuleNotInitialized,
    51: G2UnacceptableJsonKeyValueException,
    53: G2ModuleNotInitialized,
    54: G2RepositoryPurgedException,
    61: G2ConfigurationException,
    62: G2ConfigurationException,
    63: G2ModuleNotInitialized,
    64: G2ConfigurationException,
    999: G2ModuleLicenseException,
    1001: G2DatabaseException,
    1007: G2DatabaseConnectionLost,
    2089: G2NotFoundException,
    2134: G2ModuleResolveMissingResEnt,
    2208: G2ConfigurationException,
    7221: G2ConfigurationException,
    7426: G2BadInputException,
    7344: G2NotFoundException,
    9000: G2ModuleLicenseException,
    30020: G2UnacceptableJsonKeyValueException,
    30110: G2MessageBufferException,
    30111: G2MessageBufferException,
    30112: G2MessageBufferException,
    30121: G2MalformedJsonException,
    30122: G2MalformedJsonException,
    30123: G2MalformedJsonException
}


def ExceptionMessage(exception):
    if exception is None:
        result = ''
    elif isinstance(exception, bytearray):
        result = exception.decode()
    elif isinstance(exception, bytes):
        result = exception.decode()
    elif isinstance(exception, Exception):
        result = str(exception).split(':', 1)[1].strip()
    else:
        result = exception
    assert(isinstance(result, str))
    return result


def ExceptionCode(exception):
    exception_message = ExceptionMessage(exception)
    exception_message_splits = exception_message.split('|', 1)
    result = int(exception_message_splits[0].strip().rstrip('EIW'))
    assert(isinstance(result, int))
    return result


def TranslateG2ModuleException(exception):
    senzing_error_code = ExceptionCode(exception)
    senzing_error_class = exceptions_map.get(senzing_error_code, G2Exception)
    return senzing_error_class(ExceptionMessage(exception))
