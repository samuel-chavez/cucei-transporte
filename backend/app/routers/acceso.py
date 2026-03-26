from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from pydantic import BaseModel
from app.database.usuarios import usuarios_collection
from app.database.registros import registros_collection

router = APIRouter(prefix="/acceso", tags=["acceso"])

class QrData(BaseModel):
    nombre: str
    codigo: str
    email: str
    rol: str

@router.post("/scan")
def scan_qr(qr_data: QrData):
    # Buscar usuario por email
    user = usuarios_collection.find_one({"email": qr_data.email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Verificar si tiene un registro activo (sin fecha_salida)
    registro_activo = registros_collection.find_one(
        {"usuario_id": str(user["_id"]), "activo": True}
    )

    now = datetime.now(timezone.utc)

    if registro_activo:
        # Cerrar el registro (salida)
        registros_collection.update_one(
            {"_id": registro_activo["_id"]},
            {"$set": {"fecha_salida": now, "activo": False}}
        )
        mensaje = "Salida registrada correctamente"
    else:
        # Crear nuevo registro de entrada (sin bicicleta asociada, solo acceso)
        nuevo_registro = {
            "usuario_id": str(user["_id"]),
            "usuario_nombre": user["nombre"],
            "fecha_entrada": now,
            "fecha_salida": None,
            "activo": True,
            "bici_id": None,
            "bicicleta_marca": None,
            "bicicleta_modelo": None
        }
        registros_collection.insert_one(nuevo_registro)
        mensaje = "Entrada registrada correctamente"

    return {"mensaje": mensaje}