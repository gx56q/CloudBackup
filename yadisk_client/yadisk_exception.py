"""
YaDisk Exception module.

This module contains the YaDiskException class that handles the exceptions in YaDisk API.
"""


class YaDiskException(Exception):
    """Common exception class for YaDisk. Arg 'code' has the code of the HTTP Error."""

    def __init__(self, code, text):
        super().__init__(text)
        self.code = code

    def __str__(self):
        return f'Error {self.code}: {super().__str__()}'
