# app/routers/recipes.py
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import get_db, Recipe, Ingredient, User
from app.schemas import RecipeResponse, RecipeRate
from app.routers.auth_deps import get_current_user
from app.services import llm_service

# CAMBIO CRÍTICO: Añadimos /api para diferenciar los datos del diseño HTML
router = APIRouter(
    prefix="/api/recipes",
    tags=["Recetas (API)"]
)

def format_recipe_response(recipe: Recipe) -> RecipeResponse:
    """
    Función utilitaria para convertir los campos de texto (JSON string) 
    de la base de datos en listas reales antes de enviarlos al cliente.
    """
    try:
        ingredientes_list = json.loads(recipe.ingredientes)
    except Exception:
        ingredientes_list = [i.strip() for i in recipe.ingredientes.split("\n") if i.strip()]

    try:
        pasos_list = json.loads(recipe.pasos)
    except Exception:
        pasos_list = [p.strip() for p in recipe.pasos.split("\n") if p.strip()]

    return RecipeResponse(
        id=recipe.id,
        nombre_plato=recipe.nombre_plato,
        ingredientes=ingredientes_list,
        pasos=pasos_list,
        tiempo_estimado=recipe.tiempo_estimado,
        nivel_dificultad=recipe.nivel_dificultad,
        rating=recipe.rating,
        user_id=recipe.user_id,
        created_at=recipe.created_at
    )


@router.get("", response_model=list[RecipeResponse])
def get_recipes_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ver el historial completo de recetas generadas por el usuario autenticado.
    """
    recipes = db.query(Recipe).filter(Recipe.user_id == current_user.id).order_by(Recipe.created_at.desc()).all()
    return [format_recipe_response(recipe) for recipe in recipes]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una receta específica del historial del usuario, validando su propiedad.
    """
    db_recipe = db.query(Recipe).filter(Recipe.id == id, Recipe.user_id == current_user.id).first()
    
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La receta no existe en tu historial."
        )
        
    db.delete(db_recipe)
    db.commit()
    return None


@router.post("/{id}/rate", response_model=RecipeResponse)
def rate_recipe(
    id: int,
    rate_in: RecipeRate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Califica una receta existente de 1 a 5 estrellas. 
    Valida la existencia y la pertenencia al usuario actual.
    """
    db_recipe = db.query(Recipe).filter(Recipe.id == id, Recipe.user_id == current_user.id).first()
    
    if not db_recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La receta no existe en tu historial."
        )
    
    db_recipe.rating = rate_in.rating
    
    db.commit()
    db.refresh(db_recipe)
    return format_recipe_response(db_recipe)


@router.post("/generate", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
async def generate_recipe_from_inventory(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Flujo Integración con IA: Solicitud de generación enviada a OpenRouter.
    """
    db_ingredients = db.query(Ingredient).filter(Ingredient.user_id == current_user.id).all()
    
    if not db_ingredients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tu inventario está vacío. Agrega ingredientes mediante tu panel antes de generar una receta."
        )
        
    lista_ingredientes = [f"{ing.nombre} ({ing.cantidad})" for ing in db_ingredients]
    recipe_data = await llm_service.generar_receta(ingredientes_usuario=lista_ingredientes)
    
    db_recipe = Recipe(
        nombre_plato=recipe_data["nombre_plato"],
        ingredientes=json.dumps(recipe_data["ingredientes"], ensure_ascii=False),
        pasos=json.dumps(recipe_data["pasos"], ensure_ascii=False),
        tiempo_estimado=recipe_data["tiempo_estimado"],
        nivel_dificultad=recipe_data["nivel_dificultad"],
        user_id=current_user.id,
        rating=None
    )
    
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    
    return format_recipe_response(db_recipe)