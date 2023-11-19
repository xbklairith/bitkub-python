def test_client():
    import bitkub

    client = bitkub.Client(api_key="api-key", api_secret="api-secret")
    assert client._api_key == "api-key"
    assert client._api_secret == "api-secret"
