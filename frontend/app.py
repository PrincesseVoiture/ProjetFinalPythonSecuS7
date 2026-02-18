from flask import Flask, render_template, request, redirect, session
import requests
import time

API_URL= "http://127.0.0.1:5000"

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
    except Exception as e:
        print(e)
        agents = []

    return render_template("dashboard.html", agents=agents, title="Dashboard")


@app.route("/terminal", methods=["GET", "POST"])
def terminal():
    if "user" not in session or "token" not in session:
        return redirect("/login")

    headers = {"Authorization": f"Bearer {session['token']}"}

    try:
        agents = requests.get(f"{API_URL}/agents", headers=headers).json()
    except:
        agents = []

    if "history" not in session:
        session["history"] = []

    selected_agent_id = agents[0]["hostname"] if agents else None

    if request.method == "POST":
        cmd = request.form["command"]
        selected_agent_id = request.form.get("agent_id", selected_agent_id)

        if not selected_agent_id:
            session["history"].append("Aucun agent disponible")
        else:
            try:
                res = requests.post(
                    f"{API_URL}/agent/command",
                    headers=headers,
                    json={"agent_id": selected_agent_id, "command": cmd}
                ).json()

                cmd_id = res.get("id")
                result = "En attente..."

                for _ in range(5):
                    time.sleep(1)
                    r = requests.get(
                        f"{API_URL}/agent/result/{cmd_id}",
                        headers=headers
                    ).json()

                    if r.get("result") and r["result"] != "Aucun résultat disponible":
                        result = r["result"]
                        break

                session["history"].append(f"[{selected_agent_id}] $ {cmd}\n{result}")

            except:
                session["history"].append(f"[{selected_agent_id}] $ {cmd}\nErreur API")

        session["history"] = session["history"][-20:]

    return render_template(
        "terminal.html",
        output="\n".join(session["history"]),
        agents=agents,
        selected_agent_id=selected_agent_id,
        title="Terminal"
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(port=5001, debug=True)