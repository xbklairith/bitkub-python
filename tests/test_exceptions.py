from bitkub.exception import BitkubAPIException, BitkubException


def test_bitkub_exception_creation():
    exception = BitkubException("Test error message")
    assert exception.message == "Test error message"


def test_bitkub_exception_str():
    exception = BitkubException("Test error message")
    assert str(exception) == "RequestError: Test error message"


def test_bitkub_api_exception_creation():
    exception = BitkubAPIException("API error message", 1001)
    assert exception.message == "API error message"
    assert exception.code == 1001


def test_bitkub_api_exception_str():
    exception = BitkubAPIException("API error message", 1001)
    assert str(exception) == "BitkubAPIErrors:(1001) API error message "


def test_bitkub_exception_inheritance():
    exception = BitkubException("Test message")
    assert isinstance(exception, Exception)


def test_bitkub_api_exception_inheritance():
    exception = BitkubAPIException("Test message", 1001)
    assert isinstance(exception, Exception)


def test_bitkub_exception_with_empty_message():
    exception = BitkubException("")
    assert exception.message == ""
    assert str(exception) == "RequestError: "


def test_bitkub_api_exception_with_zero_code():
    exception = BitkubAPIException("Success message", 0)
    assert exception.code == 0
    assert str(exception) == "BitkubAPIErrors:(0) Success message "


def test_bitkub_api_exception_with_negative_code():
    exception = BitkubAPIException("Error message", -1)
    assert exception.code == -1
    assert str(exception) == "BitkubAPIErrors:(-1) Error message "
