from pydantic import BaseModel, EmailStr
from typing import Optional

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
