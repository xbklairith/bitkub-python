# fixture
import pytest

import requests_mock


@pytest.fixture
def input_value():

    input = 39
    return input


@pytest.fixture
def mock_requests():
    import requests

    with requests_mock.Mocker() as mock:

        yield mock


@pytest.fixture
def mock_client(mock_requests):
    from bitkub import Client

    client = Client(api_key="api-key", api_secret="api-secret")
    return client


@pytest.fixture
def with_request_status_ok(mock_requests):
    mock_requests.get(
        "/api/status",
        json=[
            {"name": "Non-secure endpoints", "status": "ok", "message": ""},
            {"name": "Secure endpoints", "status": "ok", "message": ""},
        ],
    )


@pytest.fixture
def with_request_status_error(mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/status",
        json={"error": "Invalid API key"},
        status_code=400,
    )


@pytest.fixture
def with_request_status_invalid_json(mock_requests: requests_mock.Mocker):
    mock_requests.get(
        "/api/status",
        text="Invalid JSON",
        status_code=200,
    )
