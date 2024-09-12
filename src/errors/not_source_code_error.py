class NotSourceCodeError(Exception):
    """
    Custom exception raised when a file is not recognized as valid source code.

    This exception is used to handle cases where the content of a file is
    not identified as source code by the application, such as when the file
    has binary format or does not have correct language syntax.
    """
    pass
