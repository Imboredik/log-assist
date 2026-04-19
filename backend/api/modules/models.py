from sqlalchemy import Column, Integer, String, TIMESTAMP, Sequence, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, Sequence("users_id_seq"), nullable=False, unique=True, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    role_id = Column(Integer, nullable=False)
    password = Column(String, nullable=False)
    date_of_reg = Column(TIMESTAMP, nullable=False, unique=False)

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, Sequence("chats_id_seq"), nullable=False, primary_key=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String(20), nullable=True)
    date_of_create = Column(TIMESTAMP, nullable=False)
    service = Column(String(1000), nullable=True)
    summary = Column(String(10000), nullable=True)
    trace = Column(String(5000), nullable=True)
    back_logs = Column(String(10000), nullable=True)
    front_logs = Column(String(10000), nullable=True)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, Sequence("messages_id_seq"), nullable=False, unique=True, primary_key=True)
    chat_id = Column(Integer, nullable=False, unique=False)
    sender_type = Column(String, nullable=False, unique=False)
    content = Column(String, nullable=False, unique=False)
    date_of_create = Column(TIMESTAMP, nullable=False, unique=False)

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    priority_id = Column(Integer, nullable=False)
    date_of_create = Column(TIMESTAMP, nullable=False)
    service = Column(String(100), nullable=True)
    summary = Column(String(10000), nullable=True)
    trace = Column(String(5000), nullable=True)
    back_logs = Column(String(10000), nullable=True)
    front_logs = Column(String(10000), nullable=True)
    

class Priorities(Base):
    __tablename__ = "priorities"

    id = Column(Integer, primary_key=True)
    priority = Column(String(14), nullable=False)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    role = Column(String(60), nullable=False, unique=True)
    prompt = Column(String(10000), nullable=False, unique=True)
    description = Column(String(500), nullable=True)
    is_admin = Column(Boolean, nullable=False, unique=False)
