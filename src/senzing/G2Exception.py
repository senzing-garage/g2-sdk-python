__all__ = [
    'G2Exception',
    'G2ModuleEmptyMessage',
    'G2ModuleException',
    'G2ModuleGenericException',
    'G2ModuleInvalidXML',
    'G2ModuleLicenseException',
    'G2ModuleMySQLNoSchema',
    'G2ModuleNotInitialized',
    'G2ModuleResolveMissingResEnt',
    'TranslateG2ModuleException',
]


class G2Exception(Exception):
    '''Base exception for G2 related python code'''

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class G2ModuleException(G2Exception):
    '''Base exception for G2 Module related python code'''

    def __init__(self, *args, **kwargs):
        G2Exception.__init__(self, *args, **kwargs)


class G2ModuleNotInitialized(G2ModuleException):
    '''G2 Module called but has not been initialized '''

    def __init__(self, *args, **kwargs):
        G2ModuleException.__init__(self, *args, **kwargs)


class G2ModuleGenericException(G2ModuleException):
    '''Generic exception for non-subclassed G2 Module exception '''

    def __init__(self, *args, **kwargs):
        G2ModuleException.__init__(self, *args, **kwargs)


class G2ModuleMySQLNoSchema(G2ModuleException):

    def __init__(self, *args, **kwargs):
        G2ModuleException.__init__(self, *args, **kwargs)


class G2ModuleEmptyMessage(G2ModuleException):

    def __init__(self, *args, **kwargs):
        G2ModuleException.__init__(self, *args, **kwargs)


class G2ModuleInvalidXML(G2ModuleException):

    def __init__(self, *args, **kwargs):
        G2ModuleException.__init__(self, *args, **kwargs)


class G2ModuleResolveMissingResEnt(G2ModuleException):

    def __init__(self, *args, **kwargs):
        G2ModuleException.__init__(self, *args, **kwargs)


class G2ModuleLicenseException(G2ModuleException):

    def __init__(self, *args, **kwargs):
        G2ModuleException.__init__(self, *args, **kwargs)


def TranslateG2ModuleException(ex, *args, **kwargs):
    exInfo = ex.decode().split('|', 1)
    if exInfo[0] == '7213E':
        return G2ModuleMySQLNoSchema(ex)
    elif exInfo[0] == '0002E':
        return G2ModuleInvalidXML(ex.decode())
    elif exInfo[0] == '0007E':
        return G2ModuleEmptyMessage(ex.decode())
    elif exInfo[0] == '2134E':
        return G2ModuleResolveMissingResEnt(ex.decode())
    elif exInfo[0] == '9000E':
        return G2ModuleLicenseException(ex.decode())
    else:
        return G2ModuleGenericException(ex.decode())
