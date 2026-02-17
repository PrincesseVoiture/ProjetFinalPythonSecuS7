# main.py
from fastapi import FastAPI, Header, HTTPException, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Agent
from schemas import AgentData
import datetime
from fastapi import Body

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()
AGENT_TOKEN = "secret123"

def auth_header(authorization: str = Header(...)):
    if not authorization or authorization.split(" ")[1] != AGENT_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/agent/data")
def update_agent_status(agent_data: AgentData, db=Depends(get_db), auth=Depends(auth_header)):
    agent = db.query(Agent).filter(Agent.id == agent_data.agent_id).first()
    if agent:
        agent.cpu = agent_data.cpu
        agent.ram = agent_data.ram
        agent.last_seen = datetime.datetime.utcnow()
        agent.status = "online"
    else:
        agent = Agent(
            id=agent_data.agent_id,
            cpu=agent_data.cpu,
            ram=agent_data.ram,
            status="online"
        )
        db.add(agent)
    db.commit()
    return {"status": "OK"}

@app.get("/agents")
def list_agents(db=Depends(get_db), auth=Depends(auth_header)):
    agents = db.query(Agent).all()
    return [{"hostname": a.id, "cpu": a.cpu, "ram": a.ram} for a in agents]


@app.post("/agent/command")
def add_command(agent_id: str = Body(...), command: str = Body(...), db=Depends(get_db), auth=Depends(auth_header)):
    from models import Command
    cmd = Command(agent_id=agent_id, command=command)
    db.add(cmd)
    db.commit()
    return {"status": "command added", "id": cmd.id}

@app.get("/agent/command/{agent_id}")
def get_command(agent_id: str, db=Depends(get_db), auth=Depends(auth_header)):
    from models import Command
    cmd = db.query(Command).filter(Command.agent_id == agent_id, Command.status == "pending").first()
    if cmd:
        return {"command": cmd.command, "id": cmd.id}
    return {"command": None, "id": None}

@app.post("/agent/result")
def submit_command_result(command_id: int = Body(...), output: str = Body(...), db=Depends(get_db), auth=Depends(auth_header)):
    from models import Command
    cmd = db.query(Command).filter(Command.id == command_id).first()
    if not cmd:
        return {"status": "command not found"}
    cmd.result = output
    cmd.status = "done"
    db.commit()
    return {"status": "result saved"}