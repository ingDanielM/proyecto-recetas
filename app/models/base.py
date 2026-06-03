import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar cargar el archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Validación crítica: si no hay URL, detenemos la app
if not DATABASE_URL:
    logger.error("La variable DATABASE_URL no está definida en el entorno.")
    raise ValueError("DATABASE_URL must be set in the .env file")

# Inicialización del motor de SQLAlchemy
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
    logger.info("Motor de base de datos inicializado exitosamente.")
except Exception as e:
    logger.error(f"Error al inicializar el motor de base de datos: {e}")
    raise

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase Base declarativa
class Base(DeclarativeBase):
    pass

# Dependencia para inyectar la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()