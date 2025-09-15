from fastapi import FastAPI
from app.routers import auth, users, bicicletas  # Importamos el router que acabamos de crear

# Creamos la aplicación de FastAPI
app = FastAPI(
    title="Ciclopuerto API",
    description="API para el control de acceso del ciclopuerto 2v",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(bicicletas.router)

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API del Ciclopuerto 2V! 🚴‍♂️"}


