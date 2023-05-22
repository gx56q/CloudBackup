class YaDiskException(Exception):
    """Common exception class for YaDisk. Arg 'code' have code of HTTP Error."""
    code = None

    def __init__(self, code, text):
        super(YaDiskException, self).__init__(text)
        self.code = code

    def __str__(self):
        return f'Error {self.code}: {super(YaDiskException, self).__str__()}'
