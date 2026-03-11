from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models import UserLogin, Token, UserOut, UserCreate
from app.database import fake_users_db, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Annotated
import re
from uuid import uuid4
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configuración de passlib SIN límite de bytes problemático
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configurar limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["auth"])

# Función para verificar contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para hashear contraseña (para registro)
def get_password_hash(password):
    return pwd_context.hash(password)

# Función para crear token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ============ REGISTRO DE USUARIOS (SIGNUP) ============

@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate):
    """
    Registra un nuevo usuario en el sistema.
    """
    # 1. Validar formato de email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@alumnos\.udg\.mx$'
    if not re.match(email_pattern, user_data.email):
        raise HTTPException(
            status_code=400,
            detail="El email debe ser del dominio @alumnos.udg.mx"
        )
    
    # 2. Validar que el email no exista
    for user_key, existing_user in fake_users_db.items():
        if existing_user["email"] == user_data.email:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un usuario con este email"
            )
    
    # 3. Validar que el código no exista
    for user_key, existing_user in fake_users_db.items():
        if existing_user["codigo"] == user_data.codigo:
            raise HTTPException(
                status_code=400,
                detail="Ya existe un usuario con este código"
            )
    
    # 4. Validar código (8-15 dígitos)
    if not re.match(r'^\d{8,15}$', user_data.codigo):
        raise HTTPException(
            status_code=400,
            detail="El código debe tener entre 8 y 15 dígitos numéricos"
        )
    
    # 5. Validar contraseña
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="La contraseña debe tener al menos 6 caracteres"
        )
    
    # 6. Crear nuevo usuario
    new_id = len(fake_users_db) + 1
    hashed_password = get_password_hash(user_data.password)
    
    nuevo_usuario = {
        "id": new_id,
        "codigo": user_data.codigo,
        "nombre": user_data.nombre,
        "email": user_data.email,
        "password": hashed_password,
        "rol": "estudiante"  # Por defecto, todos son estudiantes
    }
    
    # Guardar en fake_db usando el código como key
    fake_users_db[user_data.codigo] = nuevo_usuario
    
    # Devolver usuario sin contraseña
    return UserOut(**nuevo_usuario)

# ============ LOGIN (corregido) ============

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: UserLogin):
    """
    Endpoint para iniciar sesión.
    Límite: 5 intentos por minuto por IP.
    """
    # 1. Buscar usuario por email
    user_found = None
    for user_key, user_data in fake_users_db.items():
        if user_data["email"] == user_credentials.email:
            user_found = user_data
            break

    # 2. Si no existe, error
    if not user_found:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas"
        )

    # 3. Verificar contraseña
    try:
        if not verify_password(user_credentials.password, user_found["password"]):
            raise HTTPException(
                status_code=401,
                detail="Credenciales incorrectas"
            )
    except Exception as e:
        # Si hay error con bcrypt, mostrarlo claro
        print(f"Error verificando password: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al verificar credenciales"
        )

    # 4. Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_found["email"]}, 
        expires_delta=access_token_expires
    )

    # 5. Devolver token
    return {"access_token": access_token, "token_type": "bearer"}

# ============ LOGIN CON FORM (para Swagger) ============

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Endpoint para login usando form-data (para Swagger UI).
    """
    # Buscar usuario por email (form_data.username trae el email)
    user_found = None
    for user_key, user_data in fake_users_db.items():
        if user_data["email"] == form_data.username:
            user_found = user_data
            break

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