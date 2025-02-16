from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import ssmart.database.requests as rq
import ssmart.admin.a_keyboards as admin_kb
from ssmart.admin.state import AddSubcategory
from ssmart.config import ADMINS
import logging

subcategory_router = Router()


@subcategory_router.message(F.text == 'Добавить подкатегорию')
async def start_add_subcategory(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        category_kb = await admin_kb.add_categories(for_admin=True)
        await state.set_state(AddSubcategory.category)
        await message.answer("Выберите категорию для добавления подкатегории:", reply_markup=category_kb)
    else:
        await message.answer("У вас нет доступа !!!")


@subcategory_router.callback_query(F.data.startswith('add_category_'))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[-1])
    await state.update_data(category=category_id)

    logging.info(f"Выбрана категория: {category_id}")

    brand_kb = await admin_kb.add_brands(category_id)
    main_menu = await admin_kb.admin_keyboard(callback.from_user.id)
    if brand_kb.inline_keyboard and len(brand_kb.inline_keyboard) > 0:
        await state.set_state(AddSubcategory.brand)
        await callback.message.edit_text("Выберите бренд для добавления подкатегории:", reply_markup=brand_kb)
    else:
        await callback.message.answer("❌ В этой категории нет брендов. Добавьте бренд перед "
                                         "созданием подкатегории.", reply_markup=main_menu)

    await callback.answer()


@subcategory_router.callback_query(F.data.startswith('add_brands_'))
async def process_brand(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split('_')
    brand_id = int(data_parts[2])
    category_id = int(data_parts[3])

    logging.info(f"Выбран бренд для добавления подкатегории: {brand_id}, категория: {category_id}")

    await state.update_data(brand=brand_id, category=category_id)
    await state.set_state(AddSubcategory.name_ru)

    await callback.message.answer("Введите название подкатегории (на русском)", reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@subcategory_router.message(AddSubcategory.name_ru)
async def process_brand(message: Message, state: FSMContext):
    await state.update_data(name_ru=message.text.strip())
    await state.set_state(AddSubcategory.name_uz)
    await message.answer("Введите название подкатегории (на узбекском):")


@subcategory_router.message(AddSubcategory.name_uz)
async def process_subcategory_name(message: Message, state: FSMContext):
    await state.update_data(name_uz=message.text)
    data = await state.get_data()

    logging.info(f"Данные перед добавлением подкатегории: {data}")

    await rq.add_subcategory(
        name_uz=data['name_uz'],
        name_ru=data['name_ru'],
        brand=data['brand'],
        category=data['category']
    )
    main_menu = await admin_kb.admin_keyboard(message.from_user.id)
    await state.clear()
    await message.answer("Подкатегория успешно добавлена!", reply_markup=main_menu)
