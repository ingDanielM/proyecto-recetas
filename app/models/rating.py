from datetime import datetime
from sqlalchemy import Integer, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.recipe import Recipe
from app.models.user import User

class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    stars: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relaciones cruzadas
    user: Mapped["User"] = relationship("User", back_populates="ratings")
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ratings")

    # Restricción Check estricta a nivel de base de datos
    __table_args__ = (
        CheckConstraint("stars >= 1 AND stars <= 5", name="check_stars_range"),
    )