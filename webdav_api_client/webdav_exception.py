"""
WebDav Exception module.

This module contains the WebDavException class that handles the exceptions in WebDav API.
"""


class WebDavException(Exception):
    """Common exception class for WebDav. Arg 'code' has the code of the HTTP Error."""

    def __init__(self, code, text):
        super().__init__(text)
        self.code = code

    def __str__(self):
        return f'Error {self.code}: {super().__str__()}'
