from pydantic import BaseModel
from typing import Optional, List, Dict


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


# ===== Usuarios =====

class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    email: str


# ===== Quiz =====

class QuizAnswers(BaseModel):
    favorite_genre: str
    action_level: str  # "low", "medium", "high"
    keywords: List[str]


class QuizOut(BaseModel):
    user_id: str
    quiz: Dict  # mejor que "dict" porque usa tipado pydantic


# ===== Recomendaciones =====

class RecommendationOut(BaseModel):
    book_id: str
    title: str
    score: int
