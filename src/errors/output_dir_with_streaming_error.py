class OutputDirWithStreamingError(Exception):
    """
    Custom exception raised when a output dir option is provided together with streaming. 
    There should only be one.
    """

    pass
