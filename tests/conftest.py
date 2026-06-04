import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.base import Base, get_db
from app.models.user import User
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.rating import Rating
from app.routers.auth import get_password_hash

# Usar SQLite en memoria para pruebas rápidas y aisladas
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db", scope="function")
def db_fixture():
    """Crea una base de datos limpia en memoria vinculando la sesión a una conexión abierta."""
    connection = engine.connect()
    # Crear las tablas en la conexión activa
    Base.metadata.create_all(bind=connection)
    
    # Crear una sesión vinculada a la misma conexión activa
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=connection)
        connection.close()

@pytest.fixture(name="client", scope="function")
def client_fixture(db):
    """Retorna un TestClient con la dependencia de base de datos sobreescrita."""
    def override_get_db():
        try:
            yield db
        finally:
            pass  # La sesión la gestiona y cierra el fixture db_fixture
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user", scope="function")
def test_user_fixture(db):
    """Crea y retorna un usuario de prueba en la base de datos."""
    user = User(
        username="chef_tester",
        email="tester@gourmet.com",
        hashed_password=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(name="auth_headers", scope="function")
def auth_headers_fixture(test_user):
    """Retorna las cabeceras de autorización simulando un login exitoso."""
    from app.routers.auth import create_access_token
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}
