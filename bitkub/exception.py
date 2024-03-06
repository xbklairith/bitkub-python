class BitkubException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):  # pragma: no cover
        return "RequestError: %s" % (self.message)
