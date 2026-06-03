import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 1. CONFIGURACIÓN CRÍTICA: Importamos la Base declarativa y TODOS los modelos ORM
# para que Alembic los registre en memoria antes de la inspección.
from app.models.base import Base
from app.models.user import User
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.rating import Rating

# Este es el objeto de configuración de Alembic que mapea el archivo alembic.ini
config = context.config

# Configurar logs básicos de Alembic si el archivo de configuración existe
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. CONFIGURACIÓN CRÍTICA: Apuntamos el target_metadata a la estructura de nuestros modelos
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    Ejecuta las migraciones en modo 'offline'.
    Configura el contexto únicamente con la URL de conexión sin levantar el pool real.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """
    Ejecuta las migraciones en modo 'online' (Conexión activa a PostgreSQL).
    """
    # Lee la sección de configuración del archivo alembic.ini
    configuration = config.get_section(config.config_ini_section, {})
    
    # Permite sobrescribir de forma dinámica la URL si tienes una variable de entorno DATABASE_URL
    if os.getenv("DATABASE_URL"):
        configuration["sqlalchemy.url"] = os.getenv("DATABASE_URL")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()