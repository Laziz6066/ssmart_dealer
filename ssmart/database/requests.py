from ssmart.database.models import async_session
from ssmart.database.models import User, Category, Item, Brand, Subcategory, DollarExchangeRate
from sqlalchemy import select, update, delete
import logging
from sqlalchemy.ext.asyncio import AsyncSession


async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_user(user_id: int):
    async with async_session() as session:
        result = await session.scalars(select(User.language).where(User.tg_id == user_id))
        return result.first()  # Get the first value


async def get_course():
    async with async_session() as session:
        result = await session.execute(select(DollarExchangeRate.course))
        return result.scalar()


async def get_categories():
    async with async_session() as session:
        return await session.scalars(select(Category))


async def get_brands(category_id):
    async with async_session() as session:
        return await session.scalars(select(Brand).where(Brand.category == category_id))


async def get_subcategories(brand_id, category_id):
    async with async_session() as session:
        return await session.scalars(select(Subcategory).where(
            Subcategory.brand == brand_id, Subcategory.category == category_id))


async def get_items(category_id, brand_id, subcategory_id):
    async with async_session() as session:
        query = select(Item).where(
            Item.category == category_id, Item.brand == brand_id, Item.subcategory == subcategory_id)

        return await session.scalars(query)


async def add_user(user_id: int, user_name: str, language: str, session: AsyncSession):
    user = User(tg_id=user_id, user_name=user_name, language=language)
    session.add(user)
    await session.commit()


async def update_course(course: int, session: AsyncSession):
    result = await session.execute(select(DollarExchangeRate).limit(1))
    existing_course = result.scalars().first()

    if existing_course:
        await session.execute(
            update(DollarExchangeRate)
            .where(DollarExchangeRate.id == existing_course.id)
            .values(course=course)
        )
    else:
        new_course = DollarExchangeRate(course=course)
        session.add(new_course)

    await session.commit()


async def user_exists(user_id: int, session: AsyncSession) -> bool:
    result = await session.execute(select(User).filter_by(tg_id=user_id))
    return result.scalars().first() is not None


async def add_category(name_uz: str, name_ru: str, ):
    async with async_session() as session:
        category = Category(name_uz=name_uz, name_ru=name_ru)
        session.add(category)
        await session.commit()


async def add_brand(name_uz: str, name_ru: str, category: int):
    async with async_session() as session:
        brand = Brand(name_uz=name_uz, name_ru=name_ru, category=category)
        session.add(brand)
        await session.commit()


async def add_subcategory(name_uz: str, name_ru: str, category: int, brand: int):
    async with async_session() as session:
        subcategory = Subcategory(name_uz=name_uz, name_ru=name_ru, category=category, brand=brand)
        session.add(subcategory)
        await session.commit()


async def add_item(
        name_uz: str,
        name_ru: str,
        description_uz: str,
        description_ru: str,
        price: int,
        photo: list,
        category: int,
        brand: int,
        subcategory: int
):
    logging.info(f"Добавление товара: {name_uz}, {name_ru}, {description_uz}, {description_ru}, "
                 f"{price}, {photo}, {category}, {brand}, {subcategory}")

    async with async_session() as session:
        item = Item(
            name_uz=name_uz,
            name_ru=name_ru,
            description_uz=description_uz,
            description_ru=description_ru,
            price=price,
            photo=photo,
            category=category,
            brand=brand,
            subcategory=subcategory
        )
        session.add(item)
        await session.commit()


async def delete_item(item_id: int):
    async with async_session() as session:
        await session.execute(delete(Item).where(Item.id == item_id))
        await session.commit()


async def update_item(item_id: int, name_ru: str, name_uz: str, description_ru: str, description_uz: str, price: int):
    async with async_session() as session:
        await session.execute(
            update(Item)
            .where(Item.id == item_id)
            .values(
                name_ru=name_ru,
                name_uz=name_uz,
                description_ru=description_ru,
                description_uz=description_uz,
                price=price
            )
        )
        await session.commit()


async def get_item_for_update(item_id: int):
    async with async_session() as session:
        result = await session.execute(select(Item).where(Item.id == item_id))
        return result.scalars().first()


async def delete_category_by_name(category_name: str):
    async with async_session() as session:
        await session.execute(delete(Category).where(Category.name_ru == category_name))
        await session.commit()


# В requests.py добавьте:
async def update_user_language(user_id: int, new_language: str, session: AsyncSession):
    await session.execute(
        update(User).where(User.tg_id == user_id).values(language=new_language)
    )
    await session.commit()