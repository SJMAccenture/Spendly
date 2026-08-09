# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Spendly** — a personal expense tracker web app built with Python/Flask and SQLite. The project is structured as a step-by-step build-out; many routes and database functions are stubs to be filled in incrementally.

## Setup & Commands

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Run the app
python app.py                # http://localhost:5001

# Run tests
pytest

# Run a single test file
pytest tests/test_routes.py

# Run a single test
pytest tests/test_routes.py::test_name
```

## Architecture

**Flask + Jinja2 + SQLite — no frontend build system.**

- `app.py` — all routes defined here; runs on port 5001 with `debug=True`
- `database/db.py` — SQLite helpers (`get_db`, `init_db`, `seed_db`); currently a stub
- `templates/` — Jinja2 templates using inheritance from `base.html`
- `static/css/style.css` — custom design system using CSS custom properties (no CSS framework)
- `static/js/main.js` — vanilla JS placeholder

**Route status:** GET routes for `/`, `/login`, `/register`, `/terms`, `/privacy` render templates. Routes for logout, profile, and all expense CRUD (`/expenses/add`, `/expenses/<id>/edit`, `/expenses/<id>/delete`) are stubs returning plain strings, to be implemented in later steps.

**Database:** SQLite file `expense_tracker.db` (gitignored). `get_db()` in `database/db.py` is expected to enable foreign keys and set `row_factory = sqlite3.Row`.

## Design System

CSS custom properties defined in `static/css/style.css`:
- Colors: `--ink`, `--ink-soft`, `--ink-muted`, `--ink-faint`, `--paper`, `--paper-warm`, `--paper-card`, `--accent` (`#1a472a` dark green), `--accent-2` (`#c17f24` amber), `--danger`
- Fonts: `--font-display` (DM Serif Display), `--font-body` (DM Sans) — loaded via Google Fonts in `base.html`
- Currency: Indian Rupees (₹)

## Planned Build Steps

Steps are numbered in `app.py` comments: Step 1 = DB setup, Steps 2–3 = auth (register/login POST handlers, logout), Step 4 = profile, Steps 7–9 = expense CRUD (add, edit, delete). A dashboard/expense list route is implied but not yet stubbed.
