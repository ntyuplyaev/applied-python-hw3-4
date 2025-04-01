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
def project_header(client):
    token = login_and_get_token(client)
    return {"Authorization": f"Bearer {token}"}


def test_create_duplicate_project(client, project_header):
    client.post("/projects/", json={"name": "DuplicateProject"}, headers=project_header)
    response = client.post("/projects/", json={"name": "DuplicateProject"}, headers=project_header)
    assert response.status_code == 409
    assert response.json()["detail"] == "Project with this name already exists"


def test_create_project(client, project_header):
    response = client.post("/projects/", json={"name": "MyProject"}, headers=project_header)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "MyProject"
    assert "id" in data


def test_add_link_to_project(client, project_header):
    # Создаём ссылку
    client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "testalias",
        "expires_at": "2025-05-31T12:46:57",
    }, headers=project_header)

    # Создаём проект
    project_resp = client.post("/projects/", json={"name": "Proj1"}, headers=project_header)
    project_id = project_resp.json()["id"]

    # Добавляем ссылку
    response = client.post(f"/projects/{project_id}/links/testalias", headers=project_header)
    assert response.status_code == 200
    assert response.json()["message"] == "Link added to project"


def test_get_project(client, project_header):
    project_resp = client.post("/projects/", json={"name": "ProjectToRead"}, headers=project_header)
    project_id = project_resp.json()["id"]

    response = client.get(f"/projects/{project_id}", headers=project_header)
    assert response.status_code == 200
    assert response.json()["name"] == "ProjectToRead"