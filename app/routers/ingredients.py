from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models import get_db, Ingredient, User
from app.schemas import IngredientCreate, IngredientUpdate, IngredientResponse
from app.routers.auth_deps import get_current_user

router = APIRouter(
    prefix="/ingredients",
    tags=["Ingredientes"]
)

@router.post("", response_model=IngredientResponse, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    ingredient_in: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Agrega un nuevo ingrediente al inventario personal del usuario autenticado.
    """
    db_ingredient = Ingredient(
        nombre=ingredient_in.nombre,
        cantidad=ingredient_in.cantidad,
        user_id=current_user.id
    )
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@router.get("", response_model=list[IngredientResponse])
def get_ingredients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene todos los ingredientes que pertenecen exclusivamente al usuario autenticado.
    """
    ingredients = db.query(Ingredient).filter(Ingredient.user_id == current_user.id).all()
    return ingredients


@router.put("/{id}", response_model=IngredientResponse)
def update_ingredient(
    id: int,
    ingredient_in: IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza un ingrediente específico del inventario, validando la propiedad del mismo.
    """
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == id, Ingredient.user_id == current_user.id).first()
    
    if not db_ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ingrediente no existe en tu inventario personal."
        )
    
    # Actualizar solo los campos que vengan en el cuerpo de la petición
    update_data = ingredient_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ingredient, key, value)
        
    db.commit()
    db.refresh(db_ingredient)
    return db_ingredient


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Elimina un ingrediente específico del inventario personal del usuario.
    """
    db_ingredient = db.query(Ingredient).filter(Ingredient.id == id, Ingredient.user_id == current_user.id).first()
    
    if not db_ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El ingrediente no existe en tu inventario personal."
        )
        
    db.delete(db_ingredient)
    db.commit()
    return None