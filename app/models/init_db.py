import logging
from app.models.base import engine, Base
# Importar modelos para que estén presentes en la metadata
from app.models.user import User
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.rating import Rating

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas creadas exitosamente.")

if __name__ == "__main__":
    init_db()