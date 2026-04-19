# Импорты внешних библиотек
from fastapi import FastAPI, status, Depends, HTTPException, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging
import base64

logging.basicConfig(level=logging.INFO, format='%(levelname)s:     %(message)s')

# Импорты внутренних файлов
from modules.database import get_db
from modules.config import config_values
from modules.utils import print_logo, simple_summarizer, create_access_token, verify_password, timestamp_category, password_hash, parse_tags, create_upload_file_from_base64
from modules.openrouter import OpenRouterMessage, OpenRouterChat
from modules.log_sender import setup_logging
from modules import schemas, crud, file_database, models, pdf_generator, csv_generator



# Цикл работы
@asynccontextmanager
async def lifespan(app: FastAPI):
    # То что будет выполняться до запуска FastAPI сервера
    print_logo()
    setup_logging()
    yield
    # То что будет выполняться после выключения FastAPI сервера
    if config_values.SSH_TUNNELING:
        from modules.database import tunnel
        tunnel.close()


# Базовая конфигурация FastAPI
app = FastAPI(
    title="Log-Assist API",
    description="",
    version="1.1.0",
    contact={
        "name": "Asriel_Story",
        "url": "https://t.me/Asriel_Story",
        "email": "asriel.story.com@gmail.com"
    },
    lifespan=lifespan
)

# Аутентификатор токена носителя HTTP
security = HTTPBearer()

# Позволяет API слушать обращения (* - любой)
origins = [
    # "http://localhost",
    # "http://localhost:" + str(config_values.PORT),
    # "https://localhost"
    "*"
]

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Авторизация пользователя по токену из headers
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> models.User:
    token = credentials.credentials
    user = crud.get_user_by_token(db=db, token=token)
    if user is None:
        raise HTTPException(status_code=400, detail="Пользователя не существует")
    return user

# Упаковка информации пользователя в словарь
def packaging_user_data(user: models.User, db: Session) -> dict:
    """Упаковка данных пользователя с получением названия роли из таблицы roles"""
    role = crud.get_role_by_id(db, user.role_id)
    role_name = role.role if role else "Пользователь"  

    return {
        "token": create_access_token({
            "email": user.email,
            "password": user.password
        }),
        "username": user.username,
        "email": user.email,
        "role": role_name,
        "avatar_url": file_database.get_avatar_by_id(user_id=user.id),
        "date_of_create": user.date_of_reg
    }


# Техническое
@app.get(
    path="/api/health",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    responses={
        200: {"description": "Информация получена"},
    },
    tags=["Техническое"]
)
async def health_check():
    """Проверка работоспособности API"""
    return None

@app.get(
    path="/api/test/error",
    response_model=str,
    status_code=status.HTTP_200_OK,
    summary="Тестовая ошибка",
    responses={},
    tags=["Техническое"]
)
async def test_error():
    """Тестовая ошибка для теста корректной работы системы логирования"""
    return str(1 / 0)


# Чат
@app.post(
    path="/api/v1/message",
    response_model=schemas.Message,
    status_code=status.HTTP_200_OK,
    summary="Сообщение от пользователя",
    responses={
        200: {"description": "Сообщение успешно отправлено"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Чат"]
)
async def get_msg(message_data: schemas.NewMessage = Depends(), images: Optional[list[UploadFile]] = File(None), user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Отправка сообщения пользователя"""
    # Проверка для работы
    chat = crud.get_chat_by_id(db=db, chat_id=message_data.chat_id)
    if chat is None:
        raise HTTPException(status_code=400, detail="Чата не существует")
    if user.id != chat.user_id:
        raise HTTPException(status_code=400, detail="Недостаточно прав на доступ к чату")
    if not images is None:
        if len(images) > config_values.MAX_IMAGE_COUNT:
            raise HTTPException(status_code=400, detail="Слишком много файлов")
        for image in images:
            if image.size > config_values.MAX_IMAGE_SIZE * 1024: # Перевод в из Кб в б
                raise HTTPException(status_code=400, detail="Файл(ы) слишком большие")
    # Экземпляры сообщений для последующего сохранения
    user_message = schemas.SendMessage(
        chat_id=message_data.chat_id,
        sender_type="user",
        content=message_data.message,
        date_of_create=datetime.now()
    )
    ai_message = schemas.SendMessage(
        chat_id=message_data.chat_id,
        sender_type="ai",
        content="",
        date_of_create=datetime.now()
    )
    # Упаковка сообщений для отправки сообщений нейросети
    db_messages = crud.get_chat_messages(db=db, chat_id=message_data.chat_id)
    request_messages = []
    for message in db_messages:
        message_images = file_database.get_message_image(
            user_id=user.id,
            chat_id=message_data.chat_id,
            message=message.id
        )
        request_messages.append(OpenRouterMessage(
            role=message.sender_type,
            text=message.content,
            images=message_images
        ))
    chat_session = OpenRouterChat(messages_history=request_messages)
    # Ограничение количества сообщений
    if len(request_messages) >= 100:
        raise HTTPException(status_code=400, detail="Превышено максимальное количество сообщений")
    # Получение ответа нейросети
    request_user_msg = OpenRouterMessage(
        role=user_message.sender_type,
        text=user_message.content,
        images=[
            f"data:{image.content_type};base64,{base64.b64encode(image.file.read()).decode("utf-8")}" for image in images
        ] if not images is None else None
    )
    ai_message.content += simple_summarizer(await chat_session.get_response(request_user_msg), max_chars=10000)
    # Сохранение сообщений и изображений в БД
    user_msg_db = crud.save_message(db=db, message=user_message)
    msg = crud.save_message(db=db, message=ai_message)
    if not images is None:
        for index, image in enumerate(images):
            file_database.upload_message_image(
                user_id=user.id,
                chat_id=message_data.chat_id,
                message_id=user_msg_db.id,
                image_id=index,
                file=image
            )
    return {
        "id": msg.id,
        "chat_id": msg.chat_id,
        "sender_type": msg.sender_type,
        "content": msg.content,
        "images_url": None,
        "date_of_create": msg.date_of_create
    }

@app.post(
    path="/api/v1/message/analysis",
    response_model=schemas.Message,
    status_code=status.HTTP_200_OK,
    summary="Анализ проблемы",
    responses={
        200: {"description": "Анализ проблемы выполнен"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Чат"]
)
async def get_analysis( chat_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Получение анализа проблемы с сохранением шагов воспроизведения"""
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=400, detail="Чата не существует")
    if user.id != chat.user_id:
        raise HTTPException(status_code=400, detail="Недостаточно прав на доступ к чату")
    
    # Получаем промпт из роли пользователя
    role = crud.get_role_by_id(db, user.role_id)
    if not role:
        raise HTTPException(status_code=400, detail="Роль пользователя не найдена")
    
    # Получаем все изображения из первого сообщения чата
    first_message = db.query(models.Message).filter(
        models.Message.chat_id == chat_id,
        models.Message.sender_type == "user"
    ).order_by(models.Message.id).first()
    
    images = []
    if first_message:
        images = file_database.get_message_image(
            user_id=user.id,
            chat_id=chat_id,
            message=first_message.id
        ) or []
    
    # Получаем логи из чата
    back_logs = chat.back_logs or ""
    front_logs = chat.front_logs or ""
    logs = f"Логи бекенда:\n{back_logs}\n\nЛоги фронтенда:\n{front_logs}"

    # Создаем сообщение для анализа с изображениями и логами
    analysis_message = OpenRouterMessage(
        role="user",
        text=f"{role.prompt}\n\nЛоги для анализа:\n{logs}\n\nПроведи подробный анализ действий пользователя, которые привели к ошибке, по шагам. Заключи все в тег XML <trace></trace>",
        images=images
    )
    
    # Получаем ответ от нейросети
    chat_session = OpenRouterChat()
    response = parse_tags(simple_summarizer(await chat_session.get_response(analysis_message), max_chars=10000))
    
    # Создаем и сохраняем сообщение
    ai_message = schemas.SendMessage(
        chat_id=chat_id,
        sender_type="ai",
        content=response.get('trace') if response.get('trace') else "Возникла ошибка. Пожалуйста повторите запрос.",
        date_of_create=datetime.now()
    )
    msg = crud.save_message(db=db, message=ai_message)
    
    # Извлекаем и сохраняем trace
    if 'trace' in response:
        crud.update_chat_error_info(
            db=db,
            chat_id=chat_id,
            trace=response.get('trace')
        )
    
    return {
        "id": msg.id,
        "chat_id": msg.chat_id,
        "sender_type": msg.sender_type,
        "content": msg.content,
        "images_url": None,
        "date_of_create": msg.date_of_create
    }

@app.post(
    path="/api/v1/message/solution",
    response_model=schemas.Message,
    status_code=status.HTTP_200_OK,
    summary="Решение проблемы",
    responses={
        200: {"description": "Решение проблемы предоставлено"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Чат"]
)
async def get_solution(
    chat_id: int, 
    user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Получение решения проблемы с использованием логов и изображений из чата"""
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=400, detail="Чата не существует")
    if user.id != chat.user_id:
        raise HTTPException(status_code=400, detail="Недостаточно прав на доступ к чату")
    
    # Получаем промпт из роли пользователя
    role = crud.get_role_by_id(db, user.role_id)
    if not role:
        raise HTTPException(status_code=400, detail="Роль пользователя не найдена")
    
    # Получаем все изображения из первого сообщения чата
    first_message = db.query(models.Message).filter(
        models.Message.chat_id == chat_id,
        models.Message.sender_type == "user"
    ).order_by(models.Message.id).first()
    
    images = []
    if first_message:
        images = file_database.get_message_image(
            user_id=user.id,
            chat_id=chat_id,
            message=first_message.id
        ) or []
    
    # Получаем логи из чата
    back_logs = chat.back_logs or ""
    front_logs = chat.front_logs or ""
    logs = f"Логи бекенда:\n{back_logs}\n\nЛоги фронтенда:\n{front_logs}"
    
    # Создаем сообщение для запроса решения с изображениями и логами
    solution_message = OpenRouterMessage(
        role="user",
        text=f"{role.prompt}\n\nЛоги для анализа:\n{logs}\n\nПредложи пошаговое решение проблемы.",
        images=images
    )
    
    # Получаем ответ от нейросети
    chat_session = OpenRouterChat()
    response = await chat_session.get_response(solution_message)
    
    # Создаем и сохраняем только сообщение с решением (без сохранения solution в БД)
    ai_message = schemas.SendMessage(
        chat_id=chat_id,
        sender_type="ai",
        content=simple_summarizer(response, max_chars=10000),
        date_of_create=datetime.now()
    )
    msg = crud.save_message(db=db, message=ai_message)
    
    return {
        "id": msg.id,
        "chat_id": msg.chat_id,
        "sender_type": msg.sender_type,
        "content": msg.content,
        "images_url": None,
        "date_of_create": msg.date_of_create
    }

@app.get(
    path="/api/v1/user/chats",
    response_model=list[schemas.Chat],
    status_code=status.HTTP_200_OK,
    summary="Чаты пользователя",
    responses={
        200: {"description": "ID чатов пользователя получены"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Чат", "Пользователь"]
)
async def get_chats(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Получение ID всех чатов пользователя с указанием времени создания в виде TIMESTAMP и их названия"""
    chats = crud.get_user_chats(db=db, user_id=user.id)
    return [
        {
            "id": chat.id,
            "user_id": chat.user_id,
            "name": chat.name,
            "category": timestamp_category(chat.date_of_create),
            "date_of_create": chat.date_of_create,
            "service": chat.service,
            "summary": chat.summary,
            "trace": chat.trace,
            "back_logs": chat.back_logs,
            "front_logs": chat.front_logs
        }
        for chat in chats
    ]


@app.get(
    path="/api/v1/chat",
    response_model=list[schemas.Message],
    status_code=status.HTTP_200_OK,
    summary="Чат пользователя",
    responses={
        200: {"description": "Данные о чате получены"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Чат"]
)
async def get_chat(chat_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Получение сообщений из чата"""
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=400, detail="Чата не существует")
    if user.id != chat.user_id:
        raise HTTPException(status_code=400, detail="Недостаточно прав на доступ к чату")
    result = []
    msgs = crud.get_chat_messages(db=db, chat_id=chat_id)
    for msg in msgs:
        result.append(schemas.Message(
            id=msg.id,
            chat_id=msg.chat_id,
            sender_type=msg.sender_type,
            content=msg.content,
            images_url=file_database.get_url_image(
                user_id=user.id,
                chat_id=msg.chat_id,
                message=msg.id
            ),
            date_of_create=msg.date_of_create
        ))
    return result

# Создание нового чата
@app.post(
    path="/api/v1/chat",
    response_model=tuple[schemas.Chat, schemas.Message],
    status_code=status.HTTP_201_CREATED,
    summary="Создание чата",
    responses={
        201: {"description": "Чат успешно создан"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Чат"]
)
async def create_chat(new_chat: schemas.NewChat, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Создание нового чата пользователя, если значение image будет "", то будет отправлено только текстовое сообщение"""
    user_message = schemas.SendMessage(
        chat_id=0,
        sender_type="user",
        content="",
        date_of_create=datetime.now()
    )
    user_message.content += f"{new_chat.back_logs}\n{new_chat.front_logs}"

    ai_message = schemas.SendMessage(
        chat_id=0,
        sender_type="ai",
        content="",
        date_of_create=datetime.now()
    )
    
    # Создание сообщения
    response_message = OpenRouterMessage(
        role="user",
        text=f"{new_chat.message}\nЛоги бекенда:\n{new_chat.back_logs}\nЛоги фронтенда:\n{new_chat.front_logs}",
        images=[new_chat.images]
    )
    
    # Инициализация чата
    chat_session = OpenRouterChat()
    # Получение ответа от нейросети на сообщение выше
    response = await chat_session.get_response(message=response_message)
    summarized_response = simple_summarizer(response, max_chars=10000)
    parsed = parse_tags(summarized_response) if summarized_response else {}
    
    # Извлекаем данные с проверкой на None
    summary = parsed.get('summary', '') if parsed else ''
    
    chat_name = simple_summarizer(parsed.get('chat_name', ''), max_chars=20) if parsed else simple_summarizer(summarized_response, markdown=False) if summarized_response else 'Новый чат'
    service = parsed.get('service', '') if parsed else ''
    
    ai_message.content += summary
    
    # Создание и сохранение сообщений и чата
    chat = crud.create_chat(db=db, user_id=user.id, name=chat_name, back_logs=new_chat.back_logs, front_logs=new_chat.front_logs)
    ai_message.chat_id = chat.id
    user_message.chat_id = chat.id
    
    user_msg = crud.save_message(db=db, message=user_message)
    msg = crud.save_message(db=db, message=ai_message)
    # Сохранение сообщений
    for index, image in enumerate(new_chat.images):
        try:
            upload_file = create_upload_file_from_base64(image)
            file_database.upload_message_image(
                user_id=user.id,
                chat_id=chat.id,
                message_id=user_msg.id,
                image_id=index,
                file=upload_file
            )
        except Exception as e:
            logging.error(f"Error processing image {index}: {str(e)}")


    # Сохраняем summary и service
    crud.update_chat_error_info(
        db=db,
        chat_id=chat.id,
        summary=summary,
        service=service,
        back_logs=new_chat.back_logs,
        front_logs=new_chat.front_logs
    )

    return (
        schemas.Chat(
            id=chat.id,
            user_id=chat.user_id,
            name=chat.name,
            category=timestamp_category(chat.date_of_create),
            date_of_create=chat.date_of_create,
            service=service,
            summary=summary,
            trace=None,
            back_logs=new_chat.back_logs,
            front_logs=new_chat.front_logs
        ),
        schemas.Message(
            id=msg.id,
            chat_id=chat.id,
            sender_type="ai",
            content=msg.content,
            images_url=file_database.get_url_image(
                user_id=user.id,
                chat_id=chat.id,
                message=msg.id
            ),
            date_of_create=msg.date_of_create
        )
    )


@app.delete(
    path="/api/v1/chat",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    summary="Удаление чата",
    responses={
        200: {"description": "Чат удалён"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Чат"]
)
async def delete_chat(chat_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Удаление чата пользователя по его токену и ID этого чата"""
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=400, detail="Чата не существует")
    if user.id != chat.user_id:
        raise HTTPException(status_code=400, detail="Недостаточно прав на доступ к чату")
    return crud.delete_chat(db=db, chat_id=chat_id)


# Пользователь
@app.get(
    path="/api/v1/user",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Информация о пользователе",
    responses={
        200: {"description": "Успешное получение данных"},
        400: {"description": "Некорректные данные (например, пользователя по такому токену не существует)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def get_user(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Получение информации о пользователе по его токену, выданному после авторизации в системе"""
    return packaging_user_data(user=user, db=db)


@app.post(
    path="/api/v1/user/login",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Авторизация",
    responses={
        200: {"description": "Успешная авторизация"},
        400: {"description": "Некорректные данные (например, логин или пароль не верный)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def user_login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    """Авторизации пользователя в системе"""
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователя с таким email не существует")
    if not verify_password(password=user.password, hashed_password=db_user.password):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    return packaging_user_data(user=db_user, db=db)


@app.post(
    path="/api/v1/user/register",
    response_model=schemas.User,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    responses={
        201: {"description": "Пользователь успешно создан"},
        400: {"description": "Некорректные данные (например, email уже занят)"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def user_register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Регистрация пользователя в системе"""
    if len(user.email) > 100:
        raise HTTPException(status_code=422, detail="Email слишком большой")
    if crud.get_user_by_email(db=db, email=user.email):
        raise HTTPException(status_code=400, detail="Пользователь с такой почтой уже зарегистрирован")
    if crud.get_user_by_username(db=db, username=user.username):
        raise HTTPException(status_code=400, detail="Пользователь с подобным именем уже зарегистрирован")
    
    role = db.query(models.Role).filter(models.Role.id == user.role_id).first()
    if not role:
        raise HTTPException(status_code=400, detail="Указанная роль не существует")
    new_user = crud.add_new_user(db=db, user=user)
    
    file_database.create_bucket(user_id=new_user.id)
    return packaging_user_data(user=new_user, db=db)

@app.post(
    path="/api/v1/user/token",
    response_model=schemas.Token,
    status_code=status.HTTP_200_OK,
    summary="Обновление токена",
    responses={
        201: {"description": "Токен пользователя успешно обновлён"},
        400: {"description": "Некорректные данные (например, неверный токен)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def token_update(user: models.User = Depends(get_current_user)):
    """Обновление срока действия токена пользователя по его нынешнему действующему токену"""
    return {
        "token": create_access_token({
            "email": user.email,
            "password": user.password
        })
    }

@app.post(
    path="/api/v1/user/name",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Обновление имени",
    responses={
        201: {"description": "Имя пользователя успешно обновлено"},
        400: {"description": "Некорректные данные (например, неверный токен)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def username_update(new_name: schemas.UpdateName, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Обновление имени пользователя с выдачей нового токена для совершения последующих действий"""
    if crud.get_user_by_username(db=db, username=new_name.username):
        raise HTTPException(status_code=400, detail="Имя уже занято")
    user.username = new_name.username
    db.commit()
    db.refresh(user)
    return packaging_user_data(user=user, db=db)

@app.post(
    path="/api/v1/user/email",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Обновление почты",
    responses={
        201: {"description": "Почта пользователя успешно обновлена"},
        400: {"description": "Некорректные данные (например, неверный токен)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def email_update(new_email: schemas.UpdateEmail, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Обновление электронной почты пользователя с выдачей нового токена для совершения последующих действий"""
    if len(new_email.email) > 100:
        raise HTTPException(status_code=422, detail="Email слишком большой")
    if crud.get_user_by_email(db=db, email=new_email.email):
        raise HTTPException(status_code=400, detail="Почта уже занята")
    user.email = new_email.email
    db.commit()
    db.refresh(user)
    return packaging_user_data(user=user, db=db)

@app.post(
    path="/api/v1/user/password",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Обновление пароля",
    responses={
        201: {"description": "Пароль пользователя успешно обновлён"},
        400: {"description": "Некорректные данные (например, неверный токен)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def password_update(new_password: schemas.UpdatePassword, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Обновление пароля пользователя с выдачей нового токена для совершения последующих действий"""
    if not verify_password(new_password.old_password, user.password):
        raise HTTPException(status_code=400, detail="Пароль неверный")
    user.password = password_hash(new_password.new_password)
    db.commit()
    db.refresh(user)
    return packaging_user_data(user=user, db=db)

@app.post(
path="/api/v1/user/avatar",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Обновление аватара пользователя",
    responses={
        201: {"description": "Аватар пользователя успешно обновлён"},
        400: {"description": "Некорректные данные (например, неверный токен)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def avatar_update(file: UploadFile, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Обновление аватара пользователя с выдачей ссылки на новый"""
    if file.content_type.split('/')[0] != 'image':
        raise HTTPException(status_code=400, detail="Файл не является изображением")
    if not file.content_type.split('/')[1] in ["png", "jpg", "jpeg"]:
        raise HTTPException(status_code=400, detail="Не поддерживаемый формат")
    if file.size > 2 * 1024 * 1024: # Ограничение веса изображения в 2 Мб
        raise HTTPException(status_code=400, detail="Файл слишком большой")
    
    role = crud.get_role_by_id(db, user.role_id)
    role_name = role.role if role else "Пользователь"
    
    return {
        "token": create_access_token({
            "email": user.email,
            "password": user.password
        }),
        "username": user.username,
        "email": user.email,
        "role": role_name,
        "avatar_url": file_database.update_avatar_by_id(user_id=user.id, file=file),
        "date_of_create": user.date_of_reg
    }

@app.delete(
path="/api/v1/user/avatar",
    response_model=schemas.User,
    status_code=status.HTTP_200_OK,
    summary="Удаление аватара пользователя",
    responses={
        201: {"description": "Аватар пользователя успешно удалён"},
        400: {"description": "Некорректные данные (например, неверный токен)"},
        401: {"description": "Не авторизован"},
        403: {"description": "Необходима авторизация"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Пользователь"]
)
async def avatar_delete(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Удаление аватара пользователя"""
    file_database.delete_avatar_by_id(user_id=user.id)
    return packaging_user_data(user=user, db=db)


# Работа с тикетами

# Первичная генерация тикета
@app.get("/api/v1/ticket/init")
async def init_ticket(chat_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = crud.get_chat_by_id(db=db, chat_id=chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=404, detail="Чат не найден")
    
    # Получаем первое сообщение бота в чате
    messages = crud.get_chat_messages(db=db, chat_id=chat_id)
    bot_message = next((msg for msg in messages if msg.sender_type == "ai"), None)
    summary = simple_summarizer(bot_message.content, max_chars=300) if bot_message else ""
    
    # Получаем приоритет по умолчанию (medium)
    default_priority = crud.get_priority_by_name(db=db, name="medium")
    if not default_priority:
        default_priority = crud.get_priorities(db=db)[1]
    
    # Создаем временный тикет с раздельными логами
    ticket_data = {
        "id": 0,
        "chat_id": chat_id,
        "priority": default_priority.priority,
        "priority_id": default_priority.id,
        "service": chat.service if chat.service else "",
        "summary": chat.summary if chat.summary else summary,
        "trace": chat.trace if chat.trace else "",
        "back_logs": chat.back_logs if chat.back_logs else "",
        "front_logs": chat.front_logs if chat.front_logs else "", 
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role_id": user.role_id,
        "date_of_create": datetime.now()
    }
    
    return ticket_data

# Сохранение тикета
@app.post(
    path="/api/v1/ticket",
    response_model=schemas.TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тикет",
    tags=["Тикеты"]
)
async def create_ticket(
    ticket_data: schemas.TicketCreate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового тикета"""
    chat = crud.get_chat_by_id(db=db, chat_id=ticket_data.chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Создаем тикет
    db_ticket = crud.create_ticket(
        db=db,
        chat_id=ticket_data.chat_id,
        priority_id=ticket_data.priority_id,
        ticket_data=ticket_data
    )
    
    # Получаем обновленную информацию о чате
    chat = crud.get_chat_by_id(db=db, chat_id=ticket_data.chat_id)
    role = crud.get_role_by_id(db, user.role_id)
    priority = crud.get_priority_by_id(db, db_ticket.priority_id)
    
    # Формируем ответ
    return {
        "id": db_ticket.id,
        "chat_id": db_ticket.chat_id,
        "priority": priority.priority if priority else "",
        "priority_id": db_ticket.priority_id,
        "service": db_ticket.service if db_ticket.service else "",
        "summary": db_ticket.summary if db_ticket.summary else "",
        "trace": db_ticket.trace if db_ticket.trace else "",
        "back_logs": db_ticket.back_logs if db_ticket.back_logs else "",
        "front_logs": db_ticket.front_logs if db_ticket.front_logs else "",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role_id": user.role_id,
        "role": role.role if role else "Пользователь",
        "date_of_create": db_ticket.date_of_create
    }



## Получение информации о содержании тикета
@app.get(
    path="/api/v1/ticket",
    response_model=schemas.TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о тикете",
    responses={
        200: {"description": "Информация о тикете успешно получена"},
        400: {"description": "Тикет не найден"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
    },
    tags=["Тикеты"]
)
async def get_ticket(
    ticket_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о конкретном тикете по его ID"""
    # Получаем данные тикета
    db_ticket = crud.get_ticket_by_id(db=db, ticket_id=ticket_id)
    if not db_ticket:
        raise HTTPException(status_code=400, detail="Тикет не найден")
    
    # Получаем связанный чат
    chat = crud.get_chat_by_id(db=db, chat_id=db_ticket.chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    priority = crud.get_priority_by_id(db, db_ticket.priority_id)
    role = crud.get_role_by_id(db, user.role_id)
    
    return {
        "id": db_ticket.id, 
        "chat_id": db_ticket.chat_id,
        "priority": priority.priority if priority else "",
        "priority_id": db_ticket.priority_id,
        "service": db_ticket.service if db_ticket.service else "",
        "summary": db_ticket.summary if db_ticket.summary else "",
        "trace": db_ticket.trace if db_ticket.trace else "",
        "back_logs": db_ticket.back_logs if db_ticket.back_logs else "",
        "front_logs": db_ticket.front_logs if db_ticket.front_logs else "",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role_id": user.role_id,
        "role": role.role if role else "Пользователь",
        "date_of_create": db_ticket.date_of_create
    }

# Редактирование тикета
@app.post(
    path="/api/v1/ticket/update",
    response_model=schemas.TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить тикет",
    responses={
        200: {"description": "Тикет успешно обновлен"},
        400: {"description": "Тикет не найден"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Тикеты"]
)
@app.post(
    path="/api/v1/ticket/update",
    response_model=schemas.TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновить тикет",
    responses={
        200: {"description": "Тикет успешно обновлен"},
        400: {"description": "Тикет не найден"},
        401: {"description": "Не авторизован"},
        403: {"description": "Недостаточно прав"},
        422: {"description": "Ошибка валидации полей"}
    },
    tags=["Тикеты"]
)
async def update_ticket(
    ticket_data: schemas.TicketUpdate,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обновление информации о тикете"""
    # Проверка существования тикета
    db_ticket = crud.get_ticket_by_id(db=db, ticket_id=ticket_data.id)  
    if not db_ticket:
        raise HTTPException(status_code=400, detail="Тикет не найден")
    
    # Проверка прав доступа
    chat = crud.get_chat_by_id(db=db, chat_id=db_ticket.chat_id)
    if not chat or chat.user_id != user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Обновляем приоритет в тикете
    db_ticket = crud.update_ticket(
        db=db,
        ticket_id=ticket_data.id,  
        priority_id=ticket_data.priority_id,
        ticket_data=ticket_data
    )
    
    priority = crud.get_priority_by_id(db, db_ticket.priority_id)
    role = crud.get_role_by_id(db, user.role_id)

    # Получаем обновленную информацию о тикете 
    return {
        "id": db_ticket.id, 
        "chat_id": db_ticket.chat_id,
        "priority": priority.priority if priority else "",
        "priority_id": db_ticket.priority_id,
        "service": db_ticket.service if db_ticket.service else "",
        "summary": db_ticket.summary if db_ticket.summary else "",
        "trace": db_ticket.trace if db_ticket.trace else "",
        "back_logs": db_ticket.back_logs if db_ticket.back_logs else "",
        "front_logs": db_ticket.front_logs if db_ticket.front_logs else "",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role_id": user.role_id,
        "role": role.role if role else "Пользователь",
        "date_of_create": db_ticket.date_of_create
    }

# Скачивание тикета
# Скачивание pdf файла
@app.get(
    path="/api/v1/ticket/download/pdf",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Скачать тикет в формате PDF",
    tags=["Тикеты"]
)
async def download_ticket_pdf(
    ticket_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download ticket as PDF"""
    try:
        logging.info(f"Начало скачивания PDF для тикета {ticket_id}")
        
        db_ticket = crud.get_ticket_by_id(db=db, ticket_id=ticket_id)
        if not db_ticket:
            logging.error(f"Тикет {ticket_id} не найден")
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        chat = crud.get_chat_by_id(db, db_ticket.chat_id)
        if not chat or chat.user_id != user.id:
            logging.error(f"Нет прав доступа к тикету {ticket_id} для пользователя {user.id}")
            raise HTTPException(status_code=403, detail="Not authorized")
        
        priority = crud.get_priority_by_id(db, db_ticket.priority_id)
        role = crud.get_role_by_id(db, user.role_id)
        
        # Формируем данные для генерации файла
        ticket_data = {
            "id": str(db_ticket.id),
            "chat_id": str(db_ticket.chat_id),
            "priority": str(priority.priority) if priority else "",
            "priority_id": str(db_ticket.priority_id),
            "service": str(db_ticket.service) if db_ticket.service else "",
            "summary": str(db_ticket.summary) if db_ticket.summary else "",
            "trace": str(db_ticket.trace) if db_ticket.trace else "",
            "back_logs": str(db_ticket.back_logs) if db_ticket.back_logs else "",
            "front_logs": str(db_ticket.front_logs) if db_ticket.front_logs else "",
            "user_id": str(user.id),
            "username": str(user.username),
            "email": str(user.email),
            "role_id": str(user.role_id),
            "role": str(role.role) if role else "Пользователь",
            "date_of_create": db_ticket.date_of_create
        }
        
        logging.info(f"Данные для PDF сформированы: {ticket_data.keys()}")
        
        pdf_buffer = pdf_generator.generate_pdf_response(ticket_data)
        
        logging.info(f"PDF буфер создан, размер: {pdf_buffer.getbuffer().nbytes} байт")
        
        # Сбрасываем позицию буфера
        pdf_buffer.seek(0)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"ticket_{ticket_id}.pdf\"",
                "Content-Type": "application/pdf",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        logging.error(f"Ошибка при создании PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при создании PDF: {str(e)}")

# Скачивание csv файла
@app.get(
    path="/api/v1/ticket/download/csv",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Скачать тикет в формате CSV",
    tags=["Тикеты"]
)
async def download_ticket_csv(
    ticket_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download ticket as CSV"""
    try:
        logging.info(f"Начало скачивания CSV для тикета {ticket_id}")
        
        db_ticket = crud.get_ticket_by_id(db=db, ticket_id=ticket_id)
        if not db_ticket:
            logging.error(f"Тикет {ticket_id} не найден")
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        chat = crud.get_chat_by_id(db, db_ticket.chat_id)
        if not chat or chat.user_id != user.id:
            logging.error(f"Нет прав доступа к тикету {ticket_id} для пользователя {user.id}")
            raise HTTPException(status_code=403, detail="Not authorized")
        
        priority = crud.get_priority_by_id(db, db_ticket.priority_id)
        role = crud.get_role_by_id(db, user.role_id)
        
        # Формируем данные для генерации файла
        ticket_data = {
            "id": str(db_ticket.id),
            "chat_id": str(db_ticket.chat_id),
            "priority": str(priority.priority) if priority else "",
            "priority_id": str(db_ticket.priority_id),
            "service": str(db_ticket.service) if db_ticket.service else "",
            "summary": str(db_ticket.summary) if db_ticket.summary else "",
            "trace": str(db_ticket.trace) if db_ticket.trace else "",
            "back_logs": str(db_ticket.back_logs) if db_ticket.back_logs else "",
            "front_logs": str(db_ticket.front_logs) if db_ticket.front_logs else "",
            "user_id": str(user.id),
            "username": str(user.username),
            "email": str(user.email),
            "role_id": str(user.role_id),
            "role": str(role.role) if role else "Пользователь",
            "date_of_create": db_ticket.date_of_create
        }
        
        logging.info(f"Данные для CSV сформированы: {ticket_data.keys()}")
        
        csv_buffer = csv_generator.generate_csv_response(ticket_data)
        
        # Проверим содержимое CSV
        csv_content = csv_buffer.getvalue().decode('utf-8-sig')
        logging.info(f"CSV содержимое (первые 200 символов): {csv_content[:200]}")
        
        # Сбрасываем позицию буфера
        csv_buffer.seek(0)
        
        logging.info(f"CSV буфер создан, размер: {csv_buffer.getbuffer().nbytes} байт")
        
        return StreamingResponse(
            csv_buffer,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=\"ticket_{ticket_id}.csv\"",
                "Content-Type": "text/csv; charset=utf-8-sig",
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
        
    except Exception as e:
        logging.error(f"Ошибка при создании CSV: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ошибка при создании CSV: {str(e)}")
    
# Получение списка тикетов
@app.get(
    path="/api/v1/tickets",
    response_model=list[schemas.TicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить все тикеты пользователя",
    tags=["Тикеты"]
)
async def get_user_tickets(
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение всех тикетов пользователя"""
    tickets = crud.get_user_tickets(db=db, user_id=user.id)
    return tickets



# Приоритеты тикетов
@app.get(
    path="/api/v1/priorities",
    response_model=list[schemas.Priority],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех приоритетов",
    responses={
        200: {"description": "Список приоритетов успешно получен"},
        401: {"description": "Не авторизован"},
    },
    tags=["Приоритеты"]
)
async def get_priorities(
    db: Session = Depends(get_db)
):
    """Получение списка всех доступных приоритетов для тикетов"""
    return crud.get_priorities(db=db)


# Роли
@app.get(
    path="/api/v1/roles",
    response_model=list[schemas.Role],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех ролей",
    responses={
        200: {"description": "Список ролей успешно получен"},
        401: {"description": "Не авторизован"},
    },
    tags=["Роли"]
)
async def get_roles(
    db: Session = Depends(get_db)
):
    """Получение списка всех доступных ролей"""
    return crud.get_roles(db=db)
