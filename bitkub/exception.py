class BitkubAPIExcption(Exception):
    def __init__(self, code, message):
        self.code = code or -1
        self.message = message

    def __str__(self):  # pragma: no cover
        return "APIError(code=%s): %s" % (self.code, self.message)


class BitkubException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):  # pragma: no cover
        return "RequestError: %s" % (self.message)
