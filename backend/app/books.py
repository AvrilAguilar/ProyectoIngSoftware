from typing import List
from fastapi import APIRouter, HTTPException
from bson import ObjectId

from .database import books_collection, reviews_collection
from .schemas import BookCreate, BookOut
from .nlp.sentiment import analyze_sentiment
from .nlp.keywords import extract_keywords

router = APIRouter(prefix="/books", tags=["Books"])


def object_id_or_404(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(status_code=400, detail="Invalid id format")


def document_to_book_out(doc) -> BookOut:
    return BookOut(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        author=doc.get("author"),
        description=doc.get("description"),
    )


@router.post("/", response_model=BookOut)
async def create_book(book: BookCreate):
    new_book = book.dict()
    result = await books_collection.insert_one(new_book)
    new_book["_id"] = result.inserted_id
    return document_to_book_out(new_book)


@router.get("/", response_model=List[BookOut])
async def list_books():
    books = []
    async for doc in books_collection.find({}):
        books.append(document_to_book_out(doc))
    return books


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: str):
    oid = object_id_or_404(book_id)
    doc = await books_collection.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Book not found")
    return document_to_book_out(doc)
