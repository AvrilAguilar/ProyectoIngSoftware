from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict


# ======================
# RESEÑAS
# ======================

class ReviewBase(BaseModel):
    username: Optional[str] = None
    text: str


class ReviewCreate(ReviewBase):
    pass


class ReviewOut(ReviewBase):
    id: str
    sentiment_label: str
    sentiment_score: float


# ======================
# LIBROS
# ======================

class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None


class BookCreate(BookBase):
    pass


class BookOut(BookBase):
    id: str


# ======================
# RESUMEN EMOCIONAL
# ======================

class BookSummary(BaseModel):
    book_id: str
    total_reviews: int
    positive_pct: float
    negative_pct: float
    neutral_pct: float
    keywords: List[str]


# ======================
# USUARIOS (AUTH)
# ======================

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ======================
# QUIZ
# ======================

class QuizAnswers(BaseModel):
    favorite_genre: str
    action_level: str  # "low" | "medium" | "high"
    keywords: List[str]


class QuizOut(BaseModel):
    user_id: str
    quiz: Dict[str, object]


# ======================
# RECOMENDACIONES
# ======================

class RecommendationOut(BaseModel):
    book_id: str
    title: str
    score: int
