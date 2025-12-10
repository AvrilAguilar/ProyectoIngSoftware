# backend/app/main.py

from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Base de datos
from .database import books_collection, reviews_collection

# Schemas
from . import schemas

# NLP
from .nlp.sentiment import analyze_sentiment
from .nlp.keywords import extract_keywords

# Routers
from .auth import router as auth_router
from .quiz import router as quiz_router
from .recommend_user import router as recommend_user_router

# Seguridad
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi


# ============================================================
#   FASTAPI APP CONFIG + SECURITY FIX
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(
    title="Book Review Recommender & NLP (MongoDB)",
    description="API para reseñas, sentimiento, keywords, quiz y recomendaciones.",
    version="3.0.0",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
)


# --- CORS ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Routers ---
app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(recommend_user_router)


@app.get("/")
async def root():
    return {"message": "API funcionando 🔥 MongoDB + FastAPI + NLP"}


# ============================================================
#   CUSTOM OPENAPI (PARA QUE SWAGGER USE BEARER TOKEN)
# ============================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Book Review Recommender & NLP (MongoDB)",
        version="3.0.0",
        routes=app.routes,
    )

    # SECURITY SCHEMA FIX
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {}
                }
            }
        }
    }

    # Aplicar seguridad global a rutas que lo pidan
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================
#  HELPERS
# ============================================================

def object_id_or_404(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid id format")


def document_to_book_out(doc) -> schemas.BookOut:
    return schemas.BookOut(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        author=doc.get("author"),
        description=doc.get("description"),
    )


def document_to_review_out(doc) -> schemas.ReviewOut:
    return schemas.ReviewOut(
        id=str(doc["_id"]),
        username=doc.get("username"),
        text=doc.get("text", ""),
        sentiment_label=doc.get("sentiment_label", "neutral"),
        sentiment_score=float(doc.get("sentiment_score", 0.0)),
    )


# ============================================================
#  BOOK ENDPOINTS
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
    cursor = books_collection.find({})
    books = []
    async for doc in cursor:
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
#  REVIEWS
# ============================================================

@app.post("/books/{book_id}/reviews", response_model=schemas.ReviewOut)
async def create_review(book_id: str, review: schemas.ReviewCreate):

    book_oid = object_id_or_404(book_id)
    book = await books_collection.find_one({"_id": book_oid})

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

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

    oid = object_id_or_404(book_id)
    cursor = reviews_collection.find({"book_id": oid})

    reviews = []
    async for doc in cursor:
        reviews.append(document_to_review_out(doc))

    return reviews


# ============================================================
#  SUMMARY (Sentiment + Keywords)
# ============================================================

@app.get("/books/{book_id}/summary")
async def get_book_summary(book_id: str):

    oid = object_id_or_404(book_id)
    reviews = await reviews_collection.find({"book_id": oid}).to_list(None)

    if not reviews:
        return {
            "book_id": book_id,
            "total_reviews": 0,
            "positive": 0,
            "negative": 0,
            "avg_sentiment_score": 0,
            "keywords": [],
        }

    total = len(reviews)
    positive_count = sum(r["sentiment_label"] == "positive" for r in reviews)
    negative_count = sum(r["sentiment_label"] == "negative" for r in reviews)
    scores = [float(r.get("sentiment_score", 0)) for r in reviews]

    positive_pct = round((positive_count / total) * 100, 2)
    negative_pct = round((negative_count / total) * 100, 2)
    avg_score = round(sum(scores) / total, 4)

    texts = [r["text"] for r in reviews]
    keywords = extract_keywords(texts, top_k=5)

    return {
        "book_id": book_id,
        "total_reviews": total,
        "positive": positive_pct,
        "negative": negative_pct,
        "avg_sentiment_score": avg_score,
        "keywords": keywords,
    }


# ============================================================
#  BOOK RECOMMENDATIONS (TF-IDF)
# ============================================================

@app.get("/books/{book_id}/recommendations")
async def recommend_books(book_id: str):

    try:
        ObjectId(book_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid book ID")

    all_books = await books_collection.find({}).to_list(None)

    corpus = []
    ids = []

    for b in all_books:
        ids.append(str(b["_id"]))

        reviews = await reviews_collection.find({"book_id": b["_id"]}).to_list(None)

        if reviews:
            text = " ".join(r["text"] for r in reviews)
        else:
            text = (b.get("description") or "")

        corpus.append(text)

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform(corpus)

    sims = cosine_similarity(tfidf)

    if book_id not in ids:
        raise HTTPException(status_code=404, detail="Book not found")

    i = ids.index(book_id)
    scores = [(idx, sims[i][idx]) for idx in range(len(ids)) if idx != i]
    scores.sort(key=lambda x: x[1], reverse=True)

    recommendations = [
        {
            "id": ids[idx],
            "title": all_books[idx]["title"],
            "similarity": round(float(score), 3),
        }
        for idx, score in scores[:5]
    ]

    return {"book_id": book_id, "recommendations": recommendations}
