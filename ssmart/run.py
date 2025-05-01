import os
import asyncio
import logging
from pythonjsonlogger import jsonlogger
from aiogram import Bot, Dispatcher
from ssmart.users.handlers import router
from ssmart.admin.handlers.admin_menu import admin_router
from ssmart.admin.handlers.category import category_router
from ssmart.admin.handlers.brand import brand_router
from ssmart.admin.handlers.add_item import add_item_router
from ssmart.admin.handlers.delete_item import del_item_router
from ssmart.admin.handlers.update_item import upd_item_router
from ssmart.admin.handlers.subcategory import subcategory_router
from ssmart.database.models import async_main
from dotenv import load_dotenv

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
#
# logHandler = logging.FileHandler('bot_logs.json', encoding='utf-8')
# formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
#
# logHandler.setFormatter(formatter)
# logger.addHandler(logHandler)

async def main():
    await async_main()
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_router(subcategory_router)
    dp.include_router(router)
    dp.include_router(admin_router)
    dp.include_router(category_router)
    dp.include_router(brand_router)
    dp.include_router(add_item_router)
    dp.include_router(del_item_router)
    dp.include_router(upd_item_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
