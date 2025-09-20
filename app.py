from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "demo_secret_key"

DATA_FILE = "users.json"

# Initialize users.json if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

# Load & save functions
def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ---------------- Routes ---------------- #

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect("/dashboard")
        return "Invalid credentials 💀"
    return render_template("login.html")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users:
            return "User already exists 💀"
        users[username] = {"password": password, "balance": 1000, "transactions": []}
        save_users(users)
        session["username"] = username
        return redirect("/dashboard")
    return render_template("register.html")

# Logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    users = load_users()
    user = users[username]
    return render_template("dashboard.html",
                           username=username,
                           balance=user["balance"],
                           transactions=user["transactions"])

# Send Payment
@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    recipient = request.form["recipient"]
    try:
        amount = float(request.form["amount"])
    except:
        return "Invalid amount 💀"

    users = load_users()
    if recipient not in users:
        return "Recipient not found 💀"
    if users[username]["balance"] < amount:
        return "Insufficient balance 💀"

    # Update balances
    users[username]["balance"] -= amount
    users[username]["transactions"].append({"type": "Sent", "to": recipient, "amount": amount})

    users[recipient]["balance"] += amount
    users[recipient]["transactions"].append({"type": "Received", "from": username, "amount": amount})

    save_users(users)
    return redirect("/dashboard")

# -------------------------------------- #

if __name__ == "__main__":
    app.run(debug=True)