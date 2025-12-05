from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Relación 1 a muchos: un libro tiene muchas reseñas
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), index=True)
    username = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    sentiment_label = Column(String, nullable=False)  # positive / negative / neutral
    sentiment_score = Column(Float, nullable=False)   # aprox entre -1 y 1

    # Relación inversa: la reseña pertenece a un libro
    book = relationship("Book", back_populates="reviews")
