class BitkubException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:  # pragma: no cover
        return f"RequestError: {self.message}"


class BitkubAPIException(Exception):
    """
    Exception raised for known API errors.

    Attributes:
        message (str): The error message.
        code (int): The error code.
    """

    def __init__(self, message: str, code: int) -> None:
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self) -> str:  # pragma: no cover
        return f"BitkubAPIErrors:({self.code}) {self.message} "
