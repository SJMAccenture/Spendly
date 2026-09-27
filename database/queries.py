from datetime import datetime

from database.db import get_db


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    """Returns the most recent expenses for a user, newest first."""
    conn = get_db()
    params = [user_id]
    date_clause = ""
    if date_from and date_to:
        date_clause = " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
    rows = conn.execute(
        "SELECT date, description, category, amount FROM expenses "
        f"WHERE user_id = ?{date_clause} ORDER BY date DESC LIMIT ?",
        params + [limit],
    ).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = datetime.strptime(r["date"], "%Y-%m-%d")
        result.append({
            "date": d.strftime("%#d %b %Y"),
            "description": r["description"] or "",
            "category": r["category"],
            "amount": f"₹{r['amount']:,.0f}",
        })
    return result


def get_summary_stats(user_id, date_from=None, date_to=None):
    """Returns total spent, transaction count, and top category for a user."""
    conn = get_db()
    params = [user_id]
    date_clause = ""
    if date_from and date_to:
        date_clause = " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
    row = conn.execute(
        f"SELECT SUM(amount) as total, COUNT(*) as cnt FROM expenses WHERE user_id = ?{date_clause}",
        params,
    ).fetchone()
    total = row["total"] or 0
    count = row["cnt"] or 0

    top_row = conn.execute(
        "SELECT category, SUM(amount) as cat_total FROM expenses "
        f"WHERE user_id = ?{date_clause} GROUP BY category ORDER BY cat_total DESC LIMIT 1",
        params,
    ).fetchone()
    conn.close()

    top_category = top_row["category"] if top_row else "—"
    return {
        "total_spent": f"₹{total:,.2f}",
        "transactions": count,
        "top_category": top_category,
    }


def get_category_breakdown(user_id, date_from=None, date_to=None):
    """Returns per-category spending totals and percentages, sorted by amount descending."""
    conn = get_db()
    params = [user_id]
    date_clause = ""
    if date_from and date_to:
        date_clause = " AND date BETWEEN ? AND ?"
        params.extend([date_from, date_to])
    rows = conn.execute(
        "SELECT category, SUM(amount) as total FROM expenses "
        f"WHERE user_id = ?{date_clause} GROUP BY category ORDER BY total DESC",
        params,
    ).fetchall()
    conn.close()

    if not rows:
        return []

    grand_total = sum(r["total"] for r in rows)
    result = []
    for r in rows:
        result.append({
            "name": r["category"],
            "amount": f"₹{r['total']:,.0f}",
            "percent": round(r["total"] / grand_total * 100),
        })

    # Largest category absorbs rounding remainder so percents always sum to 100
    current_sum = sum(c["percent"] for c in result)
    if current_sum != 100:
        result[0]["percent"] += (100 - current_sum)

    return result
