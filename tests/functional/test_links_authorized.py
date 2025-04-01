import pytest


def login_and_get_token(client):
    client.post("/auth/register", json={
        "email": "secure@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", data={
        "username": "secure@example.com",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def auth_header(client):
    token = login_and_get_token(client)
    return {"Authorization": f"Bearer {token}"}


def test_update_link(client, auth_header):
    client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "testalias",
        "expires_at": "2025-05-31T12:46:57",
    }, headers=auth_header)

    response = client.put("/links/testalias", json={
        "new_url": "https://example.com"
    }, headers=auth_header)

    assert response.status_code == 200
    assert response.json()["message"] == "Link updated successfully"


def test_delete_link(client, auth_header):
    client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "testalias"
    }, headers=auth_header)

    response = client.delete("/links/testalias", headers=auth_header)
    assert response.status_code == 200
    assert response.json()["message"] == "Link deleted"


def test_get_archive(client, auth_header):
    response = client.get("/links/archive/", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
