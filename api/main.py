from flask import Flask, request, jsonify
from models import Database
import datetime
from flask_cors import CORS
import sqlite3

app = Flask(__name__)

CORS(app,
     origins=[
         "http://127.0.0.1:5001",
         "http://localhost:5001"
     ],
     supports_credentials=True)

AGENT_TOKEN = "secret123" # TODO seems useless, to remove ?

db = Database()

def verify_agent_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header.split(" ")[1] != AGENT_TOKEN: # TODO check user token in database instead of useless hardcoded value
        return False
    return True


@app.route("/auth/login", methods=["POST"])
def login():
    """Vérifie login/password et retourne un token."""
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = db.run_query(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password),
        fetch=True
    )
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = user[0]["token"]
    return jsonify({"token": token})


@app.route("/fromagent/data", methods=["POST"])
def update_agent_status():
    if not verify_agent_token():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    agent_id = data.get("agent_id")
    cpu = data.get("cpu")
    ram = data.get("ram")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    existing = db.run_query("SELECT * FROM agents WHERE id = ?", (agent_id,), fetch=True)

    if existing:
        db.run_query(
            "UPDATE agents SET cpu = ?, ram = ?, last_seen = ?, status = 'online' WHERE id = ?",
            (cpu, ram, now, agent_id)
        )
    else:
        db.run_query(
            "INSERT INTO agents (id, cpu, ram, last_seen, status) VALUES (?, ?, ?, ?, 'online')",
            (agent_id, cpu, ram, now)
        )

    return jsonify({"status": "OK"})


@app.route("/agents", methods=["GET"])
def list_agents():
    # TODO uncomment when verify_agent_token() will be fixed
    #if not verify_agent_token():
    #   return jsonify({"error": "Unauthorized"}), 401
    
    rows = db.run_query("SELECT * FROM agents", fetch=True)
    agents = [{"hostname": r["id"], "cpu": r["cpu"], "ram": r["ram"]} for r in rows]

    return jsonify(agents)



@app.route("/agent/command", methods=["POST"])
def add_command():
    data = request.json
    agent_id = data.get("agent_id")
    command = data.get("command")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO commands (agent_id, command) VALUES (?, ?)", (agent_id, command))
    cmd_id = cursor.lastrowid  
    conn.commit()
    conn.close()
    print(f"idddddddd: {cmd_id}")

    return jsonify({"status": "command added", "id": cmd_id})


@app.route("/fromagent/getcommand/<agent_id>", methods=["GET"])
def get_command(agent_id: str):
    auth_header = request.headers.get("Authorization")
    print(f"DEBUGUUGUG GET /fromagent/getcommand/{agent_id} - Authorization header: {auth_header}")
    if not verify_agent_token():
        return jsonify({"error": "Unauthorized"}), 401

    rows = db.run_query(
        "SELECT * FROM commands WHERE agent_id = ? AND status = 'pending' ORDER BY id LIMIT 1",
        (agent_id,), fetch=True
    )

    if rows:
        row = rows[0]
        return jsonify({"command": row["command"], "id": row["id"]})

    return jsonify({"command": None, "id": None})

#changement
@app.route("/fromagent/result", methods=["POST"])
def submit_command_result():
    if not verify_agent_token():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    command_id = data.get("command_id")
    output = data.get("output")  

    print("COMMAND ID:", command_id)
    print("OUTPUT:", output)
    db.run_query(
        "UPDATE commands SET result = ?, status = 'done' WHERE id = ?",
        (output["stdout"], command_id)
    )

    return jsonify({"status": "result saved"})



@app.route("/agent/result/<int:command_id>", methods=["GET"])
def get_result(command_id):
    rows = db.run_query(
        "SELECT result FROM commands WHERE id = ?",
        (command_id,),
        fetch=True
    )
    if rows and rows[0]["result"] is not None:
        return jsonify({"result": rows[0]["result"]})
    return jsonify({"result": "Aucun résultat disponible"})



if __name__ == "__main__":
    app.run(port=5000, debug=True)