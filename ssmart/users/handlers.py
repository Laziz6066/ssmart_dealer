from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import ssmart.users.keyboards as kb
import ssmart.database.requests as rq
import logging


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = await kb.get_main_keyboard(message.from_user.id)
    photo = "https://sun9-77.userapi.com/KWoCJ3Smj_J7QyoEci1kEAU2Lyp9YOHvmI6DnA/SXtJSQwIFKw.jpg"

    await message.answer_photo(photo=photo, caption="Добро пожаловать в дилерский центр Ssmart.",
                               reply_markup=keyboard)


@router.message(F.text == 'Контакты')
async def contacts(message: Message):
    keyboard = await kb.get_contacts()
    await message.reply("Тут будет текст типа:\nПо техническим вопросам выберите Сервисный центр\n"
                        "По остальным вопросам выберите Менеджер.", reply_markup=keyboard)


@router.message(F.text == 'Сервисный центр')
async def contacts(message: Message):
    await message.reply("+998901234567")


@router.message(F.text == 'Менеджер')
async def contacts(message: Message):
    await message.reply("+998999999999")


@router.message(F.text == 'Главное меню')
async def contacts(message: Message):
    keyboard = await kb.get_main_keyboard(message.from_user.id)
    await message.answer(text='Добро пожаловать в дилерский центр Ssmart.', reply_markup=keyboard)


@router.message(F.text == 'О нас')
async def contacts(message: Message):
    await message.answer("Можно что-то написать или фото отправить (сертификат/гувохнома)")


@router.message(F.text == 'Каталог')
async def view_catalog(message: Message):
    await message.answer('Выберите категорию:', reply_markup=await kb.show_categories())


@router.callback_query(F.data.startswith('show_category_'))
async def show_brands(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[-1])
    keyboard = await kb.show_brands(category_id)
    await callback.message.edit_text("Выберите бренд:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('show_brand_'))
async def show_subcategories(callback: CallbackQuery):
    brand_id = int(callback.data.split('_')[-2])
    category_id = int(callback.data.split('_')[-1])
    keyboard = await kb.show_subcategories(brand_id, category_id)
    await callback.message.edit_text("Выберите подкатегорию:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('show_subcategory_'))
async def show_items(callback: CallbackQuery):
    brand_id = int(callback.data.split('_')[-2])
    category_id = int(callback.data.split('_')[-1])
    subcategory_id = int(callback.data.split('_')[-3])
    items = await rq.get_items(category_id, brand_id, subcategory_id)
    if not items:
        await callback.message.answer("Товары не найдены.")
        return
    for item in items:
        await callback.message.answer_photo(
            photo=item.photo,
            caption=f"{item.name}\n{item.description}\nЦена: {item.price:,.0f} UZS.".replace(",", " "),
            reply_markup=kb.item_keyboard(item.id)
        )

    await callback.answer()


