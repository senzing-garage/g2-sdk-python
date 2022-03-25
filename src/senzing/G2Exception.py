__all__ = [
    'G2BadInputException',
    'G2DBException',
    'G2DBMNotStarted',
    'G2DBNotFound',
    'G2DBUniqueConstraintViolation',
    'G2DBUnknownException',
    'G2Exception',
    'G2InvalidFileTypeContentsException',
    'G2ModuleEmptyMessage',
    'G2ModuleException',
    'G2ModuleGenericException',
    'G2ModuleInvalidXML',
    'G2ModuleLicenseException',
    'G2ModuleMySQLNoSchema',
    'G2ModuleNotInitialized',
    'G2ModuleResolveMissingResEnt',
    'G2RetryableException',
    'G2TableNoExist',
    'G2UnsupportedDatabaseType',
    'G2UnsupportedFileTypeException',
    'TranslateG2ModuleException',
    'UnconfiguredDataSourceException'
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
# Detail exceptions
# -----------------------------------------------------------------------------

# -- G2BadInputException ------------------------------------------------------


class G2DBUniqueConstraintViolation(G2BadInputException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2IncompleteRecordException(G2BadInputException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2InvalidFileTypeContentsException(G2BadInputException):

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


class G2UnsupportedFileTypeException(G2BadInputException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class UnconfiguredDataSourceException(G2BadInputException):

    def __init__(self, DataSourceName):
        super().__init__(self, ("Datasource %s not configured. See https://senzing.zendesk.com/hc/en-us/articles/360010784333 on how to configure datasources in the config file." % DataSourceName))

# -- G2DBException ------------------------------------------------------------


class G2DBException(G2Exception):
    '''Base exception for G2 DB related python code'''

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2DBMNotStarted(G2DBException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2DBNotFound(G2DBException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2DBUnknownException(G2DBException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2TableNoExist(G2DBException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)


class G2UnsupportedDatabaseType(G2DBException):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

# -- G2ModuleException --------------------------------------------------------


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
}


def TranslateG2ModuleException(exception_message):
    senzing_error_code = exception_message.split('|', 1)[0].strip()
    senzing_error_class = exceptions_map.get(senzing_error_code, G2Exception)
    return senzing_error_class(exception_message)
