from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_current_user, require_admin
from app.models.user import User

router = APIRouter(
    prefix="/home",
    tags=["Home"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/user", response_class=HTMLResponse)
async def user_home(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="user_home.html",
        context={
            "username": current_user.username,
            "role": current_user.role,
        },
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_home(
    request: Request,
    current_user: User = Depends(require_admin),
):
    return templates.TemplateResponse(
        request=request,
        name="admin_home.html",
        context={
            "username": current_user.username,
            "role": current_user.role,
        },
    )
