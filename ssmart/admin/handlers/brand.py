from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import ssmart.database.requests as rq
import ssmart.users.keyboards as user_kb
import ssmart.admin.a_keyboards as admin_kb
from ssmart.admin.state import AddBrand
from ssmart.config import ADMINS
import logging


brand_router = Router()


@brand_router.message(F.text == 'Добавить бренд')
async def start_add_brand(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        category_kb = await user_kb.show_categories(message.from_user.id, for_admin=True)
        await state.set_state(AddBrand.category)
        await message.answer("Выберите категорию:", reply_markup=category_kb)
    else:
        await message.answer("У вас нет доступа !!!")


@brand_router.callback_query(F.data.startswith('admin_category_'))
async def process_category(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split('_')
    logging.info(f"Разделенные данные: {data_parts}")

    category_id_str = data_parts[-1]

    if not category_id_str.isdigit():
        await callback.message.answer(f"Ошибка: '{category_id_str}' не является числом!")
        await callback.answer()
        return

    category_id = int(category_id_str)
    logging.info(f"Извлеченный ID категории: {category_id}")

    await state.update_data(category=category_id)
    await state.set_state(AddBrand.name_ru)
    await callback.message.answer("Введите название Бренда (на русском):", reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@brand_router.message(AddBrand.name_ru)
async def process_brand(message: Message, state: FSMContext):
    await state.update_data(name_ru=message.text.strip())
    await state.set_state(AddBrand.name_uz)
    await message.answer("Введите название Бренда (на узбекском):")


@brand_router.message(AddBrand.name_uz)
async def process_brand(message: Message, state: FSMContext):
    await state.update_data(name_uz=message.text.strip())
    data = await state.get_data()

    logging.info(f"Данные из FSM перед добавлением: {data}")

    await rq.add_brand(
        name_uz=data['name_uz'],
        name_ru=data['name_ru'],
        category=data['category']
    )
    keyboard = await admin_kb.admin_keyboard(message.from_user.id)
    await state.clear()
    await message.answer("Бренд успешно добавлен!", reply_markup=keyboard)
