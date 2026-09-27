import pytest


# ------------------------------------------------------------------ #
# GET /login                                                          #
# ------------------------------------------------------------------ #

def test_login_get_renders_form(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert b"email" in r.data
    assert b"password" in r.data


# ------------------------------------------------------------------ #
# POST /login — validation failures                                   #
# ------------------------------------------------------------------ #

def test_login_blank_fields_shows_error(client):
    r = client.post("/login", data={"email": "", "password": ""})
    assert r.status_code == 200
    assert b"required" in r.data.lower()


def test_login_blank_email_shows_error(client):
    r = client.post("/login", data={"email": "", "password": "correct"})
    assert r.status_code == 200
    assert b"required" in r.data.lower()


def test_login_blank_password_shows_error(client):
    r = client.post("/login", data={"email": "test@example.com", "password": ""})
    assert r.status_code == 200
    assert b"required" in r.data.lower()


def test_login_unknown_email_shows_generic_error(client):
    r = client.post("/login", data={"email": "nobody@example.com", "password": "correct"})
    assert r.status_code == 200
    assert b"Invalid email or password" in r.data


def test_login_wrong_password_shows_generic_error(client):
    r = client.post("/login", data={"email": "test@example.com", "password": "wrongpass"})
    assert r.status_code == 200
    assert b"Invalid email or password" in r.data


def test_login_error_does_not_reveal_which_field_wrong(client):
    r_bad_email = client.post("/login", data={"email": "nobody@example.com", "password": "x"})
    r_bad_pass  = client.post("/login", data={"email": "test@example.com",   "password": "x"})
    # Both should show the same message
    assert b"Invalid email or password" in r_bad_email.data
    assert b"Invalid email or password" in r_bad_pass.data


# ------------------------------------------------------------------ #
# POST /login — success                                               #
# ------------------------------------------------------------------ #

def test_login_valid_credentials_redirects_to_profile(client):
    r = client.post("/login", data={"email": "test@example.com", "password": "correct"})
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/profile")


def test_login_valid_credentials_sets_session(client):
    with client.session_transaction() as pre:
        assert "user_id" not in pre

    client.post("/login", data={"email": "test@example.com", "password": "correct"})

    with client.session_transaction() as post:
        assert post["user_id"] is not None
        assert post["user_name"] == "Test User"


# ------------------------------------------------------------------ #
# GET /logout                                                         #
# ------------------------------------------------------------------ #

def test_logout_redirects_to_landing(client):
    r = client.get("/logout")
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/")


def test_logout_clears_session(client):
    client.post("/login", data={"email": "test@example.com", "password": "correct"})
    with client.session_transaction() as sess:
        assert "user_id" in sess

    client.get("/logout")
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logout_without_session_does_not_crash(client):
    r = client.get("/logout")
    assert r.status_code == 302


# ------------------------------------------------------------------ #
# Nav conditional                                                     #
# ------------------------------------------------------------------ #

def test_nav_shows_login_register_when_logged_out(client):
    r = client.get("/")
    assert b"Sign in" in r.data or b"login" in r.data
    assert b"logout" not in r.data.lower()


def test_nav_shows_logout_when_logged_in(client):
    client.post("/login", data={"email": "test@example.com", "password": "correct"})
    r = client.get("/profile")
    assert b"Sign out" in r.data or b"logout" in r.data.lower()
    assert b"Test User" in r.data
