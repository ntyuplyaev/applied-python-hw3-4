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


def test_update_link_unauthorized(client):
    response = client.put("/links/testalias", json={"new_url": "https://newurl.com"})
    assert response.status_code == 401


def test_delete_link_unauthorized(client):
    response = client.delete("/links/testalias")
    assert response.status_code == 401


def test_archive_requires_auth(client):
    response = client.get("/links/archive/")
    assert response.status_code == 401


def test_project_access_forbidden(client, auth_header):
    # Попробуем получить проект, которого нет
    response = client.get("/projects/9999", headers=auth_header)
    assert response.status_code == 404