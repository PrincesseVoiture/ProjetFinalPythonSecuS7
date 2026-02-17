from pydantic import BaseModel

class AgentData(BaseModel):
    agent_id: str
    cpu: float
    ram: float