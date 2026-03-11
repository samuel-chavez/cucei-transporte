from fastapi import APIRouter, Depends
from app.dependencies import get_current_admin
from app.database.usuarios import usuarios_collection
from app.database.bicis import bicis_collection
from app.database.registros import registros_collection

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/usuarios")
async def obtener_usuarios(admin_user=Depends(get_current_admin)):
    """Devuelve todos los usuarios (solo admin)"""
    return list(usuarios_collection.find({}, {"_id": 0}))

@router.get("/bicicletas")
async def obtener_bicicletas(admin_user=Depends(get_current_admin)):
    """Devuelve todas las bicicletas (solo admin)"""
    return list(bicis_collection.find({}, {"_id": 0}))

@router.get("/registros")
async def obtener_registros(admin_user=Depends(get_current_admin)):
    """Devuelve todos los registros (solo admin)"""
    return list(registros_collection.find({}, {"_id": 0}))