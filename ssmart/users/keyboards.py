from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os
from ssmart.database.requests import get_categories, get_brands, get_subcategories, get_items
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ssmart.config import ADMINS

load_dotenv()


async def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='Каталог')],
        [KeyboardButton(text='Контакты'), KeyboardButton(text='О нас')]]

    if user_id in ADMINS:
        buttons.insert(1, [KeyboardButton(text='Админ панель')])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_contacts() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='Сервисный центр'), KeyboardButton(text='Менеджер')],
        [KeyboardButton(text='Главное меню')]]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def show_categories(for_admin=False):
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()

    for category in all_categories:
        cb_data = f'admin_category_{category.id}' if for_admin else f'show_category_{category.id}'
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='На главную', callback_data='to_main'))

    return keyboard.adjust(2).as_markup()


async def show_brands(category_id, for_admin=False):
    all_brands = await get_brands(category_id)
    keyboard = InlineKeyboardBuilder()

    for brand in all_brands:
        cb_data = f'admin_brand_{brand.id}_{category_id}' if for_admin else f'show_brand_{brand.id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=brand.name, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_categories'))

    return keyboard.adjust(2).as_markup()


async def show_subcategories(brand_id, category_id, for_admin=False):
    all_subcategories = await get_subcategories(brand_id, category_id)
    keyboard = InlineKeyboardBuilder()

    for subcategory in all_subcategories:
        cb_data = f'admin_subcategory_{subcategory.id}_{brand_id}_{category_id}' if for_admin else \
            f'show_subcategory_{subcategory.id}_{brand_id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=subcategory.name, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_brands'))

    return keyboard.adjust(2).as_markup()


async def show_items(category_id, brand_id, subcategory_id, for_admin=False):
    all_items = await get_items(category_id, brand_id, subcategory_id)
    keyboard = InlineKeyboardBuilder()

    for item in all_items:
        cb_data = f'admin_item_{item.id}_{category_id}_{brand_id}_{subcategory_id}' if for_admin else \
            f'show_item_{item.id}_{category_id}_{brand_id}_{subcategory_id}'
        keyboard.add(InlineKeyboardButton(text=item.name, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text='🔙 Назад', callback_data='back_to_subcategories'))

    return keyboard.adjust(1).as_markup()


def item_keyboard(item_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплата картой", callback_data=f'pay_card_{item_id}')],
        [InlineKeyboardButton(text="📆 Оформить в рассрочку", callback_data=f'installment_{item_id}')]
    ])
