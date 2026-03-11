from dotenv import load_dotenv
from pathlib import Path
import os
from pymongo import MongoClient

# Cargar variables del .env
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

# Obtener variables de entorno
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

print("ENV PATH:", env_path)
print("MONGO_URI:", MONGO_URI)
print("DB_NAME:", DB_NAME)

# Verificar que existan
if not MONGO_URI or not DB_NAME:
    raise Exception("Variables de entorno MONGO_URI o DB_NAME no definidas")

# Crear cliente de MongoDB
client = MongoClient(MONGO_URI)

# Seleccionar base de datos
db = client[DB_NAME]