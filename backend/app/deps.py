from typing import Literal

from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.db.mongo import db
from app.schemas.user import UserPublic

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid id") from exc


def serialize_doc(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc

    user = await db.users.find_one({"_id": to_object_id(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    user = serialize_doc(user)
    return UserPublic(**user)


def require_role(role: Literal["student", "teacher"]):
    async def _role_guard(user: UserPublic = Depends(get_current_user)) -> UserPublic:
        if user.role != role:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _role_guard
