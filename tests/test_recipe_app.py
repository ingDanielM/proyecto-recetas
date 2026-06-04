import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.services.llm_service import llm_service
from app.models import Ingredient, Recipe

# ----------------------------------------------------------------------
# 1. PRUEBA: Validación de ingredientes (Inventario vacío)
# ----------------------------------------------------------------------
def test_validation_empty_inventory_raises_400(client, auth_headers):
    """
    Verifica que al intentar generar una receta con un inventario vacío,
    el sistema lo valide y retorne un error 400 Bad Request.
    """
    response = client.post("/recipes/generate", headers=auth_headers)
    assert response.status_code == 400
    assert "inventario está vacío" in response.json()["detail"]


# ----------------------------------------------------------------------
# 2. PRUEBA: Generación del prompt
# ----------------------------------------------------------------------
def test_prompt_generation_includes_ingredients():
    """
    Verifica que la función construir_prompt del LLMService genere un prompt
    que contenga textualmente todos los ingredientes proporcionados por el usuario.
    """
    ingredientes_prueba = ["Pollo (500g)", "Arroz (250g)", "Cebolla (1 unidad)"]
    sys_prompt, user_prompt = llm_service.construir_prompt(ingredientes_prueba)
    
    # Comprobar que los ingredientes se unieron con comas en el prompt
    assert "Pollo (500g)" in user_prompt
    assert "Arroz (250g)" in user_prompt
    assert "Cebolla (1 unidad)" in user_prompt
    assert "Mis ingredientes disponibles son:" in user_prompt
    
    # Comprobar que el prompt del sistema contenga las reglas de llaves del profesor
    assert "nombre_plato" in sys_prompt
    assert "ingredientes" in sys_prompt
    assert "pasos" in sys_prompt
    assert "tiempo_estimado" in sys_prompt
    assert "nivel_dificultad" in sys_prompt


# ----------------------------------------------------------------------
# 3. PRUEBA: Parseo del JSON del LLM
# ----------------------------------------------------------------------
def test_parsear_receta_scenarios():
    """
    Prueba tres escenarios del parseador de recetas:
    - JSON Correcto: Debe retornar el diccionario completo.
    - JSON con llaves faltantes: Debe rellenar con valores por defecto seguros.
    - JSON inválido/malformado: Debe lanzar HTTPException con status 422.
    """
    # Escenario A: JSON Correcto
    json_valido = """
    {
        "nombre_plato": "Pollo al Ajillo",
        "ingredientes": ["Pollo 500g", "Ajo 3 dientes"],
        "pasos": ["Cortar pollo", "Freír con ajo"],
        "tiempo_estimado": "25 minutos",
        "nivel_dificultad": "Fácil"
    }
    """
    parseado = llm_service.parsear_receta(json_valido)
    assert parseado["nombre_plato"] == "Pollo al Ajillo"
    assert len(parseado["ingredientes"]) == 2
    assert parseado["tiempo_estimado"] == "25 minutos"

    # Escenario B: JSON con llaves faltantes (Ej. falta nivel_dificultad y pasos)
    json_incompleto = """
    {
        "nombre_plato": "Arroz con Pollo",
        "ingredientes": ["Arroz 200g"],
        "tiempo_estimado": "35 minutos"
    }
    """
    parseado_inc = llm_service.parsear_receta(json_incompleto)
    assert parseado_inc["nombre_plato"] == "Arroz con Pollo"
    assert parseado_inc["pasos"] == []  # Rellenado por default
    assert parseado_inc["nivel_dificultad"] == ""  # Rellenado por default

    # Escenario C: JSON Malformado
    json_invalido = "{ nombre_plato: Pollo al Ajillo " # No es JSON válido
    with pytest.raises(HTTPException) as exc_info:
        llm_service.parsear_receta(json_invalido)
    assert exc_info.value.status_code == 422
    assert "no devolvió un formato JSON válido" in exc_info.value.detail


