import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from ssmart.users.handlers import router
from ssmart.admin.handlers.admin_menu import admin_router
from ssmart.admin.handlers.category import category_router
from ssmart.admin.handlers.brand import brand_router
from ssmart.admin.handlers.item import item_router
from ssmart.admin.handlers.subcategory import subcategory_router
from ssmart.database.models import async_main
from dotenv import load_dotenv


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
    dp.include_router(item_router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
