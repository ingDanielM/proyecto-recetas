import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models import Base, engine
from app.routers import ingredients_router, recipes_router

# Configuración básica de logs para monitorear errores en la consola del servidor
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear de forma automática todas las tablas registradas en la base de datos
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de la Base de Datos verificadas/creadas exitosamente.")
except Exception as e:
    logger.error(f"Error crítico al conectar o crear la Base de Datos: {e}")

app = FastAPI(
    title="Generador de Recetas",
    description="API para generar recetas con IA a partir de tu inventario (Integración OpenRouter)",
    version="1.0.0"
)

# Configuración de CORS (Útil si conectas tu frontend en React más adelante)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MANEJADORES GLOBALES DE EXCEPCIONES ---

@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    """
    Captura cualquier error inesperado del sistema (como fallos de conversión de tipos
    o caídas imprevistas) para evitar que el servidor exponga trazas de código internas.
    """
    logger.error(f"Error no controlado en la ruta {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Ocurrió un error interno inesperado en el servidor. Por favor, intente más tarde."
        }
    )

# --- INCLUSIÓN DE ROUTERS ---
app.include_router(ingredients_router)
app.include_router(recipes_router)

# --- ENDPOINTS CORE ---

@app.get("/health", tags=["Sistema"])
def health_check():
    """
    Endpoint de verificación de estado de la API.
    """
    return {"status": "ok", "message": "API funcionando correctamente"}