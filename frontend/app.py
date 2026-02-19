from flask import Flask, render_template, request, redirect, session
import requests, time
import os, secrets

API_URL = os.environ.get("API_URL", "http://api:5000")

app = Flask(__name__)
app.secret_key = "IPSSI C COOL" 

@app.route("/")
def home():
    return redirect("/login")

# Route to frontend /login
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
                session["token"] = secrets.token_hex(16)  
                requests.post(f"{API_URL}/auth/token", json={"username": username, "token": session["token"]})
                return redirect("/dashboard")
            else:
                error = "Login incorrect"
        except:
            error = "Impossible de joindre l'API"
        return render_template("login.html", error=error)

    return render_template("login.html")

# Route to frontend /dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session or "token" not in session:
        return redirect("/login")

    try:
        headers = {"Authorization": f"Bearer {session["token"]} {session["user"]}"}
        res = requests.get(f"{API_URL}/agents", headers=headers)
        agents = res.json()
    except Exception as e:
        print(e)
        agents = []

    return render_template("dashboard.html", agents=agents, API_URL=API_URL, title="Dashboard")

# Route to frontend /terminal
@app.route("/terminal", methods=["GET", "POST"])
def terminal():
    if "user" not in session or "token" not in session:
        return redirect("/login")

    # liste des agents depuis l'API
    try:
        headers = {"Authorization": f"Bearer {session["token"]} {session["user"]}"}
        res = requests.get(f"{API_URL}/agents", headers=headers)
        agents = res.json()  #  recup id agent 
    except:
        agents = []

    if "history" not in session:
        session["history"] = ["Bienvenue dans votre terminal Flask."]
    selected_agent_id = None

    if request.method == "POST":
        cmd = request.form["command"]
        selected_agent_id = request.form.get("agent_id", agents[0]["hostname"] if agents else None)

        if selected_agent_id:
            try:
                res = requests.post(
                    f"{API_URL}/agent/command",
                    headers=headers,
                    json={"agent_id": selected_agent_id, "command": cmd}
                )
                data = res.json()

                command_id = data.get('id')

                for _ in range(10):
                    res = requests.get(f"{API_URL}/agent/result", json={"command_id": command_id}, headers=headers).json()
                    result = res["result"]

                    if result != "Aucun résultat disponible":
                        break

                    time.sleep(0.2)

            except requests.exceptions.ConnectionError:
                result = f"Impossible de joindre l'API pour {selected_agent_id}"
        else:
            result = "Aucun agent disponible"

        session["history"].append(f"[{selected_agent_id}] $ {cmd}\n{result}")
        session["history"] = session["history"][-15:]
    else:
        # Si GET, on garde le1er agent par défaut
        selected_agent_id = agents[0]["hostname"] if agents else None


    output = "\n".join(session["history"])
    return render_template("terminal.html", API_URL=API_URL, output=output, agents=agents, selected_agent_id=selected_agent_id, title="Terminal")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
