from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
import ssmart.users.keyboards as kb
import ssmart.database.requests as rq
from ssmart import config

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
    price = "Цена:" if lang_choice == 'ru' else "Narxi:"
    for item in items:
        keyboard = await kb.item_keyboard(item.id, callback.from_user.id)
        item_name = item.name_ru if lang_choice == 'ru' else item.name_uz
        item_description = item.description_ru if lang_choice == 'ru' else item.description_uz
        await callback.message.answer_photo(
            photo=item.photo,
            caption=f"{item_name}\n{item_description}\n{price} {item.price:,.0f} UZS.".replace(",", " "),
            reply_markup=keyboard
        )

    await callback.answer()


@router.callback_query(F.data.startswith('to_main_inline'))
async def catalog_main(callback: CallbackQuery):
    lang_choice = await rq.get_user(callback.from_user.id)
    await callback.message.edit_text(config.choice_category[lang_choice],
                                     reply_markup=await kb.show_categories(callback.from_user.id))
    await callback.answer()
