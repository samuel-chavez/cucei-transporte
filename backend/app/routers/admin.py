from fastapi import APIRouter, Depends
from app.dependencies import get_current_admin
from app.database import fake_users_db, fake_bicicletas_db, fake_registros_db

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/usuarios")
async def obtener_usuarios(admin_user=Depends(get_current_admin)):
    """Devuelve todos los usuarios (solo admin)"""
    return list(fake_users_db.values())

@router.get("/bicicletas")
async def obtener_bicicletas(admin_user=Depends(get_current_admin)):
    """Devuelve todas las bicicletas (solo admin)"""
    return list(fake_bicicletas_db.values())

@router.get("/registros")
async def obtener_registros(admin_user=Depends(get_current_admin)):
    """Devuelve todos los registros (solo admin)"""
    return list(fake_registros_db.values())