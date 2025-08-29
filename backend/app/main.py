from fastapi import FastAPI
from app.routers import auth  # Importamos el router que acabamos de crear

# Creamos la aplicación de FastAPI
app = FastAPI(
    title="Ciclopuerto API",
    description="API para el control de acceso del ciclopuerto 2v",
    version="0.1.0"
)

# "Montamos" el router de autenticación en nuestra app.
# Esto significa que todas las rutas en `auth.py` empezarán con `/auth`.
app.include_router(auth.router)

# Una ruta simple en la raíz para saludar
@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API del Ciclopuerto 2V! 🚴‍♂️"}
