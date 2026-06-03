from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# Campos mínimos exigidos por el profesor para la receta generada por el LLM
class RecipeBase(BaseModel):
    nombre_plato: str = Field(..., min_length=1, max_length=150)
    ingredientes: list[str] = Field(..., min_length=1)
    pasos: list[str] = Field(..., min_length=1)
    tiempo_estimado: str = Field(..., max_length=50)
    nivel_dificultad: str = Field(..., max_length=50)

# Esquema para la calificación de la receta (1 a 5 estrellas)
class RecipeRate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Calificación de la receta de 1 a 5 estrellas")

# Esquema para responder al cliente (historial de recetas)
class RecipeResponse(BaseModel):
    id: int
    nombre_plato: str
    ingredientes: list[str]  # Se parseará automáticamente desde el formato de la BD
    pasos: list[str]         # Se parseará automáticamente desde el formato de la BD
    tiempo_estimado: str
    nivel_dificultad: str
    rating: int | None
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)