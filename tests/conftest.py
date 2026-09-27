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
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Test User", "test@example.com", generate_password_hash("correct")),
        )
        user_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            [
                (user_id, 450.00, "Food",      "2026-09-01", "Grocery run"),
                (user_id, 120.00, "Transport", "2026-09-02", "Metro pass"),
                (user_id, 800.00, "Bills",     "2026-09-03", "Electricity"),
            ],
        )
        conn.commit()
        conn.close()
    flask_app.config["TESTING"] = True
    flask_app.config["WTF_CSRF_ENABLED"] = False
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
