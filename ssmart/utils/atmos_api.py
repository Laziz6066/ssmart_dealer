import logging
import os
from datetime import datetime

import aiohttp
import asyncio
import uuid
from ssmart.utils.token_manager import AtmosTokenManager
from ssmart.database import requests as rq

# Инициализация менеджера токенов
_token_manager = AtmosTokenManager()

async def create_invoice(amount: int, item_name: str, item_id: int, account: str):
    """
    Создание счёта через /merchant/pay/create/checkout-ofd (для checkout.pays.uz)
    Возвращает JSON, в котором содержится transaction_id для формирования ссылки.
    """
    access_token = await AtmosTokenManager().get_valid_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "amount": amount,
        "account": account,
        "store_id": int(os.getenv("ATMOS_STORE_ID")),
        "terminal_id": int(os.getenv("ATMOS_TERMINAL_ID")),
        "lang": "ru",
        "ofd_items": [
            {
                "ofd_code": str(uuid.uuid4())[:8],
                "name": item_name,
                "amount": amount
            }
        ]
    }

    url = "https://partner.atmos.uz/merchant/pay/create/checkout-ofd"
    logging.info(f"\ud83d\udce6 Payload create_invoice: {payload}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                text = await response.text()
                logging.info(f"\ud83d\udce9 ATMOS ответ: {text}")
                if response.status == 200 and response.headers.get("Content-Type", "").startswith("application/json"):
                    return await response.json()
                else:
                    return {"status": {"code": "ERROR", "description": text}}
    except Exception as e:
        logging.error(f"Ошибка при обращении к ATMOS: {e}")
        return {"status": {"code": "EXCEPTION", "description": str(e)}}



async def check_payment_status(payment_id: int):
    url = f"https://partner.atmos.uz/mps/transaction/get/{payment_id}"
    access_token = await _token_manager.get_valid_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return None
            data = await response.json()

    return data.get("store_transaction", {})

