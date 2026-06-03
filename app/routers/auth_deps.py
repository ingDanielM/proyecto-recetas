from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import get_db, User

# Dependencia para obtener el usuario actual en los endpoints.
# Por ahora, busca el primer usuario de la base de datos o crea uno de prueba si está vacía.
def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).first()
    if not user:
        # Creamos un usuario por defecto para que puedas probar el inventario de inmediato
        user = User(
            username="juan_perez",
            email="juan@correo.com",
            hashed_password="hashed_password_segura"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user