from flask import Flask, render_template, request, redirect, session
import requests

API_URL= "http://127.0.0.1:5000"

app = Flask(__name__)
app.secret_key = "IPSSI C COOL" 

@app.route("/")
def home():
    return redirect("/login")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         if username == "admin" and password == "admin":
#             session["user"] = username
#             return redirect("/dashboard")
#         elif username == "Berzylyss" and password == "123456":
#             session["user"] = username
#             return redirect("/dashboard")        

#     return render_template("login.html", title="Connexion")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # appel API pour authentification
        try:
            response = requests.post(f"{API_URL}/auth/login",
                                     json={"username": username, "password": password})
            if response.status_code == 200:
                session["user"] = username
                session["token"] = response.json().get("token")
                return redirect("/dashboard")
            else:
                error = "Login incorrect"
        except:
            error = "Impossible de joindre l'API"
        return render_template("login.html", error=error)

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session or "token" not in session:
        return redirect("/login")

    try:
        headers = {"Authorization": f"Bearer {session['token']}"}
        res = requests.get(f"{API_URL}/agents", headers=headers)
        agents = res.json()
    except:
        agents = []

    return render_template("dashboard.html", agents=agents, title="Dashboard")

@app.route("/terminal", methods=["GET", "POST"])
def terminal():
    if "user" not in session or "token" not in session:
        return redirect("/login")

    if "history" not in session:
        session["history"] = ["Bienvenue dans votre terminal Flask."]

    if request.method == "POST":
        cmd = request.form["command"]
        try:
            headers = {"Authorization": f"Bearer {session['token']}"}
            res = requests.post(f"{API_URL}/agent/command", headers=headers, json={"agent_id": "007", "command" : cmd}) # TODO replace hardcoded 007 with the right computer's name
            data = res.json()
            result = data.get("message", "Erreur API")
        except:
            result = "Impossible de joindre l'API"

        # Ajouter la commande + sortie à l'historique
        session["history"].append(f"$ {cmd}\n{result}")
        session["history"] = session["history"][-15:]

    output = "\n".join(session["history"])
    return render_template("terminal.html", output=output, title="Terminal")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(port=5001, debug=True)