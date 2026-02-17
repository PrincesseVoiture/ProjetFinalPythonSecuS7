# models.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True)
    last_seen = Column(DateTime, default=datetime.datetime.utcnow)
    cpu = Column(Float)
    ram = Column(Float)
    status = Column(String, default="offline")

class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String)
    command = Column(String)
    status = Column(String, default="pending")  # pending / done
    result = Column(String, nullable=True)