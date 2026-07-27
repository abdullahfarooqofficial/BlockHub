from flask import Flask, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash
from flask_session import Session
import sqlite3

app = Flask(__name__)

# Session Configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database Connection
DATABASE = "database/blockhub.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# Home Page
@app.route("/")
def index():
    return render_template("index.html")



    
@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not email or not password or not confirmation:
            flash("Please fill in all fields.")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match.")
            return redirect("/register")

        conn = get_db_connection()

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

        flash("Registration successful!")
        return redirect("/login")

    return render_template("register.html")

@app.route("/test")
def test():
    return "It works!"

if __name__ == "__main__":
    app.run(debug=True)