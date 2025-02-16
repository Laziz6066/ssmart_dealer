from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ssmart.config import ADMINS
from ssmart.database.requests import get_subcategories, get_brands, get_categories


async def admin_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    if user_id in ADMINS:
        buttons = [
            [KeyboardButton(text='Добавить категорию'), KeyboardButton(text='Удалить категорию')],
            [KeyboardButton(text='Добавить бренд'), KeyboardButton(text='Удалить бренд')],
            [KeyboardButton(text='Добавить подкатегорию'), KeyboardButton(text='Удалить подкатегорию')],
            [KeyboardButton(text='Добавить товар'), KeyboardButton(text='Удалить товар')],
            [KeyboardButton(text='На главную')]
        ]
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def add_categories(for_admin=False):
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        cb_data = f'add_category_{category.id}' if for_admin else f'show_category_{category.id}'
        keyboard.add(InlineKeyboardButton(text=category.name_ru, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))

    return keyboard.adjust(2).as_markup()


async def add_brands(category_id):
    all_brands = await get_brands(category_id)
    keyboard = InlineKeyboardBuilder()

    for brand in all_brands:
        cb_data = f'add_brands_{brand.id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=brand.name_ru, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_categories'))

    return keyboard.adjust(2).as_markup()


async def add_subcategories(brand_id, category_id, for_admin=False):
    all_subcategories = await get_subcategories(brand_id, category_id)
    keyboard = InlineKeyboardBuilder()

    for subcategory in all_subcategories:
        cb_data = f'add_subcategory_{subcategory.id}_{brand_id}_{category_id}' if for_admin else \
            f'show_subcategory_{subcategory.id}_{brand_id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=subcategory.name_ru, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_brands'))

    return keyboard.adjust(2).as_markup()


async def add_categories_item():
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        cb_data = f'add_item_category_{category.id}'
        keyboard.add(InlineKeyboardButton(text=category.name_ru, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))

    return keyboard.adjust(2).as_markup()


async def add_brands_item(category_id):
    all_brands = await get_brands(category_id)
    keyboard = InlineKeyboardBuilder()

    for brand in all_brands:
        cb_data = f'add_item_brands_{brand.id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=brand.name_ru, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_categories'))

    return keyboard.adjust(2).as_markup()


async def add_subcategories_item(brand_id, category_id, for_admin=False):
    all_subcategories = await get_subcategories(brand_id, category_id)
    keyboard = InlineKeyboardBuilder()

    for subcategory in all_subcategories:
        cb_data = f'add_item_subcategory_{subcategory.id}_{brand_id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=subcategory.name_ru, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_brands'))

    return keyboard.adjust(2).as_markup()
