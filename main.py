import os
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# --- Config ---
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    message = Column(Text)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow React dev server and production frontend
origins = [
    "http://localhost:3000",  # React dev server
    # Add any others if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class MessageIn(BaseModel):
    name: str
    message: str

class MessageOut(BaseModel):
    id: int
    name: str
    message: str

# --- API Endpoints ---

@app.get("/api/messages", response_model=list[MessageOut])
def get_messages():
    session = SessionLocal()
    msgs = session.query(Message).order_by(Message.id.desc()).limit(20).all()
    session.close()
    return list(reversed([MessageOut(id=m.id, name=m.name, message=m.message) for m in msgs]))

@app.post("/api/messages", response_model=MessageOut)
def post_message(msg: MessageIn):
    session = SessionLocal()
    m = Message(name=msg.name, message=msg.message)
    session.add(m)
    session.commit()
    session.refresh(m)
    session.close()
    return MessageOut(id=m.id, name=m.name, message=m.message)
