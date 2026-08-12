# Spec: Registration

## Overview
Implement the `POST /register` handler so users can create accounts. The form collects name, email, and password, validates the input server-side, hashes the password with werkzeug, and inserts the new user into the `users` table. On success the user is redirected to `/login`; on failure a flash message is shown and the form is re-displayed. This is the first half of the auth layer (Step 3 handles login and logout).

## Depends on
- Step 1 — DB setup (`get_db`, `init_db`, `users` table)

## Routes
- `POST /register` — process registration form submission — public

## Database changes
No new tables or columns. Two new helper functions needed in `database/db.py`:
- `get_user_by_email(email)` — returns the matching row or `None`; used to detect duplicate emails before inserting
- `create_user(name, email, password_hash)` — inserts a new row into `users` and returns the new `id`

## Templates
- **Modify:** `templates/register.html` — add a `<form method="POST" action="{{ url_for('register') }}">` with fields `name`, `email`, `password`, `confirm_password`; add a flash message block at the top of the form area

## Files to change
- `app.py` — set `app.secret_key`; add `POST` to the existing `/register` route's `methods`; import `redirect`, `url_for`, `flash`, `request`, `session` from flask; add `get_user_by_email`, `create_user` to the `database.db` import; implement the POST handler
- `database/db.py` — add `get_user_by_email()` and `create_user()`
- `templates/register.html` — add form and flash message display

## Files to create
None.

## New dependencies
No new pip packages. `werkzeug.security.generate_password_hash` is already available via Flask's dependency.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders) — never f-strings in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash` — never store plaintext
- `app.secret_key` must be set before any `flash()` or `session` call; use a hardcoded dev string for now (`"spendly-dev-secret"`)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `flash(message, "error")` for validation errors; render them in the template via `get_flashed_messages(with_categories=True)`
- Validate server-side: all fields required, passwords must match, email must not already exist
- On success: redirect to `url_for("login")`
- On failure: re-render `register.html` (so the form URL stays `/register`)
- Use `abort()` for unexpected HTTP errors — not bare string returns

## Definition of done
- [ ] Submitting the form with a new name, email, and matching passwords creates a row in `users` and redirects to `/login`
- [ ] The stored password field contains a hash, not the plaintext password
- [ ] Submitting with an email that already exists shows a flash error and stays on the registration page
- [ ] Submitting with mismatched passwords shows a flash error and stays on the registration page
- [ ] Submitting with any blank field shows a flash error and stays on the registration page
- [ ] The form action uses `url_for("register")` — no hardcoded URLs
- [ ] Flash messages are visible on the page when validation fails
- [ ] `GET /register` still renders the empty form without errors
- [ ] `pytest` passes with no new failures
