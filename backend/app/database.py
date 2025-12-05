from motor.motor_asyncio import AsyncIOMotorClient

# URL de conexión a MongoDB (local por defecto)
MONGO_URL = "mongodb://localhost:27017"

# Nombre de la base de datos
DB_NAME = "book_reviews_db"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Colecciones
books_collection = db["books"]
reviews_collection = db["reviews"]
