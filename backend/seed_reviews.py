# backend/seed_reviews.py

import asyncio
import random
from bson import ObjectId

from app.database import books_collection, reviews_collection
from app.nlp.sentiment import analyze_sentiment

# -------------------------
# Reseñas predefinidas
# -------------------------

POSITIVE_REVIEWS = [
    "Me encantó, la historia fue emocionante.",
    "Un libro increíble, muy bien escrito.",
    "Disfruté cada capítulo, totalmente recomendado.",
    "El desarrollo de personajes fue excelente.",
    "Una lectura muy agradable y llena de emoción.",
    "Me atrapó desde el inicio, maravilloso.",
]

NEGATIVE_REVIEWS = [
    "La historia se me hizo aburrida y muy lenta.",
    "No cumplió mis expectativas.",
    "Los personajes no me parecieron interesantes.",
    "Demasiado predecible y sin emoción.",
    "No lo volvería a leer.",
    "Muy mal ritmo narrativo.",
]

NEUTRAL_REVIEWS = [
    "Es un libro decente, nada especial.",
    "Tuvo partes buenas y malas.",
    "Una experiencia normal, no destaca mucho.",
    "Interesante pero no memorable.",
    "Un libro promedio, aceptable.",
]

USERNAMES = [
    "juan23", "lectora_ana", "pedro.g", "sofia_reader",
    "mario88", "camila.l", "booklover", "andres_17",
    "vicente_d", "usuario_test"
]


# -------------------------
# Función generadora
# -------------------------

def generate_review_text(sentiment: str) -> str:
    if sentiment == "positive":
        return random.choice(POSITIVE_REVIEWS)
    if sentiment == "negative":
        return random.choice(NEGATIVE_REVIEWS)
    return random.choice(NEUTRAL_REVIEWS)


async def seed_reviews(reviews_per_book=5):
    print("Eliminando reseñas existentes...")
    await reviews_collection.delete_many({})

    print("Obteniendo libros...")
    books = await books_collection.find({}).to_list(None)

    if not books:
        print("❌ No hay libros en la base de datos. Ejecuta seed.py primero.")
        return

    total_reviews = 0
    print(f"Insertando {reviews_per_book} reseñas por libro...")

    for book in books:
        book_id = book["_id"]

        for _ in range(reviews_per_book):
            sentiment_label = random.choice(["positive", "negative", "neutral"])
            text = generate_review_text(sentiment_label)

            # análisis real de sentimiento
            label, score = analyze_sentiment(text)

            review_doc = {
                "book_id": book_id,
                "username": random.choice(USERNAMES),
                "text": text,
                "sentiment_label": label,
                "sentiment_score": score,
            }

            await reviews_collection.insert_one(review_doc)
            total_reviews += 1

    print(f"✔ Reseñas insertadas correctamente: {total_reviews}")


if __name__ == "__main__":
    asyncio.run(seed_reviews(reviews_per_book=20))
    print("Base de datos de reseñas poblada correctamente 🚀📝")
