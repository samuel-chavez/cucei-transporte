from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from typing import List

from app.dependencies import get_current_user
from app.models import RegistroOut, UserOut
from app.database.registros import registros_collection
from app.database.bicis import bicis_collection

router = APIRouter(prefix="/registros", tags=["registros"])


# Convertir documentos de MongoDB a modelo RegistroOut
def registro_to_dict(reg):
    return {
        "id": str(reg["_id"]),
        "bicicleta_id": reg.get("bici_id"),
        "usuario_id": reg["usuario_id"],
        "usuario_nombre": reg.get("usuario_nombre", ""),
        "bicicleta_marca": reg.get("bicicleta_marca", ""),
        "bicicleta_modelo": reg.get("bicicleta_modelo", ""),
        "fecha_entrada": reg.get("fecha_entrada"),
        "fecha_salida": reg.get("fecha_salida"),
        "activo": reg.get("activo", False)
    }


@router.post("/entrada")
def registrar_entrada(
    bici_id: str,
    current_user: UserOut = Depends(get_current_user)
):
    # Verificar bicicleta
    bici = bicis_collection.find_one({"id": bici_id})
    if not bici:
        raise HTTPException(status_code=404, detail="Bicicleta no encontrada")

    # Verificar que no tenga ya un registro activo
    activo = registros_collection.find_one({
        "usuario_id": current_user.id,
        "activo": True
    })
    if activo:
        raise HTTPException(status_code=400, detail="Ya tienes una bicicleta dentro del ciclopuerto. Debes registrar salida primero.")

    # Crear nuevo registro de entrada
    nuevo_registro = {
        "usuario_id": current_user.id,
        "usuario_nombre": current_user.nombre,
        "bici_id": bici_id,
        "bicicleta_marca": bici["marca"],
        "bicicleta_modelo": bici["modelo"],
        "fecha_entrada": datetime.now(timezone.utc),
        "fecha_salida": None,
        "activo": True
    }
    result = registros_collection.insert_one(nuevo_registro)
    return {"message": "Entrada registrada correctamente", "id": str(result.inserted_id)}


@router.post("/salida")
def registrar_salida(
    bici_id: str,
    current_user: UserOut = Depends(get_current_user)
):
    # Buscar registro activo para este usuario
    activo = registros_collection.find_one({
        "usuario_id": current_user.id,
        "activo": True
    })
    if not activo:
        raise HTTPException(status_code=400, detail="No hay un registro activo de entrada. Debes registrar entrada primero.")

    # Registrar salida en ese registro
    registros_collection.update_one(
        {"_id": activo["_id"]},
        {"$set": {"fecha_salida": datetime.now(timezone.utc), "activo": False}}
    )
    return {"message": "Salida registrada correctamente"}


@router.get("/mi-historial", response_model=List[RegistroOut])
def obtener_mi_historial(current_user: UserOut = Depends(get_current_user)):
    registros = list(registros_collection.find(
        {"usuario_id": current_user.id}
    ).sort("fecha_entrada", -1))
    return [registro_to_dict(reg) for reg in registros]