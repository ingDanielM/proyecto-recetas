from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre_plato: Mapped[str] = mapped_column(String(150), nullable=False)
    ingredientes: Mapped[str] = mapped_column(Text, nullable=False)  # Guardado como JSON string o texto estructurado
    pasos: Mapped[str] = mapped_column(Text, nullable=False)         # Guardado como JSON string o texto estructurado
    tiempo_estimado: Mapped[str] = mapped_column(String(50), nullable=False)
    nivel_dificultad: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Calificación opcional de 1 a 5 estrellas
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones
    owner: Mapped["User"] = relationship("User", back_populates="recipes")

    # Restricción física en la BD para el rango de estrellas
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )