# app/routers/frontend.py
from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models import get_db, Ingredient, Recipe

router = APIRouter(tags=["Frontend"])
templates = Jinja2Templates(directory="templates")

def get_user_or_none(request: Request, db: Session) -> bool:
    try:
        from app.routers.auth_deps import get_current_user
        user = get_current_user(request, db)
        return user
    except Exception:
        return None

@router.get("/", response_class=HTMLResponse)
def root(request: Request, db: Session = Depends(get_db)):
    user = get_user_or_none(request, db)
    if user:
        return RedirectResponse(url="/inventario", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_or_none(request, db)
    if user:
        return RedirectResponse(url="/inventario", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_or_none(request, db)
    if user:
        return RedirectResponse(url="/inventario", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/inventario", response_class=HTMLResponse)
def inventario_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_or_none(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    ingredients = db.query(Ingredient).filter(Ingredient.user_id == user.id).all()
    return templates.TemplateResponse(
        "inventario.html", 
        {"request": request, "user": user, "ingredients": ingredients, "active_tab": "inventario"}
    )

@router.get("/recipes", response_class=HTMLResponse)
def recipes_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_or_none(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Validar si tiene ingredientes en su inventario
    ingredients = db.query(Ingredient).filter(Ingredient.user_id == user.id).all()
    has_ingredients = len(ingredients) > 0
    
    # CRÍTICO: Se pasa "user": user para que layout.html sepa que está autenticado
    return templates.TemplateResponse(
        "recipes.html", 
        {"request": request, "user": user, "has_ingredients": has_ingredients, "active_tab": "recipes"}
    )

@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request, db: Session = Depends(get_db)):
    user = get_user_or_none(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    recipes = db.query(Recipe).filter(Recipe.user_id == user.id).order_by(Recipe.created_at.desc()).all()
    
    formatted_recipes = []
    for r in recipes:
        import json
        try:
            ing_list = json.loads(r.ingredientes)
        except Exception:
            ing_list = [i.strip() for i in r.ingredientes.split("\n") if i.strip()]
            
        try:
            pasos_list = json.loads(r.pasos)
        except Exception:
            pasos_list = [p.strip() for p in r.pasos.split("\n") if p.strip()]
            
        formatted_recipes.append({
            "id": r.id,
            "nombre_plato": r.nombre_plato,
            "ingredientes": ing_list,
            "pasos": pasos_list,
            "tiempo_estimado": r.tiempo_estimado,
            "nivel_dificultad": r.nivel_dificultad,
            "rating": r.rating,
            "created_at": r.created_at.strftime("%d/%m/%Y %H:%M")
        })
        
    return templates.TemplateResponse(
        "history.html", 
        {"request": request, "user": user, "recipes": formatted_recipes, "active_tab": "history"}
    )

@router.get("/logout")
def logout_and_redirect(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response