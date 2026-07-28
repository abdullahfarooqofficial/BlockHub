from flask import Flask, render_template, request, redirect, flash, session
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required, get_wallet_data
import sqlite3

app = Flask(__name__)

# Secret key for sessions and flash messages
app.secret_key = "blockhub_secret_key"

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database
DATABASE = "database/blockhub.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Home
@app.route("/")
def index():
    return render_template("index.html")

#Dashboard
@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db_connection()

    favourites = conn.execute(
        """
        SELECT *
        FROM favourites
        WHERE user_id = ?
        ORDER BY added_at DESC
        LIMIT 5
        """,
        (session["user_id"],)
    ).fetchall()

    history = conn.execute(
        """
        SELECT *
        FROM search_history
        WHERE user_id = ?
        ORDER BY searched_at DESC
        LIMIT 5
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        favourites=favourites,
        history=history
    )


# Login
@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Please fill in all fields.")
            return redirect("/login")

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user is None:
            flash("Invalid username.")
            return redirect("/login")

        if not check_password_hash(user["password_hash"], password):
            flash("Invalid password.")
            return redirect("/login")

        session["user_id"] = user["id"]

        flash("Welcome back!")
        return redirect("/dashboard")

    return render_template("login.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate input
        if not username or not email or not password or not confirmation:
            flash("Please fill in all fields.")
            return redirect("/register")

        # Check password confirmation
        if password != confirmation:
            flash("Passwords do not match.")
            return redirect("/register")

        conn = get_db_connection()

        # Check if username already exists
        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("Username already exists.")
            return redirect("/register")

        # Check if email already exists
        existing_email = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_email:
            conn.close()
            flash("Email already exists.")
            return redirect("/register")

        # Insert new user
        conn.execute(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
            """,
            (
                username,
                email,
                generate_password_hash(password)
            )
        )

        conn.commit()
        conn.close()

        flash("Registration successful! Please login.")
        return redirect("/login")

    return render_template("register.html")

#logout
@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")
    return redirect("/")


# Profile
@app.route("/profile")
@login_required
def profile():

    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    total_searches = conn.execute(
        """
        SELECT COUNT(*)
        FROM search_history
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    total_favourites = conn.execute(
        """
        SELECT COUNT(*)
        FROM favourites
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",
        user=user,
        total_searches=total_searches,
        total_favourites=total_favourites
    )

# Wallet
@app.route("/wallet")
@login_required
def wallet():

    address = request.args.get("address")
    network = request.args.get("network")


    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO search_history
        (user_id, wallet_address, network)

        VALUES (?, ?, ?)
        """,
        (
            session["user_id"],
            address,
            network
        )
    )

    conn.commit()
    conn.close()


    wallet_data = {

        "balance": "Loading...",
        "transactions": []

    }


    return render_template(
        "wallet.html",
        address=address,
        network=network,
        wallet_data=wallet_data
    )
   
#add favourite 
@app.route("/add_favourite", methods=["POST"])
@login_required
def add_favourite():

    address = request.form.get("address")
    network = request.form.get("network")

    conn = get_db_connection()

    existing = conn.execute(
    """
    SELECT *
    FROM favourites
    WHERE user_id = ?
    AND wallet_address = ?
    AND network = ?
    """,
    (
        session["user_id"],
        address,
        network
    )
    ).fetchone()

    if existing:
        conn.close()
        flash("Wallet is already in your favourites.")
        return redirect(f"/wallet?address={address}&network={network}")

    conn.execute(
        """
        INSERT INTO favourites (user_id, wallet_address, network)
        VALUES (?, ?, ?)
        """,
        (
            session["user_id"],
            address,
            network
        )
    )

    conn.commit()
    conn.close()

    flash("Wallet added to favourites.")

    return redirect(f"/wallet?address={address}&network={network}")

#remove favourite
@app.route("/remove_favourite/<int:id>", methods=["POST"])
@login_required
def remove_favourite(id):

    conn = get_db_connection()

    conn.execute(
        """
        DELETE FROM favourites
        WHERE id = ?
        AND user_id = ?
        """,
        (
            id,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash("Wallet removed from favourites.")

    return redirect("/dashboard")


# Test Route
@app.route("/test")
def test():
    return "It works!"


if __name__ == "__main__":
    app.run(debug=True)