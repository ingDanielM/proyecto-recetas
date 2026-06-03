from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["juan_david"])
    email: EmailStr = Field(..., examples=["juan@correo.com"])

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, examples=["password_segura123"])

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)