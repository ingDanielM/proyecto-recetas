import os
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.models import get_db, User

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey123")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# Usamos OAuth2PasswordBearer para soporte automático en Swagger UI, pero sin lanzar error automático (auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependencia para obtener el usuario actual autenticado.
    Busca primero el token en las cookies de la petición (para el frontend con Jinja2) 
    y alternativamente en el header de Authorization (para APIs/pytest).
    """
    token_str = request.cookies.get("access_token")
    
    if not token_str:
        token_str = token

    if not token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se ha proporcionado una sesión activa (token faltante)."
        )

    # Si viene con formato "Bearer <token>", limpiamos el prefijo
    if token_str.startswith("Bearer "):
        token_str = token_str[7:]

    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de token no válidas (sub faltante)."
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o token inválido."
        )

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El usuario asociado a este token no existe."
        )
    
    return user