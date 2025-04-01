def test_create_short_link_with_custom_alias(client):
    response = client.post("/links/shorten", json={
        "original_url": "https://example.com",
        "custom_alias": "testalias",
        "expires_at": "2025-05-31T12:46:57",
    })

    assert response.status_code == 200
    data = response.json()
    assert data["short_url"] == "testalias"
    assert "created_at" in data
    assert data["original_url"] == "https://example.com/"


def test_create_short_link_with_generated_code(client):
    response = client.post("/links/shorten", json={
        "original_url": "https://example.org",
        "custom_alias": "",
        "expires_at": "2025-05-31T12:46:57"
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["short_url"]) >= 6  # случайный short_code
    assert data["original_url"] == "https://example.org/"


def test_create_link_with_duplicate_alias(client):
    response = client.post("/links/shorten", json={
        "original_url": "https://another.com",
        "custom_alias": "testalias",
        "expires_at": "2025-05-31T12:46:57"
    })
    assert response.status_code == 409
    assert response.json()["detail"] == "Alias already exists"


def test_redirect_existing_short_code(client):
    response = client.get("/links/testalias")
    assert response.status_code == 200
    assert response.json()["Redirect"] == "https://example.com/"


def test_redirect_nonexistent_short_code(client):
    response = client.get("/nonexistent123")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_get_stats_for_existing_link(client):
    response = client.get("/links/testalias/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == "https://example.com/"
    assert "clicks" in data
    assert "created_at" in data


def test_get_stats_for_nonexistent_link(client):
    response = client.get("/doesnotexist/stats")
    assert response.status_code == 404
    assert response.json()["detail"] == "Not Found"


def test_search_nonexistent_link(client):
    response = client.get("/links/search/", params={"original_url": "https://doesnot.exist"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Link not found"


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




