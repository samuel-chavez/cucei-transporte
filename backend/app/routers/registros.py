from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.dependencies import get_current_user
from app.models import RegistroOut, UserOut
from app.database.registros import registros_collection
from app.database.bicis import bicis_collection

router = APIRouter(prefix="/registros", tags=["registros"])


@router.post("/entrada")
async def registrar_entrada(
    bici_id: str,
    current_user: UserOut = Depends(get_current_user)
):

    bici = bicis_collection.find_one({"id": bici_id})

    if not bici:
        raise HTTPException(
            status_code=404,
            detail="Bicicleta no encontrada"
        )

    registro = {
        "bici_id": bici_id,
        "usuario_id": current_user.id,
        "tipo": "entrada",
        "fecha": datetime.utcnow()
    }

    registros_collection.insert_one(registro)

    return {"message": "Entrada registrada correctamente"}


@router.post("/salida")
async def registrar_salida(
    bici_id: str,
    current_user: UserOut = Depends(get_current_user)
):

    bici = bicis_collection.find_one({"id": bici_id})

    if not bici:
        raise HTTPException(
            status_code=404,
            detail="Bicicleta no encontrada"
        )

    registro = {
        "bici_id": bici_id,
        "usuario_id": current_user.id,
        "tipo": "salida",
        "fecha": datetime.utcnow()
    }

    registros_collection.insert_one(registro)

    return {"message": "Salida registrada correctamente"}


@router.get("/mis-registros", response_model=list[RegistroOut])
async def ver_registros(
    current_user: UserOut = Depends(get_current_user)
):

    registros = list(
        registros_collection.find(
            {"usuario_id": current_user.id},
            {"_id": 0}
        )
    )

    return registros