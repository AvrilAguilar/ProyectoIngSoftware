# backend/app/auth.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.hash import pbkdf2_sha256
from jose import jwt, JWTError
from bson import ObjectId

from .database import users_collection
from .schemas import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
    scheme_name="JWT"
)


def user_doc_to_out(doc):
    return UserOut(
        id=str(doc["_id"]),
        username=doc["username"],
        email=doc["email"]
    )


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):

    exists = await users_collection.find_one({"email": user.email})
    if exists:
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


@router.post("/login", response_model=dict)   # 👈 **FIX IMPORTANTE**
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = await users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not pbkdf2_sha256.verify(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = jwt.encode(
        {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"]
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
