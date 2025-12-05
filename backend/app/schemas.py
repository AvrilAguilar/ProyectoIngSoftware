from pydantic import BaseModel
from typing import Optional, List


# ===== Reseñas =====

class ReviewBase(BaseModel):
    username: Optional[str] = None
    text: str


class ReviewCreate(ReviewBase):
    pass


class ReviewOut(ReviewBase):
    id: str
    sentiment_label: str
    sentiment_score: float


# ===== Libros =====

class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookOut(BookBase):
    id: str


# ===== Resumen emocional =====

class BookSummary(BaseModel):
    book_id: str
    total_reviews: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    keywords: List[str]
