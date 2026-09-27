"""
Tests for Step 06 — Date Filter for Profile Page.

Based on spec: .claude/specs/06-date-filter-for-profile.md

Reuses the `app` and `client` fixtures from conftest.py.
The conftest DB contains three expenses for "Test User":
  - Food       ₹450   2026-09-01
  - Transport  ₹120   2026-09-02
  - Bills      ₹800   2026-09-03
  Total all-time: ₹1,370
"""
import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def login(client):
    """Log in as the conftest test user."""
    return client.post(
        "/login",
        data={"email": "test@example.com", "password": "correct"},
        follow_redirects=False,
    )


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

class TestAuthGuard:
    def test_unauthenticated_get_redirects_to_login(self, client):
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 302, "Unauthenticated request must redirect"
        assert "/login" in response.headers["Location"], (
            "Redirect target should be the login page"
        )

    def test_unauthenticated_with_filter_params_redirects_to_login(self, client):
        response = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-03",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


# ---------------------------------------------------------------------------
# No filter params → all-time data, no badge, no Clear link
# ---------------------------------------------------------------------------

class TestNoFilter:
    def test_no_params_returns_200(self, client):
        login(client)
        response = client.get("/profile")
        assert response.status_code == 200

    def test_no_params_shows_all_time_total(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        # All three expenses: 450 + 120 + 800 = 1,370
        assert "1,370" in html, "All-time total should include all expenses"

    def test_no_params_shows_correct_transaction_count(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        # The conftest seeds exactly 3 expenses
        assert "3" in html, "Transaction count should be 3 for all-time view"

    def test_no_params_no_filtered_badge(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        # The spec requires a visible "Filtered" indicator only when a filter is active
        assert "Filtered" not in html, (
            "'Filtered' badge must not appear when no filter params are given"
        )

    def test_no_params_no_clear_link(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        # The "Clear" link should only be rendered when the filter is active
        assert "Clear" not in html, (
            "'Clear' link must not appear when no filter is active"
        )

    def test_no_params_shows_all_categories(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        assert "Food" in html
        assert "Transport" in html
        assert "Bills" in html


# ---------------------------------------------------------------------------
# Valid date range → filtered data, badge shown, Clear link visible
# ---------------------------------------------------------------------------

class TestValidFilter:
    def test_valid_range_returns_200(self, client):
        login(client)
        response = client.get("/profile?date_from=2026-09-01&date_to=2026-09-01")
        assert response.status_code == 200

    def test_valid_range_filters_stats_total(self, client):
        """Filter to a single day should show only that day's total."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-01"
        ).data.decode()
        # Only the Food expense on 2026-09-01 (₹450) should be included
        assert "450" in html, "Filtered total should reflect only expenses in range"

    def test_valid_range_filters_transaction_count(self, client):
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-01"
        ).data.decode()
        # Only 1 transaction on 2026-09-01
        assert "1" in html

    def test_valid_range_excludes_out_of_range_expenses(self, client):
        """Expenses outside the date range must not appear in the breakdown."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-01"
        ).data.decode()
        # Bills (800) and Transport (120) are outside this range
        assert "800" not in html, "Bills expense outside range must be excluded"

    def test_valid_full_range_shows_all_expenses(self, client):
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-03"
        ).data.decode()
        assert "1,370" in html, "Full range covering all expenses should match all-time total"

    def test_valid_range_shows_filtered_badge(self, client):
        """A visible 'Filtered' indicator must appear when a date range is active."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-03"
        ).data.decode()
        assert "Filtered" in html, "'Filtered' badge must be visible when filter is active"

    def test_valid_range_shows_clear_link(self, client):
        """A 'Clear' link must appear when a date range is active."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-03"
        ).data.decode()
        assert "Clear" in html, "'Clear' link must be visible when filter is active"

    def test_clear_link_points_to_profile_root(self, client):
        """The Clear link should navigate to /profile without query params."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-03"
        ).data.decode()
        # The href should be exactly /profile (no query string)
        assert 'href="/profile"' in html, (
            "Clear link must point to /profile without any query parameters"
        )

    def test_valid_range_same_dates_is_accepted(self, client):
        """date_from == date_to is a valid single-day filter."""
        login(client)
        response = client.get("/profile?date_from=2026-09-02&date_to=2026-09-02")
        assert response.status_code == 200
        html = response.data.decode()
        assert "Filtered" in html

    def test_valid_range_two_days_correct_total(self, client):
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-02"
        ).data.decode()
        # Food (450) + Transport (120) = 570
        assert "570" in html, "Two-day filter should sum only those two expenses"


# ---------------------------------------------------------------------------
# Date inputs pre-populated after filter submission
# ---------------------------------------------------------------------------

class TestInputPrePopulation:
    def test_date_from_value_in_html(self, client):
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-03"
        ).data.decode()
        assert 'value="2026-09-01"' in html, (
            "date_from input must be pre-populated with the submitted value"
        )

    def test_date_to_value_in_html(self, client):
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-01&date_to=2026-09-03"
        ).data.decode()
        assert 'value="2026-09-03"' in html, (
            "date_to input must be pre-populated with the submitted value"
        )

    def test_no_filter_inputs_have_no_stale_values(self, client):
        """Without a filter, the date inputs should not contain leftover values."""
        login(client)
        html = client.get("/profile").data.decode()
        # No injected date values in inputs
        assert 'value="2026-09-01"' not in html
        assert 'value="2026-09-03"' not in html


# ---------------------------------------------------------------------------
# Invalid range: date_from > date_to → flash error, all-time data rendered
# ---------------------------------------------------------------------------

class TestInvalidRange:
    def test_inverted_range_returns_200(self, client):
        """Page must not crash or 500 on an invalid date range."""
        login(client)
        response = client.get(
            "/profile?date_from=2026-09-03&date_to=2026-09-01",
            follow_redirects=True,
        )
        assert response.status_code == 200

    def test_inverted_range_shows_flash_error(self, client):
        """A flash error message must be shown for date_from > date_to."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-03&date_to=2026-09-01",
            follow_redirects=True,
        ).data.decode()
        # The spec says flash an error; common patterns include "error", "invalid", or "before"
        lower_html = html.lower()
        has_error_message = (
            "error" in lower_html
            or "invalid" in lower_html
            or "must be" in lower_html
            or "before" in lower_html
            or "date" in lower_html  # at minimum the word "date" in an error context
        )
        assert has_error_message, (
            "A flash/error message must appear when date_from is later than date_to"
        )

    def test_inverted_range_shows_all_time_data(self, client):
        """All-time data must be displayed (not filtered) after an invalid range."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-03&date_to=2026-09-01",
            follow_redirects=True,
        ).data.decode()
        assert "1,370" in html, (
            "All-time total must be rendered when filter range is invalid"
        )

    def test_inverted_range_does_not_show_filtered_badge(self, client):
        """The Filtered badge must NOT appear when the range was rejected as invalid."""
        login(client)
        html = client.get(
            "/profile?date_from=2026-09-03&date_to=2026-09-01",
            follow_redirects=True,
        ).data.decode()
        assert "Filtered" not in html, (
            "'Filtered' badge must not appear when the date range was rejected"
        )


# ---------------------------------------------------------------------------
# Single param supplied → treated as no filter (all-time data)
# ---------------------------------------------------------------------------

class TestSingleParamNoFilter:
    def test_only_date_from_returns_200(self, client):
        login(client)
        response = client.get("/profile?date_from=2026-09-01")
        assert response.status_code == 200

    def test_only_date_from_shows_all_time_data(self, client):
        login(client)
        html = client.get("/profile?date_from=2026-09-01").data.decode()
        assert "1,370" in html, (
            "Only date_from without date_to must show all-time data (no filter applied)"
        )

    def test_only_date_from_no_filtered_badge(self, client):
        login(client)
        html = client.get("/profile?date_from=2026-09-01").data.decode()
        assert "Filtered" not in html, (
            "'Filtered' badge must not appear when only one date param is supplied"
        )

    def test_only_date_to_returns_200(self, client):
        login(client)
        response = client.get("/profile?date_to=2026-09-03")
        assert response.status_code == 200

    def test_only_date_to_shows_all_time_data(self, client):
        login(client)
        html = client.get("/profile?date_to=2026-09-03").data.decode()
        assert "1,370" in html, (
            "Only date_to without date_from must show all-time data (no filter applied)"
        )

    def test_only_date_to_no_filtered_badge(self, client):
        login(client)
        html = client.get("/profile?date_to=2026-09-03").data.decode()
        assert "Filtered" not in html, (
            "'Filtered' badge must not appear when only one date param is supplied"
        )

    def test_only_date_from_no_clear_link(self, client):
        login(client)
        html = client.get("/profile?date_from=2026-09-01").data.decode()
        assert "Clear" not in html

    def test_only_date_to_no_clear_link(self, client):
        login(client)
        html = client.get("/profile?date_to=2026-09-03").data.decode()
        assert "Clear" not in html


# ---------------------------------------------------------------------------
# Empty result set within a valid range → ₹0.00, 0 transactions, no breakdown
# ---------------------------------------------------------------------------

class TestEmptyFilterResult:
    def test_range_with_no_expenses_returns_200(self, client):
        login(client)
        # A valid range in the future where no expenses exist
        response = client.get("/profile?date_from=2025-01-01&date_to=2025-01-31")
        assert response.status_code == 200

    def test_range_with_no_expenses_shows_zero_total(self, client):
        login(client)
        html = client.get(
            "/profile?date_from=2025-01-01&date_to=2025-01-31"
        ).data.decode()
        assert "₹0" in html or "0.00" in html, (
            "Total spent must show ₹0 when no expenses fall in the selected range"
        )

    def test_range_with_no_expenses_shows_filtered_badge(self, client):
        """Even with 0 results, the Filtered badge must appear (range was valid)."""
        login(client)
        html = client.get(
            "/profile?date_from=2025-01-01&date_to=2025-01-31"
        ).data.decode()
        assert "Filtered" in html

    def test_range_with_no_expenses_shows_clear_link(self, client):
        login(client)
        html = client.get(
            "/profile?date_from=2025-01-01&date_to=2025-01-31"
        ).data.decode()
        assert "Clear" in html


# ---------------------------------------------------------------------------
# Template contains date filter form landmarks
# ---------------------------------------------------------------------------

class TestFilterFormPresence:
    def test_profile_contains_date_from_input(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        assert 'name="date_from"' in html, (
            "Profile page must contain a date_from input field"
        )

    def test_profile_contains_date_to_input(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        assert 'name="date_to"' in html, (
            "Profile page must contain a date_to input field"
        )

    def test_profile_contains_apply_or_submit_button(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        lower_html = html.lower()
        assert "apply" in lower_html or 'type="submit"' in lower_html, (
            "Profile page must contain an Apply/submit button for the filter form"
        )

    def test_filter_form_method_is_get(self, client):
        login(client)
        html = client.get("/profile").data.decode()
        # The form must submit via GET so filters are bookmarkable
        assert 'method="get"' in html.lower() or "method='get'" in html.lower(), (
            "Filter form must use GET method so the filtered URL is bookmarkable"
        )
