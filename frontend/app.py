from flask import Flask, render_template, request, redirect, session, url_for
import requests

app = Flask(__name__)
app.secret_key = "super-secret-key"  # pour les sessions

API_URL = "http://127.0.0.1:8000"  # ton backend API


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    try:
        response = requests.get(f"{API_URL}/agents")
        agents = response.json()
    except:
        agents = []

    return render_template("dashboard.html", agents=agents)

@app.route("/terminal", methods=["GET", "POST"])
def terminal():
    if "user" not in session:
        return redirect("/login")

    output = ""

    if request.method == "POST":
        cmd = request.form["command"]

        # envoyer commande à l’API
        try:
            response = requests.post(
                f"{API_URL}/command",
                json={"command": cmd}
            )
            output = response.json().get("output", "")
        except:
            output = "Erreur API"

    return render_template("terminal.html", output=output)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


if __name__ == "__main__":
    app.run(debug=True)