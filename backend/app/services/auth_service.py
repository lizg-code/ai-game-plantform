from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token


def register_user(db: Session, req: RegisterRequest) -> TokenResponse:
    """Register a new user with email and password."""
    # Check if email already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        nickname=req.nickname or req.email.split("@")[0],
        auth_provider="local",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Return token
    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token)


def login_user(db: Session, req: LoginRequest) -> TokenResponse:
    """Authenticate user with email and password, return JWT token."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id, user.email)
    return TokenResponse(access_token=token)


def get_user_info(user: User) -> UserResponse:
    """Convert User model to UserResponse."""
    return UserResponse.model_validate(user)
