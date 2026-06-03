from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class RatingBase(BaseModel):
    stars: int = Field(..., ge=1, le=5, description="Calificación de 1 a 5 estrellas")
    recipe_id: int

class RatingCreate(RatingBase):
    pass

class RatingResponse(RatingBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)