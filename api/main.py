from fastapi import FastAPI, Header, HTTPException, Body
from models import run_query
import datetime

app = FastAPI()
AGENT_TOKEN = "secret123"

def verify_token(authorization: str = Header(...)):
    if not authorization or authorization.split(" ")[1] != AGENT_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/agent/data")
def update_agent_status(
    agent_id: str = Body(...),
    cpu: float = Body(...),
    ram: float = Body(...),
    authorization: str = Header(...)
):
    verify_token(authorization)
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

    return {"status": "OK"}

@app.get("/agents")
def list_agents(authorization: str = Header(...)):
    verify_token(authorization)
    rows = run_query("SELECT * FROM agents", fetch=True)
    return [{"hostname": r["id"], "cpu": r["cpu"], "ram": r["ram"]} for r in rows]


@app.post("/agent/command")
def add_command(
    agent_id: str = Body(...),
    command: str = Body(...),
    authorization: str = Header(...)
):
    verify_token(authorization)
    run_query("INSERT INTO commands (agent_id, command) VALUES (?, ?)", (agent_id, command))
    cmd_id = run_query("SELECT last_insert_rowid() AS id", fetch=True)[0]["id"]
    return {"status": "command added", "id": cmd_id}

@app.get("/agent/command/{agent_id}")
def get_command(agent_id: str, authorization: str = Header(...)):
    verify_token(authorization)
    rows = run_query(
        "SELECT * FROM commands WHERE agent_id = ? AND status = 'pending' ORDER BY id LIMIT 1",
        (agent_id,), fetch=True
    )
    if rows:
        row = rows[0]
        return {"command": row["command"], "id": row["id"]}
    return {"command": None, "id": None}

@app.post("/agent/result")
def submit_command_result(
    command_id: int = Body(...),
    output: str = Body(...),
    authorization: str = Header(...)
):
    verify_token(authorization)
    run_query(
        "UPDATE commands SET result = ?, status = 'done' WHERE id = ?",
        (output, command_id)
    )
    return {"status": "result saved"}