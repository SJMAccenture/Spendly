import pytest


def login(client):
    return client.post(
        "/login",
        data={"email": "test@example.com", "password": "correct"},
        follow_redirects=False,
    )


def test_profile_redirects_unauthenticated(client):
    response = client.get("/profile", follow_redirects=False)
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_profile_returns_200_when_authenticated(client):
    login(client)
    response = client.get("/profile")
    assert response.status_code == 200


def test_profile_shows_user_info(client):
    login(client)
    html = client.get("/profile").data.decode()
    assert "Simran Naidu" in html
    assert "simran.naidu279@gmail.com" in html


def test_profile_shows_category_badges(client):
    login(client)
    html = client.get("/profile").data.decode()
    assert "badge--food" in html


def test_profile_shows_category_breakdown(client):
    login(client)
    html = client.get("/profile").data.decode()
    assert "cat-row" in html
    assert "cat-fill" in html
