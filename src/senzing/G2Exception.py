__all__ = [
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
    'G2UnacceptableJsonKeyValueException',
    'G2UnrecoverableException',
    'TranslateG2ModuleException',
]

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


class G2IncompleteRecordException(G2BadInputException):
    pass


class G2MalformedJsonException(G2BadInputException):
    pass


class G2MissingConfigurationException(G2BadInputException):
    pass


class G2MissingDataSourceException(G2BadInputException):
    pass


class G2UnacceptableJsonKeyValueException(G2BadInputException):
    pass


class G2NotFoundException(G2BadInputException):
    pass

# -----------------------------------------------------------------------------
# Detail exceptions for G2RetryableException
# - Processing did not complete.
# - These exceptions may be remedied programmatically.
# - The call to the Senzing method should be retried.
# - Processing may continue.
# -----------------------------------------------------------------------------


class G2ConfigurationException(G2RetryableException):
    pass


class G2DatabaseConnectionLost(G2RetryableException):
    pass


class G2MessageBufferException(G2RetryableException):
    pass


class G2RepositoryPurgedException(G2RetryableException):
    pass

# -----------------------------------------------------------------------------
# Detail exceptions for G2UnrecoverableException
# - Processing did not complete.
# - These exceptions cannot be remedied programmatically.
# - Processing cannot continue.
# -----------------------------------------------------------------------------


class G2ModuleException(G2Exception):
    """Base exception for G2 Module related python code."""


class G2ModuleEmptyMessage(G2UnrecoverableException):
    pass


class G2UnhandledException(G2UnrecoverableException):
    pass


class G2ModuleGenericException(G2UnrecoverableException):
    """Generic exception for non-subclassed G2 Module exception """


class G2ModuleInvalidXML(G2UnrecoverableException):
    pass


class G2ModuleLicenseException(G2UnrecoverableException):
    pass


class G2ModuleNotInitialized(G2UnrecoverableException):
    """G2 Module called but has not been initialized """


class G2ModuleResolveMissingResEnt(G2UnrecoverableException):
    pass


class G2DatabaseException(G2UnrecoverableException):
    pass

# -----------------------------------------------------------------------------
# Determine Exception based on Senzing reason code.
# Reference: https://senzing.zendesk.com/hc/en-us/articles/360026678133-Engine-Error-codes
# -----------------------------------------------------------------------------


exceptions_map = {
    "999E": G2ModuleLicenseException,
    "0001E": G2ModuleInvalidXML,
    "0002E": G2UnhandledException,
    "0007E": G2ModuleEmptyMessage,
    "0023E": G2UnacceptableJsonKeyValueException,
    "0024E": G2UnacceptableJsonKeyValueException,
    "0025E": G2UnacceptableJsonKeyValueException,
    "0026E": G2UnacceptableJsonKeyValueException,
    "0027E": G2NotFoundException,
    "0032E": G2UnacceptableJsonKeyValueException,
    "0033E": G2NotFoundException,
    "0034E": G2ConfigurationException,
    "0035E": G2ConfigurationException,
    "0036E": G2ConfigurationException,
    "0037E": G2NotFoundException,
    "0047E": G2ModuleGenericException,
    "0048E": G2ModuleNotInitialized,
    "0049E": G2ModuleNotInitialized,
    "0050E": G2ModuleNotInitialized,
    "0053E": G2ModuleNotInitialized,
    "0063E": G2ModuleNotInitialized,
    "0051E": G2UnacceptableJsonKeyValueException,
    "0054E": G2RepositoryPurgedException,
    "0061E": G2ConfigurationException,
    "0062E": G2ConfigurationException,
    "0064E": G2ConfigurationException,
    "1001E": G2DatabaseException,
    "1007E": G2DatabaseConnectionLost,
    "2089E": G2NotFoundException,
    "2134E": G2ModuleResolveMissingResEnt,
    "2208E": G2ConfigurationException,
    "7221E": G2ConfigurationException,
    "7344E": G2NotFoundException,
    "9000E": G2ModuleLicenseException,
    "30020": G2UnacceptableJsonKeyValueException,
    "30110E": G2MessageBufferException,
    "30111E": G2MessageBufferException,
    "30112E": G2MessageBufferException,
    "30121E": G2MalformedJsonException,
    "30122E": G2MalformedJsonException,
    "30123E": G2MalformedJsonException
}


def TranslateG2ModuleException(exception_message):

    if exception_message is None:
        exception_message_string = ''
    elif isinstance(exception_message, bytearray):
        exception_message_string = exception_message.decode()
    elif isinstance(exception_message, bytes):
        exception_message_string = exception_message.decode()
    else:
        exception_message_string = exception_message

    senzing_error_code = exception_message_string.split('|', 1)[0].strip()
    senzing_error_class = exceptions_map.get(senzing_error_code, G2Exception)

    return senzing_error_class(exception_message_string)
