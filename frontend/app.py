from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "super-secret-key"  # pour les sessions

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["user"] = username
            return redirect("/dashboard")
        elif username == "Berzylyss" and password == "123456":
            session["user"] = username
            return redirect("/dashboard")        

    return render_template("login.html", title="Connexion")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    # Données simulées
    agents = [
        {"hostname": "PC1", "cpu": 23, "ram": 45},
        {"hostname": "PC2", "cpu": 12, "ram": 30},
        {"hostname": "PC3", "cpu": 67, "ram": 78}
    ]

    return render_template("dashboard.html", agents=agents, title="Dashboard")

@app.route("/terminal", methods=["GET", "POST"])
def terminal():
    if "user" not in session:
        return redirect("/login")

    output = ""

    if request.method == "POST":
        cmd = request.form["command"]

        # Simulation de l'API
        if cmd == "ls":
            output = "file1.txt\nfile2.txt\nscript.py"
        elif cmd == "whoami":
            output = "admin"
        else:
            output = f"Commande simulée : {cmd}"

    return render_template("terminal.html", output=output, title="Terminal")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)