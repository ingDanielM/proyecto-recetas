from sqlalchemy import text
from app.models.base import engine

def test_db_connection():
    """Verifica si la conexión a la base de datos es exitosa."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"db_status": "connected", "message": "Conexión exitosa a PostgreSQL"}
    except Exception as e:
        return {"db_status": "disconnected", "error": str(e)}

if __name__ == "__main__":
    print(test_db_connection())