import os

import aiohttp
import asyncio
import uuid
from ssmart.utils.token_manager import AtmosTokenManager
from ssmart.database import requests as rq

# Инициализация менеджера токенов
_token_manager = AtmosTokenManager()

async def create_invoice(amount: int, item_name: str, item_id: int, user_id: int):
    access_token = await _token_manager.get_valid_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "request_id": str(uuid.uuid4()),
        "store_id": int(os.getenv("ATMOS_STORE_ID")),
        "amount": amount,
        "account": str(user_id),
        "expiration_time": 10,
        "success_url": "https://atmos.uz",
        "items": [
            {
                "items_id": str(item_id),
                "name": item_name,
                "amount": amount,
                "quantity": 1
            }
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post("https://apigw.atmos.uz/mps/checkout/invoice/create",
                                 headers=headers, json=payload) as response:
            return await response.json()

async def check_payment_status(payment_id: int):
    url = f"https://apigw.atmos.uz/mps/transaction/get/{payment_id}"
    access_token = await _token_manager.get_valid_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status != 200:
                return None
            data = await response.json()

    if data.get("payload"):
        payload = data["payload"]
        result_code = payload.get("result_code", "").upper()
        transaction_status = payload.get("transaction_status", "").upper()
        status_ps = payload.get("status_ps", "")
        if result_code == "ACCEPTED" or transaction_status == "SUCCESS" or "Accepted" in status_ps:
            return "SUCCESS"
    return "PENDING"

async def monitor_payment(payment_id: int, user_id: int, chat_id: int, item_id: int, amount: int, bot):
    lang = await rq.get_user(user_id)
    for _ in range(24):
        status = await check_payment_status(payment_id)
        if status == "SUCCESS":
            await rq.add_transaction(user_id, item_id, amount, payment_id)
            success_msg = "✅ Оплата успешно выполнена!" if lang == 'ru' else "✅ To'lov muvaffaqiyatli amalga oshirildi!"
            await bot.send_message(chat_id, success_msg)
            return
        await asyncio.sleep(5)

    fail_msg = "⚠️ Оплата не подтверждена. Попробуйте позже или обратитесь в поддержку." if lang == 'ru' else "⚠️ To'lov tasdiqlanmadi. Keyinroq qayta urinib ko'ring."
    await bot.send_message(chat_id, fail_msg)
