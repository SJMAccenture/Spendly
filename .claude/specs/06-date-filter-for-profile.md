# Spec: Date Filter for Profile Page

## Overview
Step 6 adds a date-range filter to the profile page so users can narrow all
three data sections — summary stats, recent transactions, and category
breakdown — to a chosen time window. The filter is driven entirely by GET
query parameters (`date_from`, `date_to`) so the filtered view is bookmarkable
and the form submits with a normal browser GET. When no dates are supplied the
page continues to show all-time data, preserving backwards compatibility.

## Depends on
- Step 1: Database setup (`expenses` table with a `date` TEXT column exists)
- Step 3: Login / Logout (`session["user_id"]` set on login)
- Step 5: Backend connection (live query helpers in `database/queries.py`)

## Routes
No new routes. The existing `GET /profile` route is modified to accept optional
query parameters:
- `date_from` — ISO date string `YYYY-MM-DD` (inclusive lower bound)
- `date_to`   — ISO date string `YYYY-MM-DD` (inclusive upper bound)

## Database changes
No database changes. The `expenses.date` column (`TEXT`, stored as `YYYY-MM-DD`)
already supports lexicographic range filtering with `BETWEEN`.

## Templates
- **Modify:** `templates/profile.html`
  - Add a filter form above the stats row containing two `<input type="date">`
    fields (labelled "From" and "To") and an "Apply" submit button.
  - Add a "Clear" link that resets to `/profile` (no query params).
  - Pre-populate the date inputs with the current `date_from` / `date_to`
    values so the form reflects the active filter after submission.
  - When a filter is active, display a visible "Filtered" badge or note near
    the stats row so users know the figures are not all-time.

## Files to change
- `app.py` — read `date_from` and `date_to` from `request.args` in the
  `profile()` view and pass them through to every query helper call.
- `database/queries.py` — add optional `date_from` and `date_to` parameters
  to `get_recent_transactions`, `get_summary_stats`, and
  `get_category_breakdown`; default both to `None` (no filtering).
- `templates/profile.html` — add the date filter form and conditional
  "Filtered" indicator as described above.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format values into SQL
- Use SQL `BETWEEN ? AND ?` for date filtering; both bounds are inclusive
- Validate that `date_from <= date_to` in the route; if invalid, flash an
  error and render the page without filtering (show all-time data)
- `date_from` and `date_to` default to `None`; when `None` the SQL WHERE
  clause must not be altered — do not pass empty strings to the database
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No inline styles (the `<style>` block already in `profile.html` for
  `--pct` variables is an existing exception; do not add new ones)
- Currency must always display as ₹

## Definition of done
- [ ] Visiting `/profile` with no query params shows all-time data unchanged
- [ ] Submitting the filter form with a valid date range reloads the page and
  all three sections (stats, transactions, breakdown) reflect only expenses
  within that range
- [ ] The date inputs are pre-populated with the submitted values after filtering
- [ ] A "Filtered" indicator is visible on the page when a date range is active
- [ ] The "Clear" link removes the filter and restores all-time data
- [ ] Submitting `date_from` later than `date_to` shows a flash error and
  renders all-time data (no crash, no empty page)
- [ ] A user with no expenses in the selected range sees ₹0.00 total spent,
  0 transactions, and an empty category breakdown — no errors
- [ ] The filter works correctly for the seed user when filtered to August 2026
  (all 8 seed expenses fall in that range)
