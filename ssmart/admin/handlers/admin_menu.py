from aiogram import Router, F
from aiogram.types import Message
import ssmart.admin.a_keyboards as kb
from ssmart.config import ADMINS
from ssmart.users.keyboards import get_main_keyboard
import ssmart.database.requests as rq
from ssmart.admin.state import AddCourse
from aiogram.fsm.context import FSMContext


admin_router = Router()


@admin_router.message(F.text == 'Админ панель')
async def admin_panel(message: Message):
    if message.from_user.id in ADMINS:
        keyboard = await kb.admin_keyboard(message.from_user.id)
        await message.answer("Добро пожаловать в Админ панель.", reply_markup=keyboard)
    else:
        await message.answer('У вас нет доступа !!!')


@admin_router.message(F.text == 'На главную')
async def main_menu(message: Message):
    keyboard = await get_main_keyboard(message.from_user.id)
    await message.answer("Вы перешли на главное меню.", reply_markup=keyboard)


@admin_router.message(F.text == 'Посмотреть курс')
async def show_course(message: Message):
    if message.from_user.id in ADMINS:
        course = await rq.get_course()
        await message.answer(f"Курс доллара: {course}")
    else:
        await message.answer('У вас нет доступа !!!')


@admin_router.message(F.text == 'Изменить курс')
async def edit_course(message: Message, state: FSMContext):
    if message.from_user.id in ADMINS:
        await state.set_state(AddCourse.course)
        await message.answer("Введите новый курс доллара:")
    else:
        await message.answer('У вас нет доступа !!!')


@admin_router.message(AddCourse.course)
async def save_course(message: Message, state: FSMContext):
    new_course = int(message.text.strip())
    await state.update_data(course=new_course)

    if len(str(new_course)) > 5:
        await message.answer("Вы ввели неправильный курс.")
        return
    data = await state.get_data()
    async with rq.async_session() as session:
        await rq.update_course(course=data['course'], session=session)
    await state.clear()
    await message.answer(f"Курс успешно обновлён: {new_course}")