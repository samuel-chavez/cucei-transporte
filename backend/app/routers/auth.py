from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.models import UserLogin, Token
from app.database.database_mongo import db
from app.exceptions import InvalidCredentialsException, ValidationException
from app.logger import log_login_attempt
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

# Configuración JWT
SECRET_KEY = "secret_key_ciclopuerto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Limiter para evitar ataques
limiter = Limiter(key_func=get_remote_address)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])

# colección de usuarios
usuarios_collection = db["usuarios"]


# verificar contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# crear token JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# LOGIN PRINCIPAL
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(request: Request, user_credentials: UserLogin):

    client_ip = request.client.host if request.client else "unknown"

    try:

        # buscar usuario en MongoDB
        user_found = usuarios_collection.find_one({
            "email": user_credentials.email
        })

        if not user_found:
            log_login_attempt(
                email=user_credentials.email,
                success=False,
                client_ip=client_ip,
                details="Usuario no encontrado"
            )
            raise InvalidCredentialsException()

        # verificar contraseña
        if not verify_password(user_credentials.password, user_found["password"]):

            log_login_attempt(
                email=user_credentials.email,
                success=False,
                client_ip=client_ip,
                details="Contraseña incorrecta"
            )

            raise InvalidCredentialsException()

        # login exitoso
        log_login_attempt(
            email=user_credentials.email,
            success=True,
            client_ip=client_ip
        )

        # crear token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data={"sub": user_found["email"]},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except ValueError as e:

        log_login_attempt(
            email=user_credentials.email,
            success=False,
            client_ip=client_ip,
            details=f"Error validación: {str(e)}"
        )

        raise ValidationException(detail=str(e))


# LOGIN PARA SWAGGER
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    user_found = usuarios_collection.find_one({
        "email": form_data.username
    })

    if not user_found or not verify_password(form_data.password, user_found["password"]):
        raise InvalidCredentialsException()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = create_access_token(
        data={"sub": user_found["email"]},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }