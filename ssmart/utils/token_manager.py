import os
import base64
import aiohttp
from datetime import datetime, timedelta

TOKEN_URL = "https://partner.atmos.uz/token"

class AtmosTokenManager:
    def __init__(self):
        self.token_data = None
        self.consumer_key = os.getenv("ATMOS_CONSUMER_KEY")
        self.consumer_secret = os.getenv("ATMOS_CONSUMER_SECRET")

        if not self.consumer_key or not self.consumer_secret:
            raise RuntimeError("❌ Не найдены ATMOS_CONSUMER_KEY и ATMOS_CONSUMER_SECRET в переменных окружения.")

    async def get_token(self):
        """Запрос нового access_token от ATMOS"""
        auth_string = f"{self.consumer_key}:{self.consumer_secret}"
        b64_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {b64_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = "grant_type=client_credentials"

        async with aiohttp.ClientSession() as session:
            async with session.post(TOKEN_URL, headers=headers, data=data) as response:
                if response.status != 200:
                    text = await response.text()
                    raise RuntimeError(f"Ошибка получения токена: {response.status} {text}")
                json_data = await response.json()

        access_token = json_data.get("access_token")
        expires_in = json_data.get("expires_in", 3600)
        token_type = json_data.get("token_type", "Bearer")

        self.token_data = {
            "access_token": access_token,
            "token_type": token_type,
            "expires_at": datetime.utcnow() + timedelta(seconds=expires_in)
        }

        return self.token_data

    def is_token_valid(self):
        """Проверка, истёк ли токен"""
        if not self.token_data:
            return False
        return datetime.utcnow() < self.token_data["expires_at"] - timedelta(seconds=30)

    async def get_valid_token(self):
        """Получить актуальный access_token (если устарел — обновить)"""
        if self.is_token_valid():
            return self.token_data["access_token"]
        await self.get_token()
        return self.token_data["access_token"]