# ----------------------------------------------------------------------
# 4. PRUEBA: Endpoint de login
# ----------------------------------------------------------------------
def test_login_endpoint(client, db):
    """
    Registra un usuario e intenta iniciar sesión usando el endpoint POST /auth/login.
    Prueba tanto credenciales válidas como credenciales incorrectas.
    """
    # 1. Registrar usuario
    payload_registro = {
        "username": "usuario_prueba",
        "email": "prueba@gourmet.com",
        "password": "contrasenia_segura"
    }
    resp_reg = client.post("/auth/register", json=payload_registro)
    assert resp_reg.status_code == 201
    
    # 2. Login correcto (Formulario x-www-form-urlencoded)
    payload_login = {
        "username": "usuario_prueba",
        "password": "contrasenia_segura"
    }
    resp_login = client.post("/auth/login", data=payload_login)
    assert resp_login.status_code == 200
    data_login = resp_login.json()
    assert "access_token" in data_login
    assert data_login["user"]["username"] == "usuario_prueba"
    
    # 3. Login incorrecto (Contraseña errónea)
    payload_incorrecto = {
        "username": "usuario_prueba",
        "password": "password_incorrecta"
    }
    resp_bad = client.post("/auth/login", data=payload_incorrecto)
    assert resp_bad.status_code == 401
    assert "incorrectos" in resp_bad.json()["detail"]


# ----------------------------------------------------------------------
# 5. PRUEBA: Endpoint de ingredientes (CRUD)
# ----------------------------------------------------------------------
def test_ingredients_endpoints(client, auth_headers, db, test_user):
    """
    Verifica que el usuario pueda agregar un ingrediente al inventario
    y luego recuperarlo mediante el endpoint GET /ingredients.
    """
    # 1. Agregar ingrediente
    ingrediente_data = {
        "nombre": "Zanahoria",
        "cantidad": "3 unidades"
    }
    response_post = client.post("/ingredients", json=ingrediente_data, headers=auth_headers)
    assert response_post.status_code == 201
    data_post = response_post.json()
    assert data_post["nombre"] == "Zanahoria"
    assert data_post["cantidad"] == "3 unidades"
    assert data_post["id"] is not None

    # 2. Obtener lista de ingredientes del usuario
    response_get = client.get("/ingredients", headers=auth_headers)
    assert response_get.status_code == 200
    lista = response_get.json()
    assert len(lista) == 1
    assert lista[0]["nombre"] == "Zanahoria"
    assert lista[0]["cantidad"] == "3 unidades"


# ----------------------------------------------------------------------
# 6. PRUEBA: Endpoint de generación de recetas (con mock de LLM)
# ----------------------------------------------------------------------
@patch("app.routers.recipes.llm_service.generar_receta", new_callable=AsyncMock)
def test_generate_recipe_endpoint(mock_generar, client, auth_headers, db, test_user):

    """
    Simula la respuesta de OpenRouter (mock) y verifica que el flujo completo
    del endpoint POST /recipes/generate funcione correctamente, registrando la receta en la BD.
    """
    # 1. Insertar ingrediente en la base de datos de prueba para tener inventario
    nuevo_ing = Ingredient(nombre="Papa", cantidad="1 kg", user_id=test_user.id)
    db.add(nuevo_ing)
    db.commit()

    # 2. Configurar la respuesta simulada (mock) de generar_receta del llm_service
    receta_fake = {
        "nombre_plato": "Papas Fritas Gourmet",
        "ingredients": ["Papa 1 kg", "Sal al gusto", "Aceite para freír"],
        "pasos": ["Cortar las papas en bastones", "Freír en aceite caliente", "Escurrir y salar"],
        "tiempo_estimado": "20 minutos",
        "nivel_dificultad": "Fácil"
    }
    mock_generar.return_value = receta_fake

    # 3. Invocar endpoint asíncrono
    response = client.post("/recipes/generate", headers=auth_headers)
    
    # 4. Validar respuestas y registros
    assert response.status_code == 201
    data = response.json()
    assert data["nombre_plato"] == "Papas Fritas Gourmet"
    assert data["tiempo_estimado"] == "20 minutos"
    assert len(data["pasos"]) == 3
    
    # Comprobar que el mock fue llamado con los ingredientes del usuario
    mock_generar.assert_called_once_with(ingredientes_usuario=["Papa (1 kg)"])

    # Comprobar que la receta se guardó físicamente en la BD
    recetas_db = db.query(Recipe).filter(Recipe.user_id == test_user.id).all()
    assert len(recetas_db) == 1
    assert recetas_db[0].nombre_plato == "Papas Fritas Gourmet"
