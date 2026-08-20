import os
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
from database import users_collection
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
  return pwd_context.hash(password)


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
  to_encode = data.copy()
  expire = datetime.utcnow() + (
      expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  )
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
  credentials_exception = HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
  )

  if not auth or not auth.credentials:
    raise credentials_exception

  token = auth.credentials

  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    if not user_id:
      raise credentials_exception
  except JWTError:
    raise credentials_exception

  # Invalid ObjectId format check
  if not ObjectId.is_valid(user_id):
    raise credentials_exception

  user = await users_collection.find_one({"_id": ObjectId(user_id)})
  if user is None:
    raise credentials_exception

  return user