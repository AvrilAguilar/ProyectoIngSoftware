# backend/app/recommend_user.py

from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_user
from .database import books_collection
from .schemas import RecommendationOut
from bson import ObjectId

router = APIRouter(prefix="/recommend", tags=["Recommendations"])


@router.get("/by-quiz", response_model=list[RecommendationOut])
async def recommend_by_quiz(user=Depends(get_current_user)):

    quiz = user.get("quiz")
    if not quiz:
        raise HTTPException(status_code=400, detail="User has no quiz results")

    genre_pref = quiz["favorite_genre"].lower()
    action_level = quiz["action_level"]
    keywords = [k.lower() for k in quiz["keywords"]]

    books = await books_collection.find({}).to_list(None)

    recommendations = []

    for book in books:
        score = 0
        desc = book["description"].lower()
        title = book["title"].lower()

        # Coincidencia por género (muy importante)
        if genre_pref in desc or genre_pref in title:
            score += 3

        # Coincidencia por keywords del quiz
        for kw in keywords:
            if kw in desc:
                score += 2

        # Acción
        if action_level == "high" and "batalla" in desc:
            score += 1
        if action_level == "low" and "romance" in desc:
            score += 1

        if score > 0:
            recommendations.append({
                "book_id": str(book["_id"]),
                "title": book["title"],
                "score": score
            })

    # Ordenar por puntaje
    recommendations.sort(key=lambda x: x["score"], reverse=True)

    return recommendations[:10]  # top 10
