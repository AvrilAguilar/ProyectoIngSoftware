# backend/app/database.py

from motor.motor_asyncio import AsyncIOMotorClient
import os

# URL de conexión a MongoDB (puedes usar variable de entorno si quieres)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

# Nombre de la base de datos
DB_NAME = os.getenv("MONGO_DB_NAME", "book_reviews_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Colecciones
books_collection = db["books"]
reviews_collection = db["reviews"]
users_collection = db["users"]  # ⬅⬅ NECESARIO para auth / quiz
