from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models import UserLogin, Token  # <-- Cambia UserOut por Token
from app.database import fake_users_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/auth", tags=["auth"])

router = APIRouter(prefix="/auth", tags=["auth"])

# Funcion para verificar la contraseña plana contra el hash guardado
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ENDPOINT PRINCIPAL DE LOGIN (ahora devuelve un Token)
@router.post("/login", response_model=Token)  # <-- Ahora devuelve un Token, no un User
async def login(user_credentials: UserLogin):
    user_found = None
    for user_key, user_data in fake_users_db.items():
        if user_data["email"] == user_credentials.email:
            user_found = user_data
            break

    if not user_found:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    if not verify_password(user_credentials.password, user_found["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    # CREAMOS EL TOKEN con el email del usuario dentro
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_found["email"]}, expires_delta=access_token_expires
    )

    # Devolvemos el token y su tipo (bearer)
    return {"access_token": access_token, "token_type": "bearer"}

# ENDPOINT PARA EL FORMULARIO DE LA DOCUMENTACIÓN
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Reutilizamos la misma lógica pero para el formato de form-data
    user_found = None
    for user_key, user_data in fake_users_db.items():
        if user_data["email"] == form_data.username:  # OAuth2 manda el usuario como 'username'
            user_found = user_data
            break

    if not user_found or not verify_password(form_data.password, user_found["password"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_found["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}