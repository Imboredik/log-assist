from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile
from datetime import timedelta
import requests
import logging
import base64

from .config import config_values

logger = logging.getLogger(__name__)

# Экземпляр класса MinIO
minio_client = Minio(
    endpoint=config_values.MINIO_ENDPOINT,
    access_key=config_values.MINIO_ACCESS_KEY,
    secret_key=config_values.MINIO_SECRET_KEY,
    secure=config_values.MINIO_SECURE
)


# Проверка подключения к серверу Minio
logger.info("Проверка подключения к серверу Minio...")
protocol = "https" if config_values.MINIO_SECURE else "http"
try:
    if not requests.get(url=f"{protocol}://{config_values.MINIO_ENDPOINT}/minio/health/live").status_code == 200:
        raise ValueError("Ошибка подключения к серверу Minio")
except requests.exceptions.ConnectionError:
    raise ValueError("Ошибка соединения с сервером Minio")
logger.info("Успешное подключение к серверу Minio!")


def create_bucket(user_id: int) -> bool:
    """Создание bucket пользователя (хранилище пользователя)"""
    user_bucket = f"user-{str(user_id)}"
    if not minio_client.bucket_exists(user_bucket):
        minio_client.make_bucket(user_bucket)
    return True

def delete_bucket(user_id: int) -> bool:
    """Удаление bucket пользователя (хранилища пользователя)"""
    user_bucket = f"user-{str(user_id)}"
    if minio_client.bucket_exists(user_bucket):
        minio_client.remove_bucket(user_bucket)
        result = True
    else:
        result = False
    return result

def get_avatar_by_id(user_id: int) -> str:
    """Получение аватара по id пользователя"""
    user_bucket = f"user-{str(user_id)}"
    if not minio_client.bucket_exists(user_bucket):
        raise ValueError("Бакета не существует")
    for obj in minio_client.list_objects(user_bucket):
        if "avatar" in obj.object_name:
            return minio_client.get_presigned_url("GET", user_bucket, obj.object_name, expires=timedelta(days=1))

def delete_avatar_by_id(user_id: int) -> bool:
    """Удаление пользовательского аватара"""
    try:
        user_bucket = f"user-{str(user_id)}"
        if not minio_client.bucket_exists(user_bucket):
            raise ValueError("Бакета не существует")
        for obj in minio_client.list_objects(user_bucket):
            if "avatar" in obj.object_name:
                minio_client.remove_object(user_bucket, obj.object_name)
        return True
    except S3Error:
        return False

def update_avatar_by_id(user_id: int, file: UploadFile) -> str:
    """Обновление аватарки пользователя"""
    new_obj_name = f"avatar.{file.filename.split('.')[-1]}"
    user_bucket = f"user-{str(user_id)}"
    if not minio_client.bucket_exists(user_bucket):
        raise ValueError("Бакета не существует")
    for obj in minio_client.list_objects(user_bucket):
        if "avatar" in obj.object_name:
            minio_client.remove_object(user_bucket, obj.object_name)
    minio_client.put_object(
        bucket_name=user_bucket,
        object_name=new_obj_name,
        data=file.file,
        length=-1,
        part_size=10*1024*1024,
        content_type=file.content_type
    )
    return minio_client.get_presigned_url("GET", user_bucket, new_obj_name, expires=timedelta(days=1))

def upload_message_image(user_id: int, chat_id: int, message_id: int, image_id: int, file: UploadFile) -> str:
    """Загрузка изображения на сервер Minio по id чата, сообщения, изображения"""
    user_bucket = f"user-{str(user_id)}"
    if not minio_client.bucket_exists(user_bucket):
        raise ValueError("Бакета не существует")
    file.file.seek(0)
    minio_client.put_object(
        bucket_name=user_bucket,
        object_name=f"chats/{chat_id}/{message_id}/{image_id}.{file.filename.split('.')[-1]}",
        data=file.file,
        length=-1,
        part_size=10*1024*1024,
        content_type=file.content_type
    )
    return minio_client.get_presigned_url(
        method="GET",
        bucket_name=user_bucket,
        object_name=f"chats/{chat_id}/{message_id}/{image_id}.{file.filename.split('.')[-1]}",
        expires=timedelta(days=1)
    )

def get_message_image(user_id: int, chat_id: int, message: int) -> list[str] | None:
    """Функция для получения списка изображений в формате base64 к сообщению или None в случае отсутствия из minio"""
    result = []
    user_bucket = f"user-{str(user_id)}"
    if not minio_client.bucket_exists(user_bucket):
        raise ValueError("Бакета не существует")
    objects = minio_client.list_objects(user_bucket, f"chats/{chat_id}/{message}/", recursive=True)
    for obj in objects:
        obj_file = minio_client.get_object(user_bucket, obj.object_name).read()
        base64_str = base64.b64encode(obj_file).decode("utf-8")
        mime_type = f"image/{"jpeg" if obj.object_name.endswith('.jpg') else obj.object_name.split('.')[-1].lower()}"
        result.append(f"data:{mime_type};base64," + base64_str)
    if not result:
        result = None
    return result

def get_url_image(user_id: int, chat_id: int, message: int) -> list[str] | None:
    """Функция для получения списка ссылок на изображения, прикреплённые к сообщению или в случае отсутствия None на сервере minio"""
    result = []
    user_bucket = f"user-{str(user_id)}"
    if not minio_client.bucket_exists(user_bucket):
        raise ValueError("Бакета не существует")
    objects = minio_client.list_objects(user_bucket, f"chats/{chat_id}/{message}/", recursive=True)
    for obj in objects:
        obj_url = minio_client.get_presigned_url("GET", user_bucket, obj.object_name, expires=timedelta(days=1))
        result.append(obj_url)
    if not result:
        result = None
    return result
