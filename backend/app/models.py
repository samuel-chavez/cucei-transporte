from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

#Este modelo define lo que el usuario DEBE enviarnos para hacer login.
class UserLogin(BaseModel):
    email: EmailStr  #Forcea que sea un email válido
    password: str

#Este modelo define lo que nosotros le DEVOLVEMOS al usuario. SIN PASSWORD NMMS
class UserOut(BaseModel):
    id: Optional[int] = None
    codigo: str
    nombre: str
    email: EmailStr

    # Esta configuración permite crear un UserOut desde un diccionario de Python como la falsa DB
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

#Modelo para los datos que irán dentro del token
class TokenData(BaseModel):
    email: Optional[str] = None

class BicicletaCreate(BaseModel):
    marca: str
    modelo: str
    color: str
    serial: str  #Numero de serie es unico para cada bici

class BicicletaOut(BicicletaCreate):
    id: int
    propietario_id: int  #ID del usuario que la registro

    class Config:
        from_attributes = True

class RegistroBase(BaseModel):
    bicicleta_id: str

class RegistroCreate(RegistroBase):
    pass  # Solo necesita la bicicleta_id, el usuario se obtiene del token

class RegistroOut(RegistroBase):
    id: str
    usuario_id: int
    usuario_nombre: str  # Para que sea fácil ver quién registró
    bicicleta_marca: str
    bicicleta_modelo: str
    fecha_entrada: datetime
    fecha_salida: Optional[datetime] = None
    activo: bool  # True = dentro del ciclopuerto, False = ya salió

    class Config:
        from_attributes = True
