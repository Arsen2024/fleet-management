from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/admin")
async def admin_panel(
    current_user: User = Depends(require_admin),
):
    return {
        "message": "Welcome to the admin panel",
        "username": current_user.username,
        "role": current_user.role,
    }
