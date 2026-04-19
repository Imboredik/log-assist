from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime


# Сообщения
class SendMessage(BaseModel):
    chat_id: int = Field(
        default=...,
        title="ID чата",
        examples=[1563],
        description="ID чата, к которому принадлежит сообщение"
    )
    sender_type: str = Field(
        default=...,
        title="Тип отправителя",
        max_length=4,
        examples=["user", "ai"],
        description="Тот кто отправил сообщение в чат"
    )
    content: str = Field(
        default=...,
        title="Текст сообщения",
        max_length=10000,
        examples=["Пример текстового сообщения, которое набрал пользователь или ИИ агент"],
        description="Основное наполнение сообщение, которое было отправлено ИИ или пользователем"
    )
    date_of_create: datetime = Field(
        default=...,
        title="Дата создания",
        examples=[datetime.now()],
        description="Дата отправки сообщения пользователем или ИИ агентом"
    )

class Message(SendMessage):
    id: int = Field(
        default=...,
        title="ID сообщения",
        examples=[516843],
        description="Уникальный ID сообщения для возможности загружать историю сообщений"
    )
    images_url: list[str] | None = Field(
        default=...,
        title="Ссылки на изображения",
        examples=["http://localhost:9000/user-1/chats/23/86/0.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=user%2F20250711%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20250711T153303Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=e95b74e9ae7e8743de11e51ea0f66371518515a3f4d7b61a486a11dff9104e2e"],
        description="Ссылки на изображения подписанные minio, которые прикреплены к сообщению. Список - если прикреплены, иначе None"
    )

class NewMessage(BaseModel):
    chat_id: int = Field(
        default=...,
        title="ID чата",
        examples=[1563],
        description="ID чата в который будет отправлено сообщение"
    )
    message: str = Field(
        default=...,
        title="Сообщение",
        max_length=10000,
        examples=["Реши проблему в коде, используя логи"],
        description="Входящее сообщение (prompt для нейросети)"
    )

class NewChat(BaseModel):
    message: str = Field(
        default=''' 
                Составь краткое резюме о проблеме проанализировав изображения и логи.
                Ответ в XML:<chat_name>Название чата</chat_name><service>Сервис в котором возникла проблема</service>
                <summary>Краткое резюме о проблеме</summary>
                ''',
        title="Сообщение",
        max_length=10000,
        examples=["Реши проблему в коде, используя логи"],
        description="Входящее сообщение (prompt для нейросети)"
    )
    images: list[str] = Field(
        default=...,
        title="Изображение",
        max_length=1048576,
        examples=[["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD/4QBoRXhpZgAATU0AKgAAAAgABAEaAAUAAAABAAAAPgE..."]],
        description="Изображение в base64, которое будет использовано для визуального анализа проблемы пользователя"
    )
    back_logs: str = Field(
        default="",
        title="Бэкенд логи",
        examples=["ERROR 500: Internal Server Error\nat AuthService.login (auth.service.ts:25:13)"],
        description="Логи бэкенда для анализа нейросетью"
    )
    front_logs: str = Field(
        default="",
        title="Фронтенд логи",
        examples=["Error: Failed to load resource: the server responded with a status of 500 (Internal Server Error)"],
        description="Логи фронтенда для анализа нейросетью"
    )

class Chat(BaseModel):
    id: int = Field(
        default=...,
        title="ID чата",
        examples=[1563],
        description="ID чата пользователя"
    )
    user_id: int = Field(
        default=...,
        title="ID пользователя",
        examples=[831],
        description="ID пользователя, владеющего чатом"
    )
    name: str = Field(
        default=...,
        title="Название чата",
        max_length=20,
        examples=["Решение проблемы"],
        description="Название чата пользователя"
    )
    category: str = Field(
        default=...,
        title="Категория времени",
        max_length=8,
        examples=["Сегодня", "Вчера", "7 дней", "30 дней", "2025-04"],
        description="Категория чата по времени относительно сегодняшней даты (по серверу), возможные варианты: Сегодня, Вчера, 7 дней, 30 дней, 2025-04"
    )
    date_of_create: datetime = Field(
        default=...,
        title="Время создания",
        examples=[datetime.now()],
        description="Дата в которую был создан чат пользователя"
    )
    service: str | None = Field(
        default=None,
        title="Сервис",
        max_length=1000,
        examples=["API Gateway", "Authentication", "Database"],
        description="Сервис, в котором возникла проблема"
    )
    summary: str | None = Field(
        default=None,
        title="Краткое описание",
        max_length=10000,
        examples=["Ошибка аутентификации при входе через Google"],
        description="Краткое описание проблемы"
    )
    trace: str | None = Field(
        default=None,
        title="Шаги воспроизведения",
        max_length=5000,
        examples=["1. Открыть приложение\n2. Нажать 'Войти через Google'\n3. Ввести учетные данные"],
        description="Шаги пользователя для воспроизведения проблемы"
    )
    back_logs: str | None = Field(
        default=None,
        title="Логи бэкенда",
        max_length=10000,
        examples=["ERROR 500: Internal Server Error\nat AuthService.login (auth.service.ts:25:13)"],
        description="Логи ошибки бэкенда для анализа"
    )
    front_logs: str = Field(
        default="",
        title="Логи фронтенда",
        examples=["Error: Failed to load resource: the server responded with a status of 500 (Internal Server Error)"],
        description="Логи фронтенда для анализа нейросетью"
    )

