class BitkubException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):  # pragma: no cover
        return "RequestError: %s" % (self.message)


class BitkubAPIException(Exception):
    """
    Exception raised for known API errors.

    Attributes:
        message (str): The error message.
        code (int): The error code.
    """

    def __init__(self, message, code):
        self.message = message
        self.code = code

    def __str__(self):  # pragma: no cover
        return "BitkubAPIErrors:(%s) %s " % (self.code, self.message)
