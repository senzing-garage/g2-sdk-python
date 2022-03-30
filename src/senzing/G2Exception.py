__all__ = [
    'G2BadInputException',
    'G2Exception',
    'G2ModuleEmptyMessage',
    'G2ModuleException',
    'G2ModuleGenericException',
    'G2ModuleInvalidXML',
    'G2ModuleLicenseException',
    'G2ModuleMySQLNoSchema',
    'G2ModuleNotInitialized',
    'G2ModuleResolveMissingResEnt',
    'G2RetryableException',
    'G2UnrecoverableException',
    'TranslateG2ModuleException'
]

# -----------------------------------------------------------------------------
# Base G2Exception
# -----------------------------------------------------------------------------


class G2Exception(Exception):
    '''Base exception for G2 related python code'''

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

# -----------------------------------------------------------------------------
# Category exceptions
# - These exceptions represent categories of actions that can be taken by
#   the calling program.
# - G2BadInputException - The user-supplied input contained an error.
# - G2RetryableException - The program can provide a remedy and continue.
# - G2UnrecoverableException - System failure; can't continue.
# -----------------------------------------------------------------------------


class G2BadInputException(G2Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2RetryableException(G2Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2UnrecoverableException(G2Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

# -----------------------------------------------------------------------------
# Detail exceptions for G2BadInputException
# - Processing did not complete.
# - These exceptions are "per record" exceptions.
# - The record should be recorded as "bad".  (logged, queued as failure)
# - Processing may continue.
# -----------------------------------------------------------------------------


class G2IncompleteRecordException(G2BadInputException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2MalformedJsonException(G2BadInputException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2MissingConfigurationException(G2BadInputException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2MissingDataSourceException(G2BadInputException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

# -----------------------------------------------------------------------------
# Detail exceptions for G2RetryableException
# - Processing did not complete.
# - These exceptions may be remedied programmatically.
# - The call to the Senzing method should be retried.
# - Processing may continue.
# -----------------------------------------------------------------------------

class G2MessageBufferException(G2RetryableException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

# -----------------------------------------------------------------------------
# Detail exceptions for G2UnrecoverableException
# - Processing did not complete.
# - These exceptions cannot be remedied programmatically.
# - Processing cannot continue.
# -----------------------------------------------------------------------------


class G2ModuleException(G2Exception):
    '''Base exception for G2 Module related python code'''

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2ModuleEmptyMessage(G2ModuleException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2ModuleGenericException(G2ModuleException):
    '''Generic exception for non-subclassed G2 Module exception '''

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2ModuleInvalidXML(G2ModuleException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2ModuleLicenseException(G2ModuleException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2ModuleMySQLNoSchema(G2ModuleException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2ModuleNotInitialized(G2ModuleException):
    '''G2 Module called but has not been initialized '''

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2ModuleResolveMissingResEnt(G2ModuleException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

# -----------------------------------------------------------------------------
# Determine Exception based on Senzing reason code.
# Reference: https://senzing.zendesk.com/hc/en-us/articles/360026678133-Engine-Error-codes
# -----------------------------------------------------------------------------


exceptions_map = {
    "0002E": G2ModuleInvalidXML,
    "0007E": G2ModuleEmptyMessage,
    "2134E": G2ModuleResolveMissingResEnt,
    "7213E": G2ModuleMySQLNoSchema,
    "9000E": G2ModuleLicenseException,

    "30121E": G2MalformedJsonException,
    "30122E": G2MalformedJsonException,

    "30110E": G2MessageBufferException,
    "30112E": G2MessageBufferException,


}


def TranslateG2ModuleException(exception_message):
    senzing_error_code = exception_message.split('|', 1)[0].strip()
    senzing_error_class = exceptions_map.get(senzing_error_code, G2Exception)
    return senzing_error_class(exception_message)
