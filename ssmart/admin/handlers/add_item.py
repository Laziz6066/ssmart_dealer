from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
import ssmart.database.requests as rq
import ssmart.admin.a_keyboards as admin_kb
from ssmart.admin.state import AddItem
from ssmart.config import ADMINS
import logging


add_item_router = Router()


@add_item_router.message(F.text == 'Добавить товар')
async def start_add_item(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        category_kb = await admin_kb.add_categories_item()
        await state.set_state(AddItem.category)
        await message.answer("Выберите категорию для добавления товара:", reply_markup=category_kb)
    else:
        await message.answer("У вас нет доступа !!!")


@add_item_router.callback_query(F.data.startswith('add_item_category_'))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split('_')[-1])
    await state.update_data(category=category_id)

    logging.info(f"Выбрана категория: {category_id}")

    brand_kb = await admin_kb.add_brands_item(category_id)
    if brand_kb.inline_keyboard and len(brand_kb.inline_keyboard) > 0:
        await state.set_state(AddItem.brand)
        await callback.message.edit_text("Выберите бренд для добавления товара:", reply_markup=brand_kb)
    else:
        await callback.message.answer("❌ В этой категории нет брендов. Добавьте бренд перед созданием товара.")

    await callback.answer()


@add_item_router.callback_query(F.data.startswith('add_item_brands'))
async def process_brand(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    data_parts = callback.data.split('_')
    print(data_parts)
    brand_id = int(data_parts[3])
    category_id = int(data_parts[4])

    logging.info(f"Выбран бренд: {brand_id}, категория: {category_id}")

    await state.update_data(brand=brand_id)

    subcategory_kb = await admin_kb.add_subcategories_item(brand_id, category_id)
    if subcategory_kb.inline_keyboard and len(subcategory_kb.inline_keyboard) > 0:
        await state.set_state(AddItem.subcategory)
        await callback.message.edit_text("Выберите подкатегорию для добавления товара:",
                                         reply_markup=subcategory_kb)
    else:
        await callback.message.answer("❌ В этом бренде нет подкатегорий. Добавьте подкатегорию "
                                      "перед созданием товара.")

    await callback.answer()


@add_item_router.callback_query(F.data.startswith('add_item_subcategory_'))
async def process_subcategory(callback: CallbackQuery, state: FSMContext):
    data_parts = callback.data.split('_')
    subcategory_id = int(data_parts[3])
    brand_id = int(data_parts[4])
    category_id = int(data_parts[5])

    logging.info(f"Выбрана подкатегория: {subcategory_id}, бренд: {brand_id}, категория: {category_id}")

    await state.update_data(subcategory=subcategory_id)
    await state.set_state(AddItem.name_ru)

    await callback.message.answer("Введите название товара (на русском):", reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@add_item_router.message(AddItem.name_ru)
async def process_item_name_ru(message: Message, state: FSMContext):
    await state.update_data(name_ru=message.text)
    await state.set_state(AddItem.name_uz)
    await message.answer("Введите название товара (на узбекском):")


@add_item_router.message(AddItem.name_uz)
async def process_item_name_uz(message: Message, state: FSMContext):
    await state.update_data(name_uz=message.text)
    await state.set_state(AddItem.description_ru)
    await message.answer("Введите описание товара (на русском):")


@add_item_router.message(AddItem.description_ru)
async def process_item_description_ru(message: Message, state: FSMContext):
    await state.update_data(description_ru=message.text)
    await state.set_state(AddItem.description_uz)
    await message.answer("Введите описание товара (на узбекском):")


@add_item_router.message(AddItem.description_uz)
async def process_item_description_uz(message: Message, state: FSMContext):
    await state.update_data(description_uz=message.text)
    await state.set_state(AddItem.price)
    await message.answer("Введите цену товара (только число):")


@add_item_router.message(AddItem.price)
async def process_item_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Введите корректную цену (только число).")
        return

    await state.update_data(price=int(message.text))
    await state.set_state(AddItem.photo)
    await message.answer("Отправьте до 3 фотографий товара. После отправки всех фотографий нажмите /done.")


@add_item_router.message(AddItem.photo, F.photo)
async def process_item_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photo = data.get('photo', [])  # Получаем текущий список фотографий

    if len(photo) >= 3:
        await message.answer("❌ Вы уже отправили максимальное количество фотографий (3).")
        return

    photo_id = message.photo[-1].file_id
    photo.append(photo_id)  # Добавляем новую фотографию в список
    await state.update_data(photo=photo)

    if len(photo) < 3:
        await message.answer(f"Фотография добавлена. Отправьте еще {3 - len(photo)} фотографий или нажмите /done.")
    else:
        await message.answer("Вы отправили максимальное количество фотографий. Нажмите /done для завершения.")


@add_item_router.message(AddItem.photo, F.text == '/done')
async def process_item_photo_done(message: Message, state: FSMContext):
    data = await state.get_data()
    photo = data.get('photo', [])

    if not photo:
        await message.answer("❌ Вы не отправили ни одной фотографии.")
        return

    logging.info(f"Добавляем товар: {data}")

    await rq.add_item(
        name_ru=data['name_ru'],
        name_uz=data['name_uz'],
        description_ru=data['description_ru'],
        description_uz=data['description_uz'],
        price=data['price'],
        photo=photo,
        category=data['category'],
        brand=data['brand'],
        subcategory=data['subcategory']
    )

    main_menu = await admin_kb.admin_keyboard(message.from_user.id)
    await state.clear()
    await message.answer("✅ Товар успешно добавлен!", reply_markup=main_menu)

