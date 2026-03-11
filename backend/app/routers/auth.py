from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.models import UserLogin, Token, UserOut, UserCreate
from app.database.usuarios import usuarios_collection
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from typing import Annotated
import re
from slowapi import Limiter
from slowapi.util import get_remote_address

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# ================= REGISTRO =================

@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate):

    email_pattern = r'^[a-zA-Z0-9._%+-]+@alumnos\.udg\.mx$'
    if not re.match(email_pattern, user_data.email):
        raise HTTPException(
            status_code=400,
            detail="El email debe ser del dominio @alumnos.udg.mx"
        )

    existing_user = usuarios_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario con este email"
        )

    if not re.match(r'^\d{8,15}$', user_data.codigo):
        raise HTTPException(
            status_code=400,
            detail="El código debe tener entre 8 y 15 dígitos numéricos"
        )

    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 6 caracteres"
        )

    hashed_password = get_password_hash(user_data.password)

    nuevo_usuario = {
        "codigo": user_data.codigo,
        "nombre": user_data.nombre,
        "email": user_data.email,
        "password": hashed_password,
        "rol": "estudiante"
    }

    usuarios_collection.insert_one(nuevo_usuario)

    nuevo_usuario.pop("password")

    return nuevo_usuario


# ================= LOGIN =================

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: UserLogin):

    user_found = usuarios_collection.find_one({"email": user_credentials.email})

    if not user_found:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    if not verify_password(user_credentials.password, user_found["password"]):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user_found["email"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ================= LOGIN PARA SWAGGER =================

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):

    user_found = usuarios_collection.find_one({"email": form_data.username})

    if not user_found:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    if not verify_password(form_data.password, user_found["password"]):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user_found["email"]},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}