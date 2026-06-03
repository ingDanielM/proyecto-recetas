from datetime import datetime
from typing import List
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    ingredients: Mapped[List["Ingredient"]] = relationship("Ingredient", back_populates="owner", cascade="all, delete-orphan")
    recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="owner", cascade="all, delete-orphan")