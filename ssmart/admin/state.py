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
    name_uz = State()
    name_ru = State()