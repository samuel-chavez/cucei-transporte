from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from pydantic import BaseModel
from app.database.usuarios import usuarios_collection
from app.database.registros import registros_collection
from app.dependencies import get_current_user
from app.models import UserOut

router = APIRouter(prefix="/acceso", tags=["acceso"])

class QrData(BaseModel):
    nombre: str
    codigo: str
    email: str
    rol: str

@router.post("/scan")
def scan_qr(
    qr_data: QrData,
    current_user: UserOut = Depends(get_current_user)   # <-- Usuario que escanea (vigilante)
):
    # 1. Verificar que el vigilante tenga rol permitido
    if current_user.rol not in ["admin", "cuidador"]:
        raise HTTPException(status_code=403, detail="No tienes permisos para escanear")

    # 2. Buscar al alumno por email (el que viene en el QR)
    alumno = usuarios_collection.find_one({"email": qr_data.email})
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    # 3. Verificar si el alumno tiene un registro activo (sin salida)
    registro_activo = registros_collection.find_one(
        {"usuario_id": str(alumno["_id"]), "activo": True}
    )

    now = datetime.now(timezone.utc)

    if registro_activo:
        # Salida: cerrar el registro
        registros_collection.update_one(
            {"_id": registro_activo["_id"]},
            {"$set": {"fecha_salida": now, "activo": False}}
        )
        mensaje = f"Salida registrada para {alumno['nombre']}"
    else:
        # Entrada: crear nuevo registro
        nuevo_registro = {
            "usuario_id": str(alumno["_id"]),
            "usuario_nombre": alumno["nombre"],
            "fecha_entrada": now,
            "fecha_salida": None,
            "activo": True,
            "bici_id": None,
            "bicicleta_marca": None,
            "bicicleta_modelo": None
        }
        registros_collection.insert_one(nuevo_registro)
        mensaje = f"Entrada registrada para {alumno['nombre']}"

    return {"mensaje": mensaje}