from dotenv import load_dotenv
import os
import ssmart.database.requests as rq


load_dotenv()
ADMINS = list(map(int, os.getenv('ADMINS', '').split(','))) if os.getenv('ADMINS') else []

text_main_menu_key = {
    'ru': {
        'catalog': 'Каталог',
        'contacts': 'Контакты',
        'about': 'О нас',
        'admin_panel': 'Админ панель',
    },
    'uz': {
        'catalog': 'Katalog',
        'contacts': 'Kontaktlar',
        'about': 'Biz haqimizda',
    }
}
text_get_contacts = {
    'ru': {
        'service': 'Сервисный центр',
        'manager': 'Менеджер',
        'menu': 'Главное меню',
    },
    'uz': {
        'service': "Xizmat ko'rsatish markazi",
        'manager': 'Menejer',
        'menu': 'Asosiy menyu',
    }
}

text_contacts = {
    'ru': "По техническим вопросам: <b>Сервисный центр</b>\nПо остальным вопросам: <b>Менеджер</b>.",
    'uz': "Texnik masalalar bo'yicha: <b>Xizmat ko'rsatish markazi</b>\nBoshqa masalalar bo'yicha: <b>Menejer</b>."
}

text_main_menu = {
    'ru': "Добро пожаловать в дилерский центр Ssmart.",
    'uz': "Ssmart dillerlik markaziga xush kelibsiz."
}

choice_category = {
    'ru': "Выберите категорию:",
    'uz': "Toifani tanlang:"
}

choice_brand = {
    'ru': "Выберите подкатегорию:",
    'uz': "Pastki toifani tanlang:"
}

choice_subcategory = {
    'ru': "Выберите бренд:",
    'uz': "Brendni tanlang:"
}

installment = {
    'ru': "Выберите срок рассрочки:",
    'uz': "To'lov muddatini tanlang:",
}
