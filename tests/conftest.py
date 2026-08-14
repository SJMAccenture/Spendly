import pytest
from werkzeug.security import generate_password_hash
from app import app as flask_app
from database.db import get_db, init_db


@pytest.fixture
def app(tmp_path, monkeypatch):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("database.db.DB_PATH", str(db_file))
    with flask_app.app_context():
        init_db()
        conn = get_db()
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Test User", "test@example.com", generate_password_hash("correct")),
        )
        conn.commit()
        conn.close()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
