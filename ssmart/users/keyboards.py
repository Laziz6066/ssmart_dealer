from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from ssmart.database.requests import get_categories, get_brands, get_subcategories, get_items
from aiogram.utils.keyboard import InlineKeyboardBuilder
from ssmart.config import ADMINS
import ssmart.database.requests as rq
from ssmart.database.models import Item
from ssmart.config import text_main_menu_key, text_get_contacts
from ssmart.database.models import async_session

load_dotenv()


async def get_language() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text='🇷🇺 Русский'), KeyboardButton(text="🇺🇿 O'zbekcha")]]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    lang_choice = await rq.get_user(user_id)
    print('lang_choice key: ', lang_choice)

    buttons = [
        [KeyboardButton(text=text_main_menu_key[lang_choice]['catalog']),
         KeyboardButton(text=text_main_menu_key[lang_choice]['change_lang'])],
        [KeyboardButton(text=text_main_menu_key[lang_choice]['contacts']),
         KeyboardButton(text=text_main_menu_key[lang_choice]['about'])]]


    if user_id in ADMINS:
        buttons.insert(1, [KeyboardButton(text='Админ панель')])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def get_contacts(user_id: int) -> ReplyKeyboardMarkup:
    lang_choice = await rq.get_user(user_id)
    buttons = [
        [KeyboardButton(text=text_get_contacts[lang_choice]["service"]),
         KeyboardButton(text=text_get_contacts[lang_choice]["manager"])],
        [KeyboardButton(text=text_get_contacts[lang_choice]["menu"])]]

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


async def show_categories(user_id, for_admin=False):
    all_categories = await get_categories()
    keyboard = InlineKeyboardBuilder()
    lang_choice = await rq.get_user(user_id)
    text = "На главную" if lang_choice == 'ru' else "Asosiy menyu"

    for category in all_categories:
        cat = category.name_ru if lang_choice == 'ru' else category.name_uz
        cb_data = f'admin_category_{category.id}' if for_admin else f'show_category_{category.id}'
        keyboard.add(InlineKeyboardButton(text=cat, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text=text, callback_data='to_main_inline'))

    return keyboard.adjust(2).as_markup()


async def show_brands(user_id, category_id, for_admin=False):
    all_brands = await get_brands(category_id)
    keyboard = InlineKeyboardBuilder()
    lang_choice = await rq.get_user(user_id)
    text = "На главную" if lang_choice == 'ru' else "Asosiy menyu"
    for brand in all_brands:
        brand_name = brand.name_ru if lang_choice == 'ru' else brand.name_uz
        cb_data = f'admin_brand_{brand.id}_{category_id}' if for_admin else f'show_brand_{brand.id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=brand_name, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text=text, callback_data='to_main_inline'))

    return keyboard.adjust(2).as_markup()


async def show_subcategories(brand_id, category_id, user_id, for_admin=False):
    all_subcategories = await get_subcategories(brand_id, category_id)
    keyboard = InlineKeyboardBuilder()
    lang_choice = await rq.get_user(user_id)
    text = "На главную" if lang_choice == 'ru' else "Asosiy menyu"
    for subcategory in all_subcategories:
        subcategory_name = subcategory.name_ru if lang_choice == 'ru' else subcategory.name_uz
        cb_data = f'admin_subcategory_{subcategory.id}_{brand_id}_{category_id}' if for_admin else \
            f'show_subcategory_{subcategory.id}_{brand_id}_{category_id}'
        keyboard.add(InlineKeyboardButton(text=subcategory_name, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text=text, callback_data='to_main_inline'))

    return keyboard.adjust(2).as_markup()


async def show_items(category_id, brand_id, subcategory_id, user_id, for_admin=False):
    all_items = await get_items(category_id, brand_id, subcategory_id)
    keyboard = InlineKeyboardBuilder()
    lang_choice = await rq.get_user(user_id)
    text = "На главную" if lang_choice == 'ru' else "Asosiy menyu"
    for item in all_items:
        item_name = item.name_ru if lang_choice == 'ru' else item.name_uz
        cb_data = f'admin_item_{item.id}_{category_id}_{brand_id}_{subcategory_id}' if for_admin else \
            f'show_item_{item.id}_{category_id}_{brand_id}_{subcategory_id}'
        keyboard.add(InlineKeyboardButton(text=item_name, callback_data=cb_data))

    keyboard.add(InlineKeyboardButton(text=text, callback_data='to_main_inline'))

    return keyboard.adjust(1).as_markup()


async def item_keyboard(item_id, user_id):
    lang_choice = await rq.get_user(user_id)
    keyboard = InlineKeyboardBuilder()
    text_1 = "💳 Оплата картой" if lang_choice == 'ru' else "💳 Karta bilan to'lash"
    text_2 = "📆 Оформить в рассрочку" if lang_choice == 'ru' else "📆 Bo'lib to'lash"
    keyboard.add(InlineKeyboardButton(text=text_1, callback_data=f'pay_card_{item_id}'))
    keyboard.add(InlineKeyboardButton(text=text_2, callback_data=f'installment_{item_id}'))

    if user_id in ADMINS:
        keyboard.add(InlineKeyboardButton(text="Удалить товар", callback_data=f"delete_item_{item_id}"))
        keyboard.add(InlineKeyboardButton(text="Изменить товар", callback_data=f"update_item_{item_id}"))

    return keyboard.adjust(1).as_markup()


async def installment(item_id, user_id):
    lang_choice = await rq.get_user(user_id)

    async with async_session() as session:
        item = await session.get(Item, int(item_id))

    course = await rq.get_course()

    price_per_6 = item.price * course / 6
    price_per_12 = item.price * course / 12
    price_per_18 = item.price * course / 18

    text_1 = f"6 месяцев по {price_per_6:,.0f} UZS" if lang_choice == 'ru' else f"6 oyga  {price_per_6:,.0f} UZS"
    text_2 = f"12 месяцев по {price_per_12:,.0f} UZS" if lang_choice == 'ru' else f"12 oyga  {price_per_12:,.0f} UZS"
    text_3 = f"18 месяцев по {price_per_18:,.0f} UZS" if lang_choice == 'ru' else f"18 oyga  {price_per_18:,.0f} UZS"

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text_1, callback_data=f'month_6_{item_id}')],
        [InlineKeyboardButton(text=text_2, callback_data=f'month_12_{item_id}')],
        [InlineKeyboardButton(text=text_3, callback_data=f'month_18_{item_id}')]
    ])
