from datetime import datetime
from database import users_collection
from fastapi import APIRouter, HTTPException, status
import httpx
from models import Token, UserCreate, UserLogin, UserResponse
from security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# 1. User Signup
@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(user: UserCreate):
  existing_user = await users_collection.find_one({"email": user.email})
  if existing_user:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered",
    )

  hashed_password = get_password_hash(user.password)
  user_dict = {
      "email": user.email,
      "password": hashed_password,
      "created_at": datetime.utcnow(),
  }

  result = await users_collection.insert_one(user_dict)

  return {
      "id": str(result.inserted_id),
      "email": user_dict["email"],
      "created_at": user_dict["created_at"],
  }


# 2. Email / Password Login
@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
  user = await users_collection.find_one({"email": user_credentials.email})

  stored_hash = user.get("password") if user else None

  # Agar user Google se sign-up ho kar aaya hai toh password check handle karein
  if not user or not stored_hash:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )

  try:
    if not verify_password(user_credentials.password, stored_hash):
      raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail="Incorrect email or password",
      )
  except Exception:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )

  access_token = create_access_token(data={"sub": str(user["_id"])})

  return {"access_token": access_token, "token_type": "bearer"}


# 3. Google OAuth Login Endpoint
@router.post("/google", response_model=Token)
async def google_login(payload: dict):
  google_token = payload.get("access_token")
  if not google_token:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Google Access Token missing",
    )

  # Google User Info API call to verify token
  async with httpx.AsyncClient() as client:
    resp = await client.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {google_token}"},
    )

  if resp.status_code != 200:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired Google Token",
    )

  google_data = resp.json()
  email = google_data.get("email")
  name = google_data.get("name", "")

  if not email:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Could not retrieve email from Google",
    )

  # Check if user exists in MongoDB
  user = await users_collection.find_one({"email": email})

  if not user:
    new_user = {
        "email": email,
        "name": name,
        "auth_provider": "google",
        "created_at": datetime.utcnow(),
    }
    result = await users_collection.insert_one(new_user)
    user_id = str(result.inserted_id)
  else:
    user_id = str(user["_id"])

  # Generate JWT Token for ApplyPulse
  access_token = create_access_token(data={"sub": user_id})

  return {"access_token": access_token, "token_type": "bearer"}