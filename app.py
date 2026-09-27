from flask import Flask, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db, get_user_by_email, get_user_by_id, create_user

app = Flask(__name__)
app.secret_key = "spendly-dev-secret"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm:
            flash("All fields are required.", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if get_user_by_email(email):
            flash("An account with that email already exists.", "error")
            return render_template("register.html")

        create_user(name, email, generate_password_hash(password))
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("All fields are required.", "error")
            return render_template("login.html")

        user = get_user_by_email(email)
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_id"]   = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("profile"))

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user = {
        "name": "Simran Naidu",
        "email": "simran.naidu279@gmail.com",
        "member_since": "1 September 2026",
        "initials": "SN",
    }
    stats = {
        "total_spent": "₹12,450",
        "transactions": 18,
        "top_category": "Food",
    }
    expenses = [
        {"date": "23 Sep 2026", "description": "Grocery run",      "category": "Food",          "amount": "₹850"},
        {"date": "21 Sep 2026", "description": "Metro pass",       "category": "Transport",     "amount": "₹500"},
        {"date": "18 Sep 2026", "description": "Electricity bill", "category": "Bills",         "amount": "₹2,100"},
        {"date": "15 Sep 2026", "description": "Pharmacy",         "category": "Health",        "amount": "₹320"},
        {"date": "12 Sep 2026", "description": "Movie tickets",    "category": "Entertainment", "amount": "₹600"},
        {"date": "10 Sep 2026", "description": "Clothes",          "category": "Shopping",      "amount": "₹2,200"},
    ]
    categories = [
        {"name": "Food",          "amount": "₹3,200", "percent": 26},
        {"name": "Shopping",      "amount": "₹2,800", "percent": 22},
        {"name": "Bills",         "amount": "₹2,100", "percent": 17},
        {"name": "Transport",     "amount": "₹1,950", "percent": 16},
        {"name": "Health",        "amount": "₹1,400", "percent": 11},
        {"name": "Entertainment", "amount": "₹1,000", "percent":  8},
    ]
    return render_template("profile.html",
        user=user, stats=stats, expenses=expenses, categories=categories)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)
