import asyncio

from ssmart.utils.atmos_api import check_payment_status


async def monitor_payment(payment_id: int, user_id: int, chat_id: int, item_id: int, amount: int, bot):
    from ssmart.database import requests as rq

    lang = await rq.get_user(user_id)
    for _ in range(24):
        status = await check_payment_status(payment_id)
        if status == "SUCCESS":
            await rq.add_transaction(user_id, item_id, amount, payment_id)
            msg = "✅ Оплата успешно выполнена!" if lang == 'ru' else "✅ To'lov muvaffaqiyatli amalga oshirildi!"
            await bot.send_message(chat_id, msg)
            return
        await asyncio.sleep(5)

    msg = ("⚠️ Оплата не подтверждена. Попробуйте позже." if lang == 'ru'
           else "⚠️ To'lov tasdiqlanmadi. Keyinroq urinib ko'ring.")
    await bot.send_message(chat_id, msg)
