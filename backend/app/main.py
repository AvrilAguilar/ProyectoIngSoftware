from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .database import books_collection, reviews_collection
from . import schemas
from .nlp.sentiment import analyze_sentiment
from .nlp.keywords import extract_keywords


# ============================================================
#  FASTAPI CONFIG
# ============================================================

app = FastAPI(
    title="Book Review Recommender & NLP (MongoDB)",
    description="API para reseñas de libros con análisis de sentimiento y palabras clave usando MongoDB.",
    version="2.0.0",
)

# CORS para permitir llamadas desde React
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"  # Solo en desarrollo
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "API de reseñas de libros con NLP y MongoDB funcionando"}


# ============================================================
#  HELPERS
# ============================================================

def object_id_or_404(id_str: str) -> ObjectId:
    """Convierte un string a ObjectId o lanza error 400 si no es válido."""
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id format")


def document_to_book_out(doc) -> schemas.BookOut:
    """Convierte un documento Mongo → BookOut"""
    return schemas.BookOut(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        author=doc.get("author"),
        description=doc.get("description"),
    )


def document_to_review_out(doc) -> schemas.ReviewOut:
    """Convierte un documento Mongo → ReviewOut"""
    return schemas.ReviewOut(
        id=str(doc["_id"]),
        username=doc.get("username"),
        text=doc.get("text", ""),
        sentiment_label=doc.get("sentiment_label", "neutral"),
        sentiment_score=float(doc.get("sentiment_score", 0.0)),
    )


# ============================================================
#  ENDPOINTS: LIBROS
# ============================================================

@app.post("/books", response_model=schemas.BookOut)
async def create_book(book: schemas.BookCreate):
    new_book = {
        "title": book.title,
        "author": book.author,
        "description": book.description,
    }
    result = await books_collection.insert_one(new_book)
    new_book["_id"] = result.inserted_id
    return document_to_book_out(new_book)


@app.get("/books", response_model=List[schemas.BookOut])
async def list_books():
    books_cursor = books_collection.find({})
    books: List[schemas.BookOut] = []
    async for doc in books_cursor:
        books.append(document_to_book_out(doc))
    return books


@app.get("/books/{book_id}", response_model=schemas.BookOut)
async def get_book(book_id: str):
    oid = object_id_or_404(book_id)
    doc = await books_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Book not found")
    return document_to_book_out(doc)


# ============================================================
#  ENDPOINTS: RESEÑAS
# ============================================================

@app.post("/books/{book_id}/reviews", response_model=schemas.ReviewOut)
async def create_review(book_id: str, review: schemas.ReviewCreate):
    book_oid = object_id_or_404(book_id)

    # Confirmar existencia del libro
    book_doc = await books_collection.find_one({"_id": book_oid})
    if not book_doc:
        raise HTTPException(status_code=404, detail="Book not found")

    # Análisis de sentimiento
    label, score = analyze_sentiment(review.text)

    new_review = {
        "book_id": book_oid,
        "username": review.username,
        "text": review.text,
        "sentiment_label": label,
        "sentiment_score": score,
    }

    result = await reviews_collection.insert_one(new_review)
    new_review["_id"] = result.inserted_id

    return document_to_review_out(new_review)


@app.get("/books/{book_id}/reviews", response_model=List[schemas.ReviewOut])
async def list_reviews(book_id: str):
    book_oid = object_id_or_404(book_id)

    book_doc = await books_collection.find_one({"_id": book_oid})
    if not book_doc:
        raise HTTPException(status_code=404, detail="Book not found")

    cursor = reviews_collection.find({"book_id": book_oid})
    reviews = []
    async for doc in cursor:
        reviews.append(document_to_review_out(doc))

    return reviews


# ============================================================
#  ENDPOINT: RESUMEN EMOCIONAL
# ============================================================

@app.get("/books/{book_id}/summary")
async def get_book_summary(book_id: str):
    try:
        book_obj = ObjectId(book_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid book ID")

    reviews_cursor = reviews_collection.find({"book_id": book_obj})
    reviews = await reviews_cursor.to_list(length=None)

    if len(reviews) == 0:
        return {
            "book_id": book_id,
            "total_reviews": 0,
            "positive": 0,
            "negative": 0,
            "avg_sentiment_score": 0,
            "keywords": []
        }

    # Conteo de sentimientos
    positive_count = sum(1 for r in reviews if r["sentiment_label"] == "positive")
    negative_count = sum(1 for r in reviews if r["sentiment_label"] == "negative")

    total = len(reviews)

    positive_percent = round((positive_count / total) * 100, 2)
    negative_percent = round((negative_count / total) * 100, 2)

    # Promedio del puntaje de sentimiento
    sentiment_scores = [float(r.get("sentiment_score", 0)) for r in reviews]
    avg_sentiment_score = round(sum(sentiment_scores) / total, 4)

    # Extracción de keywords TF-IDF
    texts = [r["text"] for r in reviews]
    keywords = extract_keywords(texts, top_k=5)

    return {
        "book_id": book_id,
        "total_reviews": total,
        "positive": positive_percent,
        "negative": negative_percent,
        "avg_sentiment_score": avg_sentiment_score,
        "keywords": keywords
    }


# ============================================================
#  ENDPOINT: RECOMENDACIONES
# ============================================================

@app.get("/books/{book_id}/recommendations")
async def recommend_books(book_id: str):

    try:
        target_book_oid = ObjectId(book_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid book ID")

    all_books_cursor = books_collection.find({})
    all_books = await all_books_cursor.to_list(length=None)

    if len(all_books) < 2:
        return {"book_id": book_id, "recommendations": []}

    # Construir textos por libro
    book_texts = {}
    for book in all_books:
        book_oid = book["_id"]

        reviews_cursor = reviews_collection.find({"book_id": book_oid})
        reviews = await reviews_cursor.to_list(length=None)

        if len(reviews) > 0:
            combined_text = " ".join([r["text"] for r in reviews])
        else:
            combined_text = book.get("description", "")

        book_texts[str(book_oid)] = combined_text

    # TF-IDF corpus
    book_ids = list(book_texts.keys())
    corpus = [book_texts[_id] for _id in book_ids]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    similarities = cosine_similarity(tfidf_matrix)

    try:
        target_index = book_ids.index(book_id)
    except:
        raise HTTPException(status_code=404, detail="Book not found")

    similarity_scores = [
        (idx, score)
        for idx, score in enumerate(similarities[target_index])
        if idx != target_index
    ]

    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    recommendations = []
    for idx, score in similarity_scores[:5]:
        similar_book_id = book_ids[idx]
        similar_book = await books_collection.find_one({"_id": ObjectId(similar_book_id)})

        recommendations.append({
            "id": similar_book_id,
            "title": similar_book["title"],
            "similarity": round(float(score), 3)
        })

    return {"book_id": book_id, "recommendations": recommendations}
