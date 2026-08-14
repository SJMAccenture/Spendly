# Spec: Login and Logout

## Overview
Implement the `POST /login` handler and the `GET /logout` route so registered users can authenticate and end their session. The login form collects email and password, verifies credentials against the `users` table, and stores the user's `id` and `name` in Flask's `session` on success. Logout clears the session and redirects to the landing page. This completes the auth layer started in Step 2 (registration).

## Depends on
- Step 1 — DB setup (`get_db`, `init_db`, `users` table)
- Step 2 — Registration (`get_user_by_email`, `users` rows exist)

## Routes
- `POST /login` — process login form submission, set session on success — public
- `GET /logout` — clear session, redirect to `/` — logged-in (no hard guard yet, but clears session regardless)

## Database changes
No new tables or columns. One new helper function needed in `database/db.py`:
- `get_user_by_id(user_id)` — returns the matching `users` row or `None`; useful for future profile/dashboard lookups

## Templates
- **Modify:** `templates/login.html` — add `<form method="POST" action="{{ url_for('login') }}">` with fields `email` and `password`; add a flash message block above the form; add a link to `/register` for new users
- **Modify:** `templates/base.html` — update the nav so it shows a "Logout" link when `session.user_id` is set, and "Login" / "Register" links when it is not

## Files to change
- `app.py` — add `POST` to the `/login` route's `methods`; import `session`, `check_password_hash` (via werkzeug); implement POST handler: validate fields, look up user, verify hash, set `session["user_id"]` and `session["user_name"]`, redirect to `/profile` on success or re-render with flash on failure; implement `/logout` to call `session.clear()` and redirect to `url_for("landing")`
- `database/db.py` — add `get_user_by_id(user_id)`
- `templates/login.html` — add form and flash message display
- `templates/base.html` — add conditional nav links based on session state

## Files to create
None.

## New dependencies
No new pip packages. `werkzeug.security.check_password_hash` is already available via Flask's dependency.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only (`?` placeholders) — never f-strings in SQL
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plaintext
- Session keys: `session["user_id"]` (int) and `session["user_name"]` (str)
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `flash(message, "error")` for validation errors; render via `get_flashed_messages(with_categories=True)`
- Validate server-side: both fields required; if email not found or hash mismatch, show a single generic error ("Invalid email or password") — never reveal which field was wrong
- On login success: redirect to `url_for("profile")`
- On login failure: re-render `login.html` (URL stays `/login`)
- Logout must work via `GET /logout` and always redirect to `url_for("landing")`, even if no session is active
- Use `abort()` for unexpected HTTP errors — not bare string returns

## Definition of done
- [ ] Submitting the login form with a valid email and correct password sets a session and redirects to `/profile`
- [ ] Submitting with an unregistered email shows a generic flash error and stays on the login page
- [ ] Submitting with a correct email but wrong password shows the same generic flash error and stays on the login page
- [ ] Submitting with any blank field shows a flash error and stays on the login page
- [ ] Flash messages are visible on the page when validation fails
- [ ] `GET /logout` clears the session and redirects to the landing page
- [ ] After logout, revisiting `/logout` again still works (session already empty — no crash)
- [ ] The nav in `base.html` shows "Logout" when a user is logged in and "Login"/"Register" when not
- [ ] The form action uses `url_for("login")` — no hardcoded URLs
- [ ] `pytest` passes with no new failures
