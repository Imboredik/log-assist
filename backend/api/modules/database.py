from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, TIMESTAMP, inspect, Boolean
from sqlalchemy.orm import sessionmaker
from sshtunnel import SSHTunnelForwarder
import logging

from .config import config_values

logger = logging.getLogger(__name__)

database_url = f"postgresql://{config_values.PG_USER}:{config_values.PG_PASSWORD}"

if config_values.SSH_TUNNELING is True:
    logging.info("Подключение базы данных по SSH туннелированию...")
    tunnel = SSHTunnelForwarder(
        (config_values.SSH_HOST, config_values.SSH_PORT),
        ssh_username=config_values.SSH_USER,
        ssh_password=config_values.SSH_PASSWORD,
        remote_bind_address=(config_values.PG_HOST, config_values.PG_PORT)
    )
    tunnel.start()

    database_url += f"@{config_values.PG_HOST}:{tunnel.local_bind_port}/{config_values.PG_DATABASE}"
else:
    logging.info("Подключение локальной базы данных...")
    database_url += f"@{config_values.PG_HOST}:{config_values.PG_PORT}/{config_values.PG_DATABASE}"

metadata = MetaData()

engine = create_engine(
    database_url,
    pool_size=0,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=3600
)

inspector = inspect(engine)

logger.info("Проверка подключения...")
try:
    connection = engine.connect()
    connection.close()
except OperationalError:
    raise ValueError("Ошибка подключения к базе данных. Нет доступа к базе данных")

SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()

logger.info("База данных подключена!")

def initialize_priorities(db):
    # Проверяем, есть ли уже записи в таблице priorities
    if not db.query(priorities).first():
        priority = [
            {"id": 4, "priority": "Незначительная"},
            {"id": 3, "priority": "Обычная"},
            {"id": 2, "priority": "Серьезная"},
            {"id": 1, "priority": "Критическая"}
        ]
        
        # Вставляем данные
        db.execute(priorities.insert(), priority)
        db.commit()
        logger.info("Инициализированы приоритеты по умолчанию")


def initialize_roles(db):
    if not db.query(roles).first():
        roles_examples = [
            {
                "id": 1, 
                "role": "Оператор", 
                "prompt": "Ты — ассистент поддержки. Анализируй скриншоты и давай простые инструкции.", 
                "description": "Упрощенные инструкции с фокусом на действия пользователя",
                "is_admin": False
            },
            {
                "id": 2, 
                "role": "Разработчик", 
                "prompt": "Ты — технический ассистент. Анализируй скриншоты с кодами ошибок.", 
                "description": "Технический анализ с акцентом на код и системные сообщения",
                "is_admin": False
            },
            {
                "id": 3, 
                "role": "Тестировщик", 
                "prompt": "Ты — QA-ассистент. Анализируй скриншоты для воспроизведения багов.", 
                "description": "Пошаговое воспроизведение проблем с анализом ожидаемого поведения",
                "is_admin": False
            }
        ]

        # Вставляем данные
        db.execute(roles.insert(), roles_examples)
        db.commit()
        logger.info("Инициализированы базовые роли и промпты")

def get_db():
    db = SessionLocal()
    try:
        initialize_priorities(db)
        initialize_roles(db)
        yield db
    finally:
        db.close()


users = Table(
    "users", metadata,
    Column("id", Integer, nullable=False, unique=True, primary_key=True),
    Column("email", String(100), nullable=False, unique=True),
    Column("username", String(30), nullable=False, unique=True),
    Column("role_id", Integer, nullable=False),
    Column("password", String(64), nullable=False),
    Column("date_of_reg", TIMESTAMP, nullable=False, unique=False)
)

chats = Table(
    "chats", metadata,
    Column("id", Integer, nullable=False, primary_key=True),
    Column("user_id", Integer, nullable=False),
    Column("name", String(20), nullable=True, unique=False),
    Column("date_of_create", TIMESTAMP, nullable=False, unique=False),
    Column("service", String(1000), nullable=True),
    Column("summary", String(10000), nullable=True),
    Column("trace", String(5000), nullable=True),
    Column("back_logs", String(10000), nullable=True),
    Column("front_logs", String(10000), nullable=True)
)

message = Table(
    "messages", metadata,
    Column("id", Integer, nullable=False, unique=True, primary_key=True),
    Column("chat_id", Integer, nullable=False, unique=False),
    Column("sender_type", String(4), nullable=False, unique=False),
    Column("content", String(10000), nullable=False, unique=False),
    Column("date_of_create", TIMESTAMP, nullable=False, unique=False)
)

tickets = Table(
    "tickets", metadata,
    Column("id", Integer, nullable=False, primary_key=True, autoincrement=True),
    Column("chat_id", Integer, nullable=False),
    Column("priority_id", Integer, nullable=False),
    Column("date_of_create", TIMESTAMP, nullable=False),
    Column("service", String(100), nullable=True),  
    Column("summary", String(10000), nullable=True), 
    Column("trace", String(5000), nullable=True),  
    Column("back_logs", String(10000), nullable=True),
    Column("front_logs", String(10000), nullable=True)
)

priorities = Table(
    "priorities",
    metadata,
    Column("id", Integer, nullable=False, primary_key=True, autoincrement=True),
    Column("priority", String(14), nullable=False)
)

roles = Table(
    "roles", metadata,
    Column("id", Integer, nullable=False, primary_key=True, autoincrement=True),
    Column("role", String(60), nullable=False, unique=True),
    Column("prompt", String(10000), nullable=False, unique=True),
    Column("description", String(500), nullable=True),
    Column("is_admin", Boolean, nullable=False, unique=False),
)


exiting_tables = inspector.get_table_names()
tables_to_create = [
    table for table in metadata.sorted_tables
    if table.name not in exiting_tables
]
if tables_to_create:
    metadata.create_all(engine, tables=tables_to_create)
    logger.info(f"Созданы отсутствующие таблицы: {[table.name for table in tables_to_create]}")
    
else:
    logger.info("Все необходимые таблицы существуют")
