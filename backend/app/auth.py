# backend/app/auth.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.hash import pbkdf2_sha256
from jose import jwt, JWTError
from bson import ObjectId

from .database import users_collection
from .schemas import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

security = HTTPBearer()


def user_doc_to_out(doc):
    return UserOut(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"]
    )


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    if await users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = pbkdf2_sha256.hash(user.password)

    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed,
        "quiz": None
    }

    result = await users_collection.insert_one(new_user)
    new_user["_id"] = result.inserted_id

    return user_doc_to_out(new_user)


@router.post("/login")
async def login(data: dict):
    user = await users_collection.find_one({"email": data.get("email")})
    if not user or not pbkdf2_sha256.verify(data.get("password"), user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
