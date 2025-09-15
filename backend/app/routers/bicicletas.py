from fastapi import APIRouter, Depends, HTTPException
from app.models import BicicletaCreate, BicicletaOut, UserOut
from app.dependencies import get_current_user
from app.database import fake_bicicletas_db  #Importa la falsa DB para bicis
from uuid import uuid4  #Para generar IDs unicos simples

router = APIRouter(prefix="/bicicletas", tags=["bicicletas"])

@router.post("/", response_model=BicicletaOut)
async def registrar_bicicleta(
    bicicleta: BicicletaCreate,
    current_user: UserOut = Depends(get_current_user)  #<-ENDpoint PROTEGIDO
):
    #Verificar si el serial ya existe
    for bici_id, bici_data in fake_bicicletas_db.items():
        if bici_data["serial"] == bicicleta.serial:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una bicicleta con este número de serie."
            )
    
    #Crear un nuevo ID para la bici
    new_id = str(uuid4())[:8]  #Genera un ID corto y unico
    
    #Crear el diccionario de la bicicleta
    nueva_bicicleta = {
        "id": new_id,
        "propietario_id": current_user.id,
        "marca": bicicleta.marca,
        "modelo": bicicleta.modelo,
        "color": bicicleta.color,
        "serial": bicicleta.serial
    }
    
    #Guardar en la "base de datos"
    fake_bicicletas_db[new_id] = nueva_bicicleta
    
    return nueva_bicicleta
