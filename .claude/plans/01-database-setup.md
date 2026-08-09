# Plan: 01 — Database Setup

## Context

`database/db.py` is currently a stub (comments only). All future features — auth, profile, expense CRUD — depend on a working data layer. This step implements the three required helpers (`get_db`, `init_db`, `seed_db`) exactly as specified in `.claude/specs/01-databse-setup.md`, and wires them into `app.py` startup.

---

## Files Changed

| File | Change |
|---|---|
| `database/db.py` | Implemented all three functions from scratch |
| `app.py` | Added imports; called `init_db()` + `seed_db()` on startup |

---

## Implementation

### `database/db.py`

**Imports:**
- `sqlite3` (stdlib)
- `os` (to build absolute path to DB file)
- `werkzeug.security.generate_password_hash`

#### `get_db()`
- DB file: `spendly.db` at project root (one level above `database/`)
- `row_factory = sqlite3.Row` enables dict-like column access
- `PRAGMA foreign_keys = ON` on every connection (SQLite default is OFF)

#### `init_db()`
Creates both tables with `CREATE TABLE IF NOT EXISTS` — safe to call repeatedly.

- `users`: id, name, email (unique), password_hash, created_at
- `expenses`: id, user_id (FK → users), amount (REAL), category, date, description, created_at

#### `seed_db()`
1. Guard: `SELECT COUNT(*) FROM users` — if > 0, return early (no duplicates)
2. Inserts demo user: `"Demo User"`, `"demo@spendly.com"`, password `"demo123"` (hashed)
3. Inserts 8 expenses covering all 7 categories, dated 2026-08-01 through 2026-08-09

### `app.py`

Added import:
```python
from database.db import get_db, init_db, seed_db
```

Updated `__main__` block:
```python
if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
```

---

## Constraints Honoured

- Parameterized queries only — no f-strings or `.format()` in SQL
- `PRAGMA foreign_keys = ON` in every `get_db()` call
- `amount` stored as `REAL`, not `INTEGER`
- `seed_db()` guard prevents duplicate inserts on repeated startup
- No new pip packages — `sqlite3` is stdlib, `werkzeug` already in `requirements.txt`

---

## Status: Completed
