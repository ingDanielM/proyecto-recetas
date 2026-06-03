import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Intentar cargar el archivo .env
load_dotenv()

# Intentamos leer del .env; si da None, usamos la cadena con el driver moderno explícito
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "postgresql+psycopg://recetas_user:recetas_pass@localhost:5432/chef_ia_db"

# Inicialización del motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verifica la validez de las conexiones antes de usarlas
    pool_size=10,        # Número de conexiones persistentes
    max_overflow=20      # Conexiones adicionales permitidas en picos de tráfico
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase Base declarativa para todos los modelos ORM
class Base(DeclarativeBase):
    pass

# Dependencia para inyectar la sesión en los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()