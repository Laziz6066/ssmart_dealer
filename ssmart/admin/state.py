from aiogram.fsm.state import StatesGroup, State


class AddCategory(StatesGroup):
    name_uz = State()
    name_ru = State()


class AddBrand(StatesGroup):
    name_uz = State()
    name_ru = State()
    category = State()


class AddSubcategory(StatesGroup):
    name_uz = State()
    name_ru = State()
    category = State()
    brand = State()


class AddItem(StatesGroup):
    name_uz = State()
    name_ru = State()
    description_uz = State()
    description_ru = State()
    price = State()
    photo = State()
    category = State()
    brand = State()
    subcategory = State()


class AddCourse(StatesGroup):
    course = State()


class DeleteCategory(StatesGroup):
    name_uz = State()
    name_ru = State()


class DeleteBrand(StatesGroup):
    name_uz = State()
    name_ru = State()


class DeleteSubcategory(StatesGroup):
    name_uz = State()
    name_ru = State()


class DeleteItem(StatesGroup):
    confirm = State()


class UpdateItem(StatesGroup):
    name_ru = State()
    name_uz = State()
    description_ru = State()
    description_uz = State()
    price = State()
