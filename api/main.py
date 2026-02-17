from flask import Flask, request, jsonify
from models import run_query
import datetime

app = Flask(__name__)
AGENT_TOKEN = "secret123"

def verify_token():
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header.split(" ")[1] != AGENT_TOKEN:
        return False
    return True

@app.route("/agent/data", methods=["POST"])
def update_agent_status():
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    agent_id = data.get("agent_id")
    cpu = data.get("cpu")
    ram = data.get("ram")

    now = datetime.datetime.utcnow().isoformat()

    existing = run_query("SELECT * FROM agents WHERE id = ?", (agent_id,), fetch=True)

    if existing:
        run_query(
            "UPDATE agents SET cpu = ?, ram = ?, last_seen = ?, status = 'online' WHERE id = ?",
            (cpu, ram, now, agent_id)
        )
    else:
        run_query(
            "INSERT INTO agents (id, cpu, ram, last_seen, status) VALUES (?, ?, ?, ?, 'online')",
            (agent_id, cpu, ram, now)
        )

    return jsonify({"status": "OK"})


@app.route("/agents", methods=["GET"])
def list_agents():
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    rows = run_query("SELECT * FROM agents", fetch=True)
    agents = [{"hostname": r["id"], "cpu": r["cpu"], "ram": r["ram"]} for r in rows]

    return jsonify(agents)

@app.route("/agent/command", methods=["POST"])
def add_command():
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    agent_id = data.get("agent_id")
    command = data.get("command")

    run_query("INSERT INTO commands (agent_id, command) VALUES (?, ?)", (agent_id, command))
    cmd_id = run_query("SELECT last_insert_rowid() AS id", fetch=True)[0]["id"]

    return jsonify({"status": "command added", "id": cmd_id})


@app.route("/agent/command/<agent_id>", methods=["GET"])
def get_command(agent_id):
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    rows = run_query(
        "SELECT * FROM commands WHERE agent_id = ? AND status = 'pending' ORDER BY id LIMIT 1",
        (agent_id,), fetch=True
    )

    if rows:
        row = rows[0]
        return jsonify({"command": row["command"], "id": row["id"]})

    return jsonify({"command": None, "id": None})


@app.route("/agent/result", methods=["POST"])
def submit_command_result():
    if not verify_token():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    command_id = data.get("command_id")
    output = data.get("output")

    run_query(
        "UPDATE commands SET result = ?, status = 'done' WHERE id = ?",
        (output, command_id)
    )

    return jsonify({"status": "result saved"})


if __name__ == "__main__":
    app.run(debug=True)