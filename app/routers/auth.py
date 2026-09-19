from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import Token, UserRegister, UserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await db.scalar(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="user",
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=Token)
async def login_user(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    user = await db.scalar(select(User).where(User.username == user_data.username))

    if user is None or not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
