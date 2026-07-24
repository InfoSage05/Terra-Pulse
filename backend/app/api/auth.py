from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, GoogleAuthRequest, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

COOKIE_KWARGS = dict(
    httponly=True,
    samesite="lax",   # works for localhost:5173 <-> localhost:8000 (same-site, diff port)
    secure=False,      # set True in production (requires HTTPS)
    max_age=settings.JWT_EXPIRE_MINUTES * 60,
    path="/",
)

def set_auth_cookie(response: Response, user_id: int):
    token = create_access_token({"sub": str(user_id)})
    response.set_cookie(key="access_token", value=token, **COOKIE_KWARGS)


@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        name=payload.name,
        hashed_password=hash_password(payload.password),
        auth_provider="email",
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    set_auth_cookie(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    set_auth_cookie(response, user.id)
    return user


@router.post("/google", response_model=UserOut)
def google_auth(payload: GoogleAuthRequest, response: Response, db: Session = Depends(get_db)):
    # Verify the ID token was actually issued by Google for OUR client ID.
    # This is the step that prevents anyone from forging a fake login.
    try:
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    email = idinfo.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    name = idinfo.get("name")
    picture = idinfo.get("picture")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            name=name,
            picture=picture,
            hashed_password=None,
            auth_provider="google",
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Keep name/picture fresh on subsequent Google logins
        user.name = name or user.name
        user.picture = picture or user.picture
        db.commit()

    set_auth_cookie(response, user.id)
    return user


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/")
    return {"detail": "Logged out"}