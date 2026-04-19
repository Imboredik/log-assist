from tiktoken import encoding_for_model, get_encoding
from fastapi import HTTPException
from math import ceil
from PIL import Image
import logging
import base64
import httpx
import io
import re

from .config import config_values

DEFAULT_SYSTEM_PROMPT = """"""
TOKENS_PER_MESSAGE = 3
MAX_CONTEXT_TOKENS = config_values.MAX_CONTEXT_TOKENS
MAX_OUTPUT_TOKENS = config_values.MAX_OUTPUT_TOKENS
OPENROUTER_API_KEY = config_values.OPENROUTER_API_KEY
OPENROUTER_URL = config_values.OPENROUTER_BASE_URL

logger = logging.getLogger(__name__)

logger.info("Определение токен encode...")
try:
    model_name = config_values.OPENROUTER_MODEL.split("/")[-1]
    encoding = encoding_for_model(model_name)
except KeyError:
    encoding = get_encoding("cl100k_base")
logger.info(f"Выбран: {encoding.name}")

logger.info("Определение количества токенов системного сообщения...")
SYSTEM_PROMPT_TOKENS = len(encoding.encode(DEFAULT_SYSTEM_PROMPT))
logger.info(f"TOKENS: {SYSTEM_PROMPT_TOKENS}")

class OpenRouterMessage:
    def __init__(self, role: str, text: str, images: list[str] = None):
        self.role = role
        self.text = text
        self.images = images or []

    def count_tokens(self) -> int:
        """Подсчёт токенов в сообщении класса"""
        # Токены текстового сообщения
        token = TOKENS_PER_MESSAGE + len(encoding.encode(self.text))
        # Токены изображений
        for image in self.images:
            if isinstance(image, str):  # Проверяем не строка base64 ли, для работы с несколькими скриншотами в расширении
                if image.startswith("data:"):
                    image = re.sub(r"^data:image\/\w+;base64,", "", image)
                try:
                    with Image.open(io.BytesIO(base64.b64decode(image))) as img:
                        width, height = img.size
                    if width > 1024 or height > 1024:
                        if width > height:
                            height = int(height * 1024 / width)
                            width = 1024
                        else:
                            width = int(width * 1024 / height)
                            height = 1024
                    height_token = ceil(height / 512)
                    width_token = ceil(width / 512)
                    token += 85 + 170 * height_token * width_token
                except Exception as e:
                    logger.error(f"Error processing image: {str(e)}")
                    continue
        return token

    def size_check(self) -> bool:
        """Проверка на то, выходит ли сообщение за ограничения по размерам"""
        return self.count_tokens() < MAX_CONTEXT_TOKENS + MAX_OUTPUT_TOKENS - SYSTEM_PROMPT_TOKENS

    def to_response(self) -> dict | None:
        """Перевод сообщения в формат, необходимый для отправки на openrouter"""
        content = [{"type": "text", "text": self.text}]
        if self.images:
            for image in self.images:
                if image != "":
                    content.append({
                        "type": "image_url",
                        "image_url": image
                    })
        if self.role == "ai":
            result = {"role": "assistant", "content": content}
        elif self.role == "user":
            result = {"role": self.role, "content": content}
        elif self.role == "system":
            result = {"role": self.role, "content": content}
        else:
            result = None
        return result

class OpenRouterChat:
    def __init__(
            self,
            messages_history: list[OpenRouterMessage] = None,
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            max_context_tokens: int = MAX_CONTEXT_TOKENS,
            max_output_tokens: int = MAX_OUTPUT_TOKENS
    ):
        self.messages = [OpenRouterMessage(role="system", text=DEFAULT_SYSTEM_PROMPT)]
        if messages_history:
            self.messages += messages_history
        self.system_prompt = system_prompt
        self.max_context_tokens = max_context_tokens
        self.max_output_tokens = max_output_tokens

    def count_tokens(self) -> int:
        """Подсчёт общего количества токенов в чате"""
        token = 0
        for message in self.messages:
            token += message.count_tokens()
        logger.info(f"OpenRouter отправлено TOKENS: {token}")
        return token

    def trim_history(self):
        """Удаление старых сообщений из чата при превышении токенов"""
        while self.count_tokens() > self.max_context_tokens + self.max_output_tokens:
            if len(self.messages) > 1:
                del self.messages[1]
            else:
                break

    async def get_response(self, message: OpenRouterMessage) -> str:
        """Отправка сообщения/сообщений на API OpenRouter"""
        self.messages.append(message)
        self.trim_history()
        if len(self.messages) == 1:
            raise HTTPException(status_code=400, detail="Сообщение слишком большое")
        messages_for_response = []
        for chat_message in self.messages:
            messages_for_response.append(chat_message.to_response())
        # Формирование запроса
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": config_values.OPENROUTER_MODEL,
            "messages": messages_for_response,
            "max_tokens": self.max_output_tokens
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                OPENROUTER_URL,
                headers=headers,
                json=data,
                timeout=httpx.Timeout(180)
            )
            if response.status_code == 200 and not "error" in response.json().keys():
                answer = response.json()["choices"][0]["message"]["content"]
                self.messages.append(OpenRouterMessage(role="ai", text=answer))
                return answer
            else:
                raise Exception(f"Ошибка взаимодействия с OpenRouter: {response.status_code} - {response.json()}")