# class DeleteChat(BaseModel):
#     token: str = Field(
#         default=...,
#         title="Токен пользователя",
#         max_length=256,
#         examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJwYXNzd29yZCI6InN0cmluZ3N0IiwiZXhwIjoxNzUwNjU3OTUyfQ.TM_hP1zSZmBJvW0-TtC7k3VP7Zl2QuisA-0WFITy9Hk"],
#         description="Токен пользователя, позволяющий определить является ли пользователь владельцем чата"
#     )
#     chat_id: int = Field(
#         default=...,
#         title="ID чата",
#         examples=[1563],
#         description="ID удаляемого чата пользователя"
#     )


# Пользователь
class UserCreate(BaseModel):
    username: str = Field(
        default=...,
        title="Никнейм пользователя",
        max_length=30,
        examples=["John", "Mike", "Asriel"],
        description="Никнейм пользователя, используемый в авторизации и как отличительная черта пользователя"
    )
    email: EmailStr = Field(
        default=...,
        title="Email пользователя",
        examples=["john@example.com", "mike@example.com", "asriel@example.com"],
        description="Электронная почта пользователя"
    )
    password: str = Field(
        default=...,
        title="Пароль пользователя",
        min_length=8,
        max_length=32,
        examples=["12345678", "qwerty25"],
        description="Пароль создаваемого пользователя"
    )
    role_id: int = Field(
        default=...,
        title="Id роли пользователя",
        examples=["1", "2", "3"],
        description="Id роли пользователя в системе"
    )

class UserLogin(BaseModel):
    email: EmailStr = Field(
        default=...,
        title="Email пользователя",
        examples=["john@example.com", "mike@example.com", "asriel@example.com"],
        description="Электронная почта пользователя"
    )
    password: str = Field(
        default=...,
        title="Пароль пользователя",
        min_length=8,
        max_length=32,
        examples=["12345678", "qwerty25"],
        description="Пароль авторизуемого пользователя"
    )

class User(BaseModel):
    token: str = Field(
        default=...,
        title="Токен пользователя",
        max_length=256,
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJwYXNzd29yZCI6InN0cmluZ3N0IiwiZXhwIjoxNzUwNjU3OTUyfQ.TM_hP1zSZmBJvW0-TtC7k3VP7Zl2QuisA-0WFITy9Hk"],
        description="Токен пользователя, позволяющий осуществлять действия в системе"
    )
    username: str = Field(
        default=...,
        title="Никнейм пользователя",
        max_length=30,
        examples=["John", "Mike", "Asriel"],
        description="Никнейм пользователя, используемый в авторизации и как отличительная черта пользователя"
    )
    email: EmailStr = Field(
        default=...,
        title="Email пользователя",
        examples=["john@example.com", "mike@example.com", "asriel@example.com"],
        description="Электронная почта пользователя"
    )
    role: str = Field(
        default=...,
        title="Роль пользователя",
        max_length=60,
        examples=["user", "admin"],
        description="Роль пользователя в системе, позволяющая ему определённый функционал"
    )
    avatar_url: str | None = Field(
        default=...,
        title="Ссылка на автар пользователя",
        max_length=512,
        examples=["http://localhost:9000/user-3/avatar.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&"
                  "X-Amz-Credential=admin%2F20250707%2Fus-east-1%2Fs3%2Faws4_request&"
                  "X-Amz-Date=20250707T145946Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&"
                  "X-Amz-Signature=b491df242d15d9c4530df4a7ddd54193fa9b22d4cfd798627a87dbe7521f62e6"],
        description="Ссылка на изображение аватара пользователя"
    )
    date_of_create: datetime = Field(
        default=...,
        title="Время создания",
        examples=[datetime.now()],
        description="Дата в которую был создан профиль пользователя"
    )
    # verified: bool = Field(
    #     default=...,
    #     title="Подтверждённость профиля",
    #     examples=[True, False],
    #     description="Параметр отображающий то подтверждённый ли профиль пользователя (например почта)"
    # )

class Token(BaseModel):
    token: str = Field(
        default=...,
        title="Токен пользователя",
        max_length=256,
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJwYXNzd29yZCI6InN0cmluZ3N0IiwiZXhwIjoxNzUwNjU3OTUyfQ.TM_hP1zSZmBJvW0-TtC7k3VP7Zl2QuisA-0WFITy9Hk"],
        description="Токен пользователя, позволяющий осуществлять действия в системе"
    )

class UpdateName(BaseModel):
    username: str = Field(
        default=...,
        title="Новый никнейм пользователя",
        max_length=30,
        examples=["John", "Mike", "Asriel"],
        description="Новый никнейм пользователя, используемый в авторизации и как отличительная черта пользователя"
    )

class UpdateEmail(BaseModel):
    email: EmailStr = Field(
        default=...,
        title="Новый email пользователя",
        examples=["john@example.com", "mike@example.com", "asriel@example.com"],
        description="Новая электронная почта пользователя"
    )

class UpdatePassword(BaseModel):
    old_password: str = Field(
        default=...,
        title="Старый пароль пользователя",
        min_length=8,
        max_length=32,
        examples=["12345678", "qwerty25"],
        description="Старый пароль пользователя, который будет заменён на новый"
    )
    new_password: str = Field(
        default=...,
        title="Новый пароль пользователя",
        min_length=8,
        max_length=32,
        examples=["12345678", "qwerty25"],
        description="Новый пароль пользователя, который будет после использоваться при авторизации"
    )

# схемы тикетов
class TicketBase(BaseModel):
    chat_id: int = Field(
        default=...,
        title="ID чата",
        examples=[1563],
        description="ID чата, связанного с тикетом"
    )
    priority_id: int = Field(
        default=...,
        title="ID приоритета",
        examples=[1, 2, 3, 4],
        description="ID уровня важности тикета из таблицы приоритетов",
        ge=1
    )

class TicketCreate(BaseModel):
    chat_id: int = Field(
        default=...,
        title="ID чата",
        examples=[1563],
        description="ID чата, связанного с тикетом",
        ge=1
    )
    priority_id: int = Field(
        default=...,
        title="ID приоритета",
        examples=[1, 2, 3, 4],
        description="ID уровня важности тикета из таблицы приоритетов",
        ge=1
    )
    service: str | None = Field(
        default=None,
        title="Сервис",
        max_length=1000,
        examples=["API Gateway", "Authentication", "Database"],
        description="Сервис, в котором возникла проблема"
    )
    summary: str | None = Field(
        default=None,
        title="Краткое описание",
        max_length=10000,
        examples=["Ошибка аутентификации при входе через Google"],
        description="Краткое описание проблемы"
    )
    trace: str | None = Field(
        default=None,
        title="Шаги воспроизведения",
        max_length=10000,
        examples=["1. Открыть приложение\n2. Нажать 'Войти через Google'\n3. Ввести учетные данные"],
        description="Шаги пользователя для воспроизведения проблемы"
    )
    back_logs: str | None = Field(
        default=None,
        title="Логи бэкенда",
        max_length=10000,
        examples=["ERROR 500: Internal Server Error\nat AuthService.login (auth.service.ts:25:13)"],
        description="Логи бэкенда для анализа"
    )
    front_logs: str | None = Field(
        default=None,
        title="Логи фронтенда",
        max_length=10000,
        examples=["Error: Failed to load resource: the server responded with a status of 500 (Internal Server Error)"],
        description="Логи фронтенда для анализа"
    )

class TicketResponse(BaseModel):
    id: int = Field(
        default=...,
        title="ID тикета",
        examples=[42],
        description="Уникальный идентификатор тикета в системе",
        ge=1
    )
    chat_id: int = Field(
        default=...,
        title="ID чата",
        examples=[1563],
        description="ID связанного чата, из которого был создан тикет",
        ge=1
    )
    priority: str = Field(
        default=...,
        title="Приоритет",
        max_length=20,
        examples=["Низкая", "Средняя", "Высокая", "Критическая"],
        description="Уровень важности и срочности решения тикета"
    )
    priority_id: int = Field(
        default=...,
        title="ID приоритета",
        examples=[1, 2, 3, 4],
        description="Идентификатор уровня приоритета из таблиции приоритетов",
        ge=1
    )
    service: str = Field(
        default=...,
        title="Сервис",
        max_length=100,
        examples=["API Gateway", "Authentication", "Database"],
        description="Название сервиса или компонента системы, в котором возникла проблема"
    )
    summary: str = Field(
        default=...,
        title="Краткое описание",
        max_length=10000,
        examples=["Ошибка аутентификации при входе через Google"],
        description="Краткое резюме проблемы, сгенерированное системой или введенное пользователем"
    )
    trace: str = Field(
        default=...,
        title="Шаги воспроизведения",
        max_length=10000,
        examples=["1. Открыть приложение\n2. Нажать 'Войти через Google'\n3. Ввести учетные данные"],
        description="Пошаговое описание действий, приводящих к ошибке, в формате XML или текста"
    )
    back_logs: str = Field(
        default="",
        title="Бэкенд логи ошибки",
        max_length=10000,
        examples=["ERROR 500: Internal Server Error\nat AuthService.login (auth.service.ts:25:13)"],
        description="Логи бэкенда для анализа"
    )
    front_logs: str = Field(
        default="",
        title="Фронтенд логи ошибки",
        max_length=10000,
        examples=["Error: Failed to load resource: the server responded with a status of 500 (Internal Server Error)"],
        description="Логи фронтенда для анализа"
    )
    user_id: int = Field(
        default=...,
        title="ID пользователя",
        examples=[831],
        description="Идентификатор пользователя, создавшего тикет",
        ge=1
    )
    username: str = Field(
        default=...,
        title="Имя пользователя",
        max_length=30,
        examples=["John", "Mike", "Asriel"],
        description="Имя пользователя, создавшего тикет"
    )
    email: EmailStr = Field(
        default=...,
        title="Email пользователя",
        examples=["john@example.com", "mike@example.com", "asriel@example.com"],
        description="Электронная почта пользователя для обратной связи"
    )
    role_id: int = Field(
        default=...,
        title="ID роли пользователя",
        examples=[1, 2, 3],
        description="Идентификатор роли пользователя в системе",
        ge=1
    )
    role: str = Field(
        default=...,
        title="Роль пользователя",
        max_length=60,
        examples=["Оператор", "Тестировщик"],
        description="Роль пользователя, создавшего тикет"
    )
    date_of_create: datetime = Field(
        default=...,
        title="Дата создания",
        examples=[datetime.now()],
        description="Дата и время создания тикета в формате ISO 8601"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 42, 
                "chat_id": 1563,
                "priority": "Высокая",
                "priority_id": 3,
                "service": "Authentication",
                "summary": "Ошибка аутентификации при входе через Google",
                "trace": "<error>\n<step>1. Открыть приложение</step>\n<step>2. Нажать 'Войти через Google'</step>\n</error>",
                "back_logs": "ERROR 500: Internal Server Error",
                "front_logs": "Error: Failed to load resource",
                "user_id": 831,
                "username": "John",
                "email": "john@example.com",
                "role_id": 2,
                "role": "Оператор",
                "date_of_create": "2025-07-28T12:34:56.789Z"
            }
        }

class TicketUpdate(BaseModel):
    id: int = Field(
        default=...,
        title="ID тикета",
        examples=[42],
        description="Уникальный идентификатор обновляемого тикета",
        ge=1
    )
    chat_id: int = Field(
        default=...,
        title="ID чата",
        examples=[1563],
        description="ID чата, связанного с тикетом",
        ge=1
    )
    priority_id: int = Field(
        default=...,
        title="ID приоритета",
        examples=[1, 2, 3, 4],
        description="ID уровня важности тикета из таблицы приоритетов",
        ge=1
    )
    service: str = Field(
        default=...,
        title="Сервис",
        max_length=1000,
        examples=["API Gateway", "Authentication", "Database"],
        description="Сервис, в котором возникла проблема"
    )
    summary: str = Field(
        default=...,
        title="Краткое описание",
        max_length=10000,
        examples=["Ошибка аутентификации при входе через Google"],
        description="Краткое описание проблемы"
    )
    trace: str = Field(
        default=...,
        title="Шаги воспроизведения",
        max_length=10000,
        examples=["1. Открыть приложение\n2. Нажать 'Войти через Google'\n3. Ввести учетные данные"],
        description="Шаги пользователя для воспроизведения проблемы"
    )
    back_logs: str = Field( 
        default="",
        title="Логи бэкенда",
        max_length=10000,
        examples=["ERROR 500: Internal Server Error\nat AuthService.login (auth.service.ts:25:13)"],
        description="Логи бэкенда для анализа"
    )
    front_logs: str = Field(
        default="",
        title="Логи фронтенда",
        max_length=10000,
        examples=["Error: Failed to load resource: the server responded with a status of 500 (Internal Server Error)"],
        description="Логи фронтенда для анализа"
    )

    class Config:
        from_attributes = True


class TicketList(BaseModel):
    tickets: list[TicketResponse] = Field(
        default=...,
        title="Список тикетов",
        examples=[[{
            "ticket_id": 42,
            "chat_id": 1563,
            "priority": "high",
            "service": "Authentication",
            "summary": "Ошибка аутентификации",
            "trace": "Шаги воспроизведения...",
            "logs": "Логи ошибки...",
            "user_id": 831,
            "username": "John",
            "email": "john@example.com",
            "role": "user",
            "date_of_create": "2025-07-15T12:00:00"
        }]],
        description="Список всех тикетов пользователя"
    )

class PriorityBase(BaseModel):
    id: int = Field(
        default=...,
        title="ID приоритета",
        examples=[1, 2, 3, 4],
        description="Уникальный идентификатор уровня приоритета",
    )

    priority: str = Field(
        default=...,
        title="Название приоритета",
        max_length=20,
        examples=["Низкая", "Средняя", "Высокая", "Критическая"],
        description="Название уровня приоритета тикета"
    )
    
    class Config:
        from_attributes = True

class PriorityCreate(PriorityBase):
    pass

class Priority(PriorityBase):
    pass


class RoleBase(BaseModel):
    id: int = Field(
        default =...,
        title="ID роли",
        examples=[1, 2, 3],
        description="Уникальный идентификатор роли пользователя"
    )

    role: str = Field(
        default=...,
        title="Название роли",
        examples=["Оператор", "Разработчик", "Тестировщик"],
        description="Название роли пользователя"
    )

    prompt: str = Field(
        default=...,
        title="Текст промпта",
        examples=["Ты — ассистент поддержки. Анализируй скриншоты и давай простые инструкции. Ответ в XML:\n\n<chat>\n[Название проблемы простыми словами]\n</chat>\n\n<system>\n[Программа/сервис + версия если видна]\n</system>\n\n<problem>\n[Описание проблемы для нетехнического пользователя]\n</problem>\n\n<solution>\n<step>[Действие 1]</step>\n<step>[Действие 2]</step>\n</solution>",
                  "Ты — технический ассистент. Анализируй скриншоты с кодами ошибок. Ответ в XML:\n\n<chat>\n[Название ошибки/проблемы]\n</chat>\n\n<system>\n[ОС, версия ПО, среда выполнения]\n</system>\n\n<problem>\n[Точный текст ошибки + контекст]\n</problem>\n\n<cause>\n[Root cause с техническими деталями]\n</cause>\n\n<solution>\n<step>[Техническое действие 1]</step>\n<step>[Проверка/валидация]</step>\n<step>[Фикс/рабораунд]</step>\n</solution>",
                  "Ты — QA-ассистент. Анализируй скриншоты для воспроизведения багов. Ответ в XML:\n\n<chat>\n[Название дефекта]\n</chat>\n\n<system>\n[Тестовая среда и build]\n</system>\n\n<solution>\n<step>[Шаг 1]</step>\n<step>[Шаг 2]</step>\n</solution>\n\n<expected>\n[Ожидаемое поведение]\n</expected>\n\n<actual>\n[Фактический результат]\n</actual>\n\n<severity>\n[Критичность: Low/Medium/High/Critical]\n</severity>"],
        description="Текст промпта для пользователя опеределенной роли"
    )

    description: str = Field(
        default=...,
        title="Описание роли",
        max_length=500,
        examples=["Упрощенные инструкции и фокус на действия пользователя", "Технический анализ с акцентом на код"],
        description="Краткое описание особенностей роли и типа предоставляемой помощи"
    )

    is_admin: bool = Field(
        default=...,
        title="Администратор ли",
        examples=[True, False],
        description="Флаг, указывающий на администрирующую роль"
    )


class Role(RoleBase):
    pass
