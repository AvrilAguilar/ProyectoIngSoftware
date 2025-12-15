from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .quiz import router as quiz_router
from .recommend_user import router as recommend_user_router
from .books import router as books_router
from .reviews import router as reviews_router

app = FastAPI(
    title="Book Review Recommender API",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(recommend_user_router)
app.include_router(books_router)
app.include_router(reviews_router)

@app.get("/")
async def root():
    return {"message": "API funcionando 🔥"}
