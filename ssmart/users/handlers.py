import asyncio
import logging
from random import randint
from uuid import uuid4
import os
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import ssmart.users.keyboards as kb
import ssmart.database.requests as rq
from ssmart import config
from aiogram.types import InputMediaPhoto
from ssmart.utils.atmos_api import create_invoice
from ssmart.utils.payments import monitor_payment

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = await kb.get_language()
    lang_choice = await rq.get_user(message.from_user.id)
    if lang_choice:
        keyboard = await kb.get_main_keyboard(message.from_user.id)
        await message.answer(text=config.text_main_menu[lang_choice], reply_markup=keyboard)
    else:
        await message.answer_photo(
            photo=config.main_photo,
            caption="Добро пожаловать в дилерский центр Ssmart.\nВыберите язык:",
            reply_markup=keyboard
        )


@router.message(F.text.in_({'Сменить язык', "Tilni o'zgartirish"}))
async def change_language(message: Message):
    keyboard = await kb.get_language()
    lang_choice = await rq.get_user(message.from_user.id)
    text = "Выберите язык:" if lang_choice == 'ru' else "Tilni tanlang:"
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_({'🇷🇺 Русский', "🇺🇿 O'zbekcha"}))
async def language_selected(message: Message):
    lang_mapping = {'🇷🇺 Русский': 'ru', "🇺🇿 O'zbekcha": 'uz'}
    selected_lang = lang_mapping.get(message.text)

    async with rq.async_session() as session:
        user_exists = await rq.user_exists(message.from_user.id, session)
        if await rq.user_exists(message.from_user.id, session):
            await rq.update_user_language(message.from_user.id, selected_lang, session)
        else:
            await rq.add_user(message.from_user.id, message.from_user.first_name, selected_lang, session)
        if not user_exists:
            await rq.add_user(message.from_user.id, message.from_user.first_name, selected_lang, session)
    print("selected_lang: ", selected_lang)

    keyboard = await kb.get_main_keyboard(message.from_user.id)
    lang_choice = await rq.get_user(message.from_user.id)

    print("lang_choice: ", lang_choice)
    text = "Выбрано: 🇷🇺 Русский" if selected_lang == 'ru' else "Tanlandi: 🇺🇿 O'zbekcha"
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_({'Контакты', 'Kontaktlar'}))
async def contacts(message: Message):
    keyboard = await kb.get_contacts(message.from_user.id)
    lang_choice = await rq.get_user(message.from_user.id)
    text = config.text_contacts[lang_choice]
    await message.reply(text=text, reply_markup=keyboard, parse_mode="html")


@router.message(F.text.in_({"Xizmat ko'rsatish markazi", 'Сервисный центр'}))
async def service_contact(message: Message):
    await message.reply("+998901234567")


@router.message(F.text.in_({'Менеджер', 'Menejer'}))
async def manager_contact(message: Message):
    await message.reply("+998999999999")


@router.message(F.text.in_({'Главное меню', 'Asosiy menyu'}))
async def main_menu(message: Message):
    keyboard = await kb.get_main_keyboard(message.from_user.id)
    lang_choice = await rq.get_user(message.from_user.id)
    await message.answer(text=config.text_main_menu[lang_choice], reply_markup=keyboard)


@router.message(F.text.in_({'О нас', 'Biz haqimizda'}))
async def about(message: Message):
    lang_choice = await rq.get_user(message.from_user.id)
    await message.answer("Можно что-то написать или фото отправить (сертификат/гувохнома)")


@router.message(F.text.in_({'Каталог', 'Katalog'}))
async def view_catalog(message: Message):
    lang_choice = await rq.get_user(message.from_user.id)
    await message.answer(config.choice_category[lang_choice],
                         reply_markup=await kb.show_categories(message.from_user.id))


@router.callback_query(F.data.startswith('show_category_'))
async def show_brands(callback: CallbackQuery):
    category_id = int(callback.data.split('_')[-1])
    keyboard = await kb.show_brands(callback.from_user.id, category_id)
    lang_choice = await rq.get_user(callback.from_user.id)
    await callback.message.edit_text(config.choice_brand[lang_choice], reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('show_brand_'))
async def show_subcategories(callback: CallbackQuery):
    brand_id = int(callback.data.split('_')[-2])
    category_id = int(callback.data.split('_')[-1])
    keyboard = await kb.show_subcategories(brand_id, category_id, callback.from_user.id)
    lang_choice = await rq.get_user(callback.from_user.id)
    await callback.message.edit_text(config.choice_subcategory[lang_choice], reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith('show_subcategory_'))
async def show_items(callback: CallbackQuery):
    data_parts = callback.data.split('_')
    subcategory_id = int(data_parts[-3])
    brand_id = int(data_parts[-2])
    category_id = int(data_parts[-1])

    items = await rq.get_items(category_id, brand_id, subcategory_id)
    lang_choice = await rq.get_user(callback.from_user.id)

    if not items:
        text = "Товары не найдены." if lang_choice == 'ru' else "Maxsulotlar topilmadi."
        await callback.message.answer(text)
        await callback.answer()
        return

    price_text = "Цена:" if lang_choice == 'ru' else "Narxi:"
    course = await rq.get_course()

    for item in items:
        keyboard = await kb.item_keyboard(item.id, callback.from_user.id)
        item_name = item.name_ru if lang_choice == 'ru' else item.name_uz
        item_description = item.description_ru if lang_choice == 'ru' else item.description_uz

        if isinstance(item.photo, list):
            if len(item.photo) > 1:
                media = []
                for index, photo_url in enumerate(item.photo):
                    if index == 0:
                        media.append(
                            InputMediaPhoto(
                                media=photo_url,
                                caption=f"{item_name}\n{item_description}\n{price_text} "
                                        f"<b>{item.price * course:,.0f} UZS.</b>".replace(",", " "),
                                parse_mode='html'
                            )
                        )
                    else:
                        media.append(InputMediaPhoto(media=photo_url))
                await callback.message.answer_media_group(media=media)
                # Отправляем отдельное сообщение с клавиатурой под товаром
                await callback.message.answer("Выберите действие:", reply_markup=keyboard)
            elif len(item.photo) == 1:
                photo_url = item.photo[0]
                await callback.message.answer_photo(
                    photo=photo_url,
                    caption=f"{item_name}\n{item_description}\n{price_text} "
                            f"<b>{item.price * course:,.0f} UZS.</b>".replace(",", " "),
                    reply_markup=keyboard,
                    parse_mode='html'
                )
            else:
                await callback.message.answer(
                    text=f"{item_name}\n{item_description}\n{price_text} "
                         f"<b>{item.price * course:,.0f} UZS.</b>".replace(",", " "),
                    reply_markup=keyboard,
                    parse_mode='html'
                )
        else:
            await callback.message.answer_photo(
                photo=item.photo,
                caption=f"{item_name}\n{item_description}\n{price_text} "
                        f"<b>{item.price * course:,.0f} UZS.</b>".replace(",", " "),
                reply_markup=keyboard,
                parse_mode='html'
            )
    await callback.answer()


@router.callback_query(F.data.startswith('to_main_inline'))
async def catalog_main(callback: CallbackQuery):
    lang_choice = await rq.get_user(callback.from_user.id)
    await callback.message.edit_text(config.choice_category[lang_choice],
                                     reply_markup=await kb.show_categories(callback.from_user.id))
    await callback.answer()


@router.callback_query(F.data.startswith('installment_'))
async def show_installment(callback: CallbackQuery):
    item_id = callback.data.split('_')[-1]
    keyboard = await kb.installment(item_id, callback.from_user.id)
    lang_choice = await rq.get_user(callback.from_user.id)

    if callback.message.text or callback.message.caption:
        await callback.message.edit_reply_markup(reply_markup=keyboard)
    else:
        await callback.message.answer(config.installment[lang_choice], reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data.startswith("pay_card_"))
async def process_pay_card(callback: CallbackQuery):
    """
    Обработка кнопки \"Оплата картой\": создание инвойса, отправка ссылки пользователю.
    Работает с endpoint checkout-ofd и ссылкой через checkout.pays.uz
    """
    await callback.answer()

    try:
        item_id = int(callback.data.split("_")[2])
    except (IndexError, ValueError):
        await callback.message.answer("❌ Некорректные данные для оплаты.")
        return

    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    lang = await rq.get_user(user_id)

    item = await rq.get_item(item_id)
    course = await rq.get_course()
    if not item:
        await callback.message.answer("❌ Товар не найден.")
        return

    item_name = item.name_ru if lang == 'ru' else item.name_uz
    amount = int(item.price * course) * 100
    account = f"{user_id}{item_id}{uuid4().hex[:6]}"

    invoice_data = await create_invoice(amount, item_name, item_id, account)
    store_tx = invoice_data.get("store_transaction")
    if store_tx:
        import pprint
        logging.info("📦 store_transaction:")
        logging.info(pprint.pformat(store_tx))
    else:
        logging.warning("⚠️ store_transaction отсутствует в ответе ATMOS.")
    if not isinstance(invoice_data, dict):
        await callback.message.answer("⚠️ Не удалось создать счёт. Попробуйте позже.")
        return

    result = invoice_data.get("result")
    if result and result.get("code") == "OK":
        transaction_id = invoice_data.get("transaction_id")
        if transaction_id:
            store_id = int(os.getenv("ATMOS_STORE_ID"))
            transaction_id = invoice_data.get("transaction_id")
            redirect_url = "https://t.me/testing_expenses_bot"

            pay_url = (
                f"https://checkout.pays.uz/invoice/get?"
                f"storeId={store_id}&transactionId={transaction_id}&redirectLink={redirect_url}"
            )
            text = (f"✅ Счёт на оплату <b>{item_name}</b> на сумму <b>{amount/100:.0f} UZS</b> сформирован.\n"
                    f"Нажмите кнопку ниже для перехода к оплате:")
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="💳 Оплатить сейчас", url=pay_url)]]
            )
            await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")

            asyncio.create_task(
                monitor_payment(
                    payment_id=transaction_id,
                    user_id=user_id,
                    chat_id=chat_id,
                    item_id=item_id,
                    amount=amount,
                    account=account,
                    bot=callback.bot
                )
            )
        else:
            await callback.message.answer("⚠️ Счёт создан, но идентификатор транзакции не получен.")
    else:
        desc = result.get("description") if result else "Неизвестная ошибка."
        await callback.message.answer(f"⚠️ Не удалось создать счёт: {desc}")