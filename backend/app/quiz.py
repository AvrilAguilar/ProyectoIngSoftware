# backend/app/quiz.py

from fastapi import APIRouter, Depends, HTTPException
from .auth import get_current_user
from .database import users_collection
from .schemas import QuizAnswers, QuizOut

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/save", response_model=QuizOut)
async def save_quiz(
    answers: QuizAnswers,
    user=Depends(get_current_user)
):
    quiz_dict = answers.dict()

    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"quiz": quiz_dict}}
    )

    return QuizOut(
        user_id=str(user["_id"]),
        quiz=quiz_dict
    )


@router.get("/me", response_model=QuizOut)
async def get_my_quiz(user=Depends(get_current_user)):
    quiz = user.get("quiz")
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not completed")

    return QuizOut(
        user_id=str(user["_id"]),
        quiz=quiz
    )
