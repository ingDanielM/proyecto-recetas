# Importamos la configuración de base de datos para exponerla fácilmente
from app.models.base import Base, engine, SessionLocal, get_db

# Importamos los modelos para registrar las relaciones cruzadas en SQLAlchemy
from app.models.user import User
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe

# Exponemos públicamente todo lo que los controladores y servicios necesitarán
__all__ = ["Base", "engine", "SessionLocal", "get_db", "User", "Ingredient", "Recipe"]