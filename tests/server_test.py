def test_server_ready(client):
    """success case: server ready"""
    response = client.get(
        '/',
    )

    assert response.status_code == 200

    data = response.json
    assert data["status"] == "ready"
    assert data.get("time")
