from logging.config import fileConfig
import importlib
import os
from pathlib import Path

from sqlalchemy import create_engine, pool
from alembic import context

from app.core.config import settings
from app.core.database import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


models_path = Path(os.path.join(os.path.dirname(__file__), "..", "app", "models")).resolve()
for file_path in models_path.rglob("*.py"):
    if file_path.name.startswith("__"):
        continue
    module_name = ".".join(file_path.relative_to(models_path).with_suffix("").parts)
    importlib.import_module(f"app.models.{module_name}")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.SYNC_DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        settings.SYNC_DATABASE_URL,
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()