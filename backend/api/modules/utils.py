from bcrypt import checkpw, hashpw, gensalt
from jose import jwt
import datetime
import re
import base64
from fastapi import UploadFile
import io

from .config import config_values

def password_hash(password: str) -> str:
    """Получение хэша пароля"""
    return hashpw(password.encode("UTF-8"), gensalt()).decode("UTF-8")

def verify_password(password: str, hashed_password: str) -> bool:
    """Проверка принадлежности пароля к хэшу"""
    return checkpw(password.encode("UTF-8"), hashed_password.encode("UTF-8"))

def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None) -> str:
    """Функция для генерации JWT токена по информации и срока действия"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=config_values.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config_values.SECRET_KEY, algorithm=config_values.ALGORITHM)
    return encoded_jwt

def simple_summarizer(text: str, max_chars: int = 20, markdown: bool = True) -> str:
    """Сокращает текст до max_chars символов, заменяя все последующие символы многоточием"""
    if markdown:
        cleaned_text = " ".join(text.split(" ")).strip()
    else:
        new_line = ""
        for char in text:
            if not char in "#*`-":
                new_line += char
        cleaned_text = " ".join(new_line.split()).strip()
    if len(cleaned_text) <= max_chars:
        result = cleaned_text
    else:
        available = max_chars - 3
        last_space = cleaned_text.rfind(" ", 0, available + 1)
        if last_space == -1:
            result = cleaned_text[:available] + "..."
        else:
            result = cleaned_text[:last_space] + "..."
    return result

def parse_tags(text) -> dict:
    """Парсит текст с тегами и возвращает словарь с выделенными блоками"""
    tags = [
        'chat', 'service', 'summary', 'trace', 
        'solution', 'expected', 'actual', 'severity','chat_name'
    ]
    
    result = {}
    
    for tag in tags:
        pattern = re.compile(r'<{}>(.*?)</{}>'.format(tag, tag), re.DOTALL)
        match = pattern.search(text)
        
        if match:
            result[tag] = match.group(1).strip()
        else:
            result[tag] = None
    
    return result

def create_upload_file_from_base64(base64_str: str) -> UploadFile:
    """Создает объект UploadFile из base64 строки изображения"""
    if not base64_str.startswith('data:image/'):
        raise ValueError("Invalid base64 image format")
    
    content_type = base64_str.split(';')[0].split(':')[1]
    extension = content_type.split('/')[1]
    
    image_data = base64_str.split(',')[1]
    image_bytes = base64.b64decode(image_data)
    
    temp_file = io.BytesIO(image_bytes)
    return UploadFile(
        filename=f"image.{extension}",
        file=temp_file,
        headers={"content-type": content_type}
    )

def timestamp_category(time: datetime.datetime) -> str:
    """Функция для определения категории времени (Сегодня, Вчера, 7 дней, 30 дней, [год]-[месяц])"""
    time_date = time.date()
    today_date = datetime.datetime.today().date()
    delta_time = (today_date - time_date).days
    if delta_time == 0:
        result = "Сегодня"
    elif delta_time == 1:
        result = "Вчера"
    elif delta_time <= 7:
        result = "7 дней"
    elif delta_time <= 30:
        result = "30 дней"
    else:
        result = time_date.strftime("%Y-%m")
    return result

def print_logo() -> None:
    """Функция выводящая красивую надпись в консоль"""
    print("""
  _                   _            _     _        _    ____ ___ 
 | |    ___   __ _   / \\   ___ ___(_)___| |_     / \\  |  _ \\_ _|
 | |   / _ \\ / _` | / _ \\ / __/ __| / __| __|   / _ \\ | |_) | | 
 | |__| (_) | (_| |/ ___ \\\\__ \\__ \\ \\__ \\ |_   / ___ \\|  __/| | 
 |_____\\___/ \\__, /_/   \\_\\___/___/_|___/\\__| /_/   \\_\\_|  |___|
             |___/                                              
    """)
