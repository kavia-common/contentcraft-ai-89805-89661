from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..db.models.user import User
from ..core.security import hash_password, verify_password, create_access_token
from ..core.config import settings
from ..schemas.auth import UserCreate, UserOut, Token
from ..core.deps import get_current_user

router = APIRouter()


@router.post("/signup", response_model=UserOut, summary="Create a new user")
# PUBLIC_INTERFACE
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user.

    Args:
        payload: UserCreate with email, password, full_name
        db: DB session

    Returns:
        UserOut: Created user.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, full_name=payload.full_name, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(id=user.id, email=user.email, full_name=user.full_name)


@router.post("/login", response_model=Token, summary="Obtain JWT access token")
# PUBLIC_INTERFACE
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login using OAuth2 form data (username=email) to obtain an access token.

    Args:
        form_data: OAuth2PasswordRequestForm containing username and password
        db: DB session

    Returns:
        Token: JWT access token.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(subject=user.email, expires_delta=access_token_expires)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut, summary="Get current user profile")
# PUBLIC_INTERFACE
def me(current_user: User = Depends(get_current_user)):
    """Get current user profile.

    Returns:
        UserOut: Authenticated user.
    """
    return UserOut(id=current_user.id, email=current_user.email, full_name=current_user.full_name)
