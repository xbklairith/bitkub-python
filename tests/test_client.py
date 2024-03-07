from bitkub import Client

import pytest

from bitkub.exception import BitkubException


def test_client():
    from bitkub import Client

    client = Client(api_key="api-key", api_secret="api-secret")
    assert client._api_key == "api-key"
    assert client._api_secret == "api-secret"


def test_get_status(mock_client: Client, with_request_status_ok: None):
    response = mock_client.status()
    assert response[0].get("status", {}) == "ok"


def test_get_status_error(mock_client: Client, with_request_status_error: None):
    # expect an exception to be raised on 400 status code
    with pytest.raises(BitkubException):
        mock_client.status()


def test_get_status_error_invalid_json(
    mock_client: Client, with_request_status_invalid_json: None
):
    # expect an exception to be raised on 400 status code
    with pytest.raises(BitkubException):
        mock_client.status()
