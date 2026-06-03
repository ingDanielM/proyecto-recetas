from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# Esquema base con campos comunes
class IngredientBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Pechuga de pollo"])
    cantidad: str = Field(..., min_length=1, max_length=50, examples=["500g", "2 unidades"])

# Esquema para crear un ingrediente (datos que envía el cliente)
class IngredientCreate(IngredientBase):
    pass

# Esquema para actualizar un ingrediente (campos opcionales)
class IngredientUpdate(BaseModel):
    nombre: str | None = Field(None, min_length=1, max_length=100)
    cantidad: str | None = Field(None, min_length=1, max_length=50)

# Esquema para responder al cliente (datos que salen de la BD)
class IngredientResponse(IngredientBase):
    id: int
    user_id: int
    created_at: datetime

    # Permite a Pydantic leer los datos directamente desde objetos ORM de SQLAlchemy
    model_config = ConfigDict(from_attributes=True)