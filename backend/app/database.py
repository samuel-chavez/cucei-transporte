from datetime import datetime, timedelta
import secrets

# Configuración para JWT. Cadena secreta y segura en producción
SECRET_KEY = "ciclopuerto_2v_secret_key_2025B" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # El token expira en 30 minutos


# Fake database para bicicletas
fake_registros_db = {
    "reg_1": {
        "id": "reg_1",
        "bicicleta_id": "bici_1",
        "usuario_id": 1,
        "usuario_nombre": "David Melgoza",
        "bicicleta_marca": "Trek",
        "bicicleta_modelo": "Marlin 5",
        "fecha_entrada": datetime(2025, 8, 15, 8, 30, 0),
        "fecha_salida": datetime(2025, 8, 15, 14, 45, 0),
        "activo": False  # Ya salió
    },
    "reg_2": {
        "id": "reg_2",
        "bicicleta_id": "bici_1",
        "usuario_id": 1,
        "usuario_nombre": "David Melgoza",
        "bicicleta_marca": "Trek",
        "bicicleta_modelo": "Marlin 5",
        "fecha_entrada": datetime(2025, 8, 16, 9, 15, 0),
        "fecha_salida": None,  # ¡Todavía dentro!
        "activo": True
    },
    "reg_3": {
        "id": "reg_3",
        "bicicleta_id": "bici_3",
        "usuario_id": 2,
        "usuario_nombre": "Samuel Chavez",
        "bicicleta_marca": "Giant",
        "bicicleta_modelo": "Talon",
        "fecha_entrada": datetime(2025, 8, 16, 10, 0, 0),
        "fecha_salida": None,
        "activo": True
    }
}


fake_bicicletas_db = {}

#encriptado en bcrypt, base de datos falsa/temporal para ver si jala
