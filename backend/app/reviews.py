from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId

from .database import books_collection, reviews_collection
from .schemas import ReviewCreate, ReviewOut
from .nlp.sentiment import analyze_sentiment

router = APIRouter(prefix="/books", tags=["Reviews"])


def object_id_or_404(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid id format")


def document_to_review_out(doc) -> ReviewOut:
    return ReviewOut(
        id=str(doc["_id"]),
        username=doc.get("username"),
        text=doc.get("text", ""),
        sentiment_label=doc.get("sentiment_label", "neutral"),
        sentiment_score=float(doc.get("sentiment_score", 0.0)),
    )


@router.post("/{book_id}/reviews", response_model=ReviewOut)
async def create_review(book_id: str, review: ReviewCreate):
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


@router.get("/{book_id}/reviews", response_model=List[ReviewOut])
async def list_reviews(book_id: str):
    book_oid = object_id_or_404(book_id)

    reviews = []
    async for doc in reviews_collection.find({"book_id": book_oid}):
        reviews.append(document_to_review_out(doc))

    return reviews
