from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models import UserLogin, UserOut
from app.database import fake_users_db
from passlib.context import CryptContext #Importamos la herramienta para verificar contraseñas

# Configuración para el hashing de contraseñas. Le decimos que use bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esto le dice a FastAPI que nuestro endpoint de login estará en /auth/token (útil para la doc later)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/auth", tags=["auth"])

# Función para verificar la contraseña plana contra el hash guardado
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/login", response_model=UserOut)
async def login(user_credentials: UserLogin):
    """
    Endpoint para iniciar sesión.
    Recibe un JSON con 'email' y 'password'.
    """    
    # 1. Buscar al usuario en la base de datos por su email
    user_found = None
    for user_key, user_data in fake_users_db.items():
        if user_data["email"] == user_credentials.email:
            user_found = user_data
            break

    #Error si no encuentra usuario
    if not user_found:
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas."
        )

    #VERIFICACION PASSWORD
    if not verify_password(user_credentials.password, user_found["password"]):
        raise HTTPException(
            status_code=401,
            detail="Credenciales incorrectas."
        )

    # 4. Si supera todo lo anterior, las credenciales son válidas.
    return user_found


# Este endpoint es un estándar para OAuth2. FastAPI lo usa para su doc interactiva.
# Por ahora devuelve un token falso, pero luego generaremos JWT aquí.
@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordBearer = Depends()):
    # La magia de los tokens JWT vendrá aquí después.
    # Por ahora, devolvemos un token de mentira para que la doc no se quebre.
    return {"access_token": "fake-super-secret-token", "token_type": "bearer"}