from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "IPSSI C COOL" 

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

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         username = request.form["username"]
#         password = request.form["password"]

#         # appel API pour authentification
#         try:
#             response = requests.post(f"{API_URL}/auth/login",
#                                      json={"username": username, "password": password})
#             if response.status_code == 200:
#                 token = response.json().get("token")
#                 session["user"] = username
#                 session["token"] = token  # stocke le token pour les futurs appels API
#                 return redirect("/dashboard")
#             else:
#                 error = "Login incorrect"
#         except:
#             error = "Impossible de joindre l'API"
#         return render_template("login.html", error=error)

#     return render_template("login.html")

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

    if "history" not in session:
        session["history"] = ["Bienvenue dans votre terminal Flask."]

    if request.method == "POST":
        cmd = request.form["command"]

        # simulation de l'API
        if cmd == "ls":
            result = "file1.txt\nfile2.txt\nscript.py"
        elif cmd == "whoami":
            result = session["user"]
        else:
            result = f"Commande simulée : {cmd}"

        # Ajouter la commande + sortie à l'historique
        session["history"].append(f"$ {cmd}\n{result}")

        # garder uniquement les 20 dernières lignes
        session["history"] = session["history"][-15:]

    # concaténer toutes les sorties pour affichage
    output = "\n".join(session["history"])

    return render_template("terminal.html", output=output, title="Terminal")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)