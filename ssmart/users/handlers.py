from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import ssmart.users.keyboards as kb
import ssmart.database.requests as rq
from ssmart import config
from aiogram.types import InputMediaPhoto

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = await kb.get_language()
    photo = "https://sun9-77.userapi.com/KWoCJ3Smj_J7QyoEci1kEAU2Lyp9YOHvmI6DnA/SXtJSQwIFKw.jpg"

    await message.answer_photo(
        photo=photo,
        caption="Добро пожаловать в дилерский центр Ssmart.\nВыберите язык:",
        reply_markup=keyboard
    )


@router.message(F.text.in_({'🇷🇺 Русский', "🇺🇿 O'zbekcha"}))
async def language_selected(message: Message):
    lang_mapping = {'🇷🇺 Русский': 'ru', "🇺🇿 O'zbekcha": 'uz'}
    selected_lang = lang_mapping.get(message.text)

    async with rq.async_session() as session:
        user_exists = await rq.user_exists(message.from_user.id, session)

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
    brand_id = int(callback.data.split('_')[-2])
    category_id = int(callback.data.split('_')[-1])
    subcategory_id = int(callback.data.split('_')[-3])
    items = await rq.get_items(category_id, brand_id, subcategory_id)
    lang_choice = await rq.get_user(callback.from_user.id)
    if not items:
        text = "Товары не найдены." if lang_choice == 'ru' else "Maxsulotlar topilmadi."
        await callback.message.answer(text)
        return

    price_text = "Цена:" if lang_choice == 'ru' else "Narxi:"
    course = await rq.get_course()

    for item in items:
        keyboard = await kb.item_keyboard(item.id, callback.from_user.id)
        item_name = item.name_ru if lang_choice == 'ru' else item.name_uz
        item_description = item.description_ru if lang_choice == 'ru' else item.description_uz

        # Если фото хранится в виде списка
        if isinstance(item.photo, list):
            if len(item.photo) > 1:
                # Если несколько фотографий – формируем media group
                media = []
                for index, photo_url in enumerate(item.photo):
                    if index == 0:
                        media.append(
                            InputMediaPhoto(
                                media=photo_url,
                                caption=f"{item_name}\n{item_description}\n{price_text} "
                                        f"<b>{item.price * course:,.0f} UZS.</b>".replace(",", " ")
                            )
                        )
                    else:
                        media.append(InputMediaPhoto(media=photo_url))
                await callback.message.answer_media_group(media=media)
            elif len(item.photo) == 1:
                # Если одна фотография – отправляем как обычное фото
                photo_url = item.photo[0]
                await callback.message.answer_photo(
                    photo=photo_url,
                    caption=f"{item_name}\n{item_description}\n{price_text} "
                            f"<b>{item.price * course:,.0f} UZS.</b>".replace(",", " "),
                    reply_markup=keyboard,
                    parse_mode='html'
                )
            else:
                # Если список пустой, можно обработать этот случай (например, отправить сообщение без фото)
                await callback.message.answer(
                    text=f"{item_name}\n{item_description}\n{price_text} "
                         f"<b>{item.price * course:,.0f} UZS.</b>".replace(",", " "),
                    reply_markup=keyboard,
                    parse_mode='html'
                )
        else:
            # Если по каким-то причинам photo не является списком
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

