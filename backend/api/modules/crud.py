from sqlalchemy.orm import Session
from fastapi import HTTPException
from jose import jwt, JWTError
from datetime import datetime, timezone
from uuid import uuid4 # Временное решение

from . import models, schemas, utils
from .config import config_values


# Пользователь
def get_user_by_token(db:Session, token: str) -> models.User | None:
    """Получение из базы данных информации о пользователе по токену"""
    try:
        payload = jwt.decode(token, config_values.SECRET_KEY, algorithms=[config_values.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise HTTPException(status_code=400, detail="Некорректный токен")
    except JWTError:
        raise HTTPException(status_code=400, detail="Не авторизован")
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Получение из базы данных информации о пользователе по почте"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str) -> models.User | None:
    """Получение из базы данных информации о пользователе по имени пользователя"""
    return db.query(models.User).filter(models.User.username == username).first()

def add_new_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Создание нового пользователя по классу информации о нём"""
    db_user = models.User(
        email=user.email,
        username=user.username,
        role_id=user.role_id,
        password=utils.password_hash(user.password),
        date_of_reg=datetime.now()
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Чат
def get_chat_by_id(db: Session, chat_id: int) -> models.Chat | None:
    """Получение информации о чате по его ID"""
    return db.query(models.Chat).filter(models.Chat.id == chat_id).first()

def get_user_chats(db: Session, user_id: int) -> list[models.Chat]:
    """Получение из базы данных чата по определённому токену пользователя"""
    return db.query(models.Chat).filter(models.Chat.user_id == user_id).all()

def get_chat_messages(db: Session, chat_id: int) -> list[models.Message]:
    """Получение сообщений из базы данных по их общему ID чата"""
    return db.query(models.Message).filter(models.Message.chat_id == chat_id).all()

def create_chat(db: Session, user_id: int, name: str, back_logs: str = None, front_logs: str = None) -> models.Chat:
    """Создание чата в базе данных по ID пользователя и его названию"""
    db_chat = models.Chat(
        user_id=user_id,
        name=name,
        date_of_create=datetime.now(),
        back_logs=back_logs,
        front_logs=front_logs
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def update_chat_error_info(db: Session, chat_id: int, summary: str = None, trace: str = None, back_logs: str = None, front_logs: str = None, service: str = None) -> models.Chat:
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    
    if summary is not None:
        chat.summary = summary
    if trace is not None:
        chat.trace = trace
    if back_logs is not None:
        chat.back_logs = back_logs
    if front_logs is not None:
        chat.front_logs = front_logs
    if service is not None:
        chat.service = service
    
    db.commit()
    db.refresh(chat)
    return chat

def delete_chat(db: Session, chat_id: int) -> bool:
    """Удаление чата и связанны с ним сообщениями из базы данных по ID чата"""
    messages = db.query(models.Message).filter(models.Message.chat_id == chat_id).all()
    if messages:
        for msg in messages:
            db.delete(msg)
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if chat:
        db.delete(chat)
    db.commit()
    return True

def save_message(db: Session, message: schemas.SendMessage) -> models.Message:
    """Сохранение сообщения в базу данных"""
    db_message = models.Message(
        chat_id=message.chat_id,
        sender_type=message.sender_type,
        content=message.content,
        date_of_create=message.date_of_create
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Тикеты
def create_ticket(db: Session, chat_id: int, priority_id: int, ticket_data: schemas.TicketCreate = None):
    """Создание нового тикета с минимальными данными"""
    if not db.query(models.Priorities).filter(models.Priorities.id == priority_id).first():
        raise HTTPException(status_code=400, detail="Invalid priority ID")
    
    # Получаем данные из чата, если они нужны
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    
    # Создаем тикет
    db_ticket = models.Ticket(
        chat_id=chat_id,
        priority_id=priority_id,
        date_of_create=datetime.now(),
        service=ticket_data.service if ticket_data and ticket_data.service else (chat.service if chat else None),
        summary=ticket_data.summary if ticket_data and ticket_data.summary else (chat.summary if chat else None),
        trace=ticket_data.trace if ticket_data and ticket_data.trace else (chat.trace if chat else None),
        back_logs=ticket_data.back_logs if ticket_data and ticket_data.back_logs else (chat.back_logs if chat else None),
        front_logs=ticket_data.front_logs if ticket_data and ticket_data.front_logs else (chat.front_logs if chat else None)
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket

def update_ticket(db: Session, ticket_id: int, priority_id: int, ticket_data: schemas.TicketUpdate = None):
    """Обновление тикета"""
    db_ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not db_ticket:
        return None
    
    if not db.query(models.Priorities).filter(models.Priorities.id == priority_id).first():
        raise HTTPException(status_code=400, detail="Invalid priority ID")
    
    db_ticket.priority_id = priority_id
    
    if ticket_data:
        if ticket_data.service is not None:
            db_ticket.service = ticket_data.service
        if ticket_data.summary is not None:
            db_ticket.summary = ticket_data.summary
        if ticket_data.trace is not None:
            db_ticket.trace = ticket_data.trace
        if ticket_data.back_logs is not None:
            db_ticket.back_logs = ticket_data.back_logs
        if ticket_data.front_logs is not None:
            db_ticket.front_logs = ticket_data.front_logs
    
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

def get_ticket_by_id(db: Session, ticket_id: int) -> models.Ticket | None:
    """Получение тикета по ID"""
    return db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

def get_ticket_by_chat_id(db: Session, chat_id: int) -> models.Ticket | None:
    """Получение тикета по ID чата"""
    return db.query(models.Ticket).filter(models.Ticket.chat_id == chat_id).first()

def get_user_tickets(db: Session, user_id: int):
    """Получить все тикеты пользователя"""
    # Получаем все чаты пользователя
    chats = db.query(models.Chat).filter(models.Chat.user_id == user_id).all()
    chat_ids = [chat.id for chat in chats]
    
    # Получаем все тикеты для этих чатов
    tickets = db.query(models.Ticket).filter(models.Ticket.chat_id.in_(chat_ids)).all()
    
    result = []
    for ticket in tickets:
        # Получаем приоритет
        priority = db.query(models.Priorities).filter(models.Priorities.id == ticket.priority_id).first()
        if not priority:
            continue
            
        # Получаем пользователя и его роль
        user = db.query(models.User).filter(models.User.id == user_id).first()
        role = get_role_by_id(db, user.role_id) if user else None
        
        # Получаем связанный чат
        chat = db.query(models.Chat).filter(models.Chat.id == ticket.chat_id).first()
        
        # Формируем данные для ответа
        ticket_data = {
            "id": ticket.id,
            "chat_id": ticket.chat_id,
            "priority": priority.priority if priority else "",
            "priority_id": priority.id,
            "service": ticket.service if ticket.service else "",
            "summary": ticket.summary if ticket.summary else "",
            "trace": ticket.trace if ticket.trace else "",
            "back_logs": ticket.back_logs if ticket.back_logs else "",
            "front_logs": ticket.front_logs if ticket.front_logs else "",
            "user_id": user_id,
            "username": user.username if user else "",
            "email": user.email if user else "",
            "role_id": user.role_id if user else 1,
            "role": role.role if role else "user",
            "date_of_create": ticket.date_of_create
        }
        result.append(ticket_data)
    
    return result


# Приоритеты

def get_priorities(db: Session):
    """Получить список приоритетов"""
    return db.query(models.Priorities).order_by(models.Priorities.id).all()

def get_priority_by_id(db: Session, priority_id: int):
    """Получить приоритет по ID приоритета"""
    return db.query(models.Priorities).filter(models.Priorities.id == priority_id).first()

def get_priority_by_name(db: Session, name: str):
    """Получить приоритет по имени"""
    return db.query(models.Priorities).filter(models.Priorities.priority == name).first()

def is_priority_used(db: Session, priority_id: int):
    """Check if priority is used in any tickets"""
    return db.query(models.Ticket).filter(models.Ticket.priority_id == priority_id).first() is not None


# Роли
def get_roles(db: Session):
    """Получить список ролец"""
    return db.query(models.Role).order_by(models.Role.id).all()

def get_role_by_id(db: Session, role_id: int) -> models.Role | None:
    """Получение роли по ID"""
    return db.query(models.Role).filter(models.Role.id == role_id).first()