from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from ssmart.database.models import Base  # Импортируйте ваши модели
import asyncio

# Настройка подключения к базе данных
config = context.config
url = config.get_main_option("sqlalchemy.url")

# Создаем асинхронный движок
engine = create_async_engine(url)

# Подключаем метаданные
target_metadata = Base.metadata


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    raise Exception("Offline mode is not supported with async databases.")
else:
    asyncio.run(run_migrations_online())