import asyncio

from ssmart.database.requests import add_transaction
from ssmart.utils.atmos_api import check_payment_status


async def monitor_payment(payment_id: int, user_id: int, chat_id: int,
                          item_id: int, amount: int, account: str, bot):
    for attempt in range(24):  # 2 минуты мониторинга
        await asyncio.sleep(5)
        status = await check_payment_status(payment_id)

        if isinstance(status, dict) and status.get("confirmed"):
            await add_transaction(user_id, item_id, amount, payment_id, account)
            await bot.send_message(chat_id, "✅ Оплата успешно завершена!")
            return
        else:
            if attempt == 0:
                await bot.send_message(chat_id, "⌛ Ожидаем подтверждения оплаты...")

    await bot.send_message(chat_id, "⏳ Время ожидания оплаты истекло. Попробуйте ещё раз.")
