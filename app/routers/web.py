from pathlib import Path

import jwt
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import AsyncSessionLocal
from app.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.user import UserRegister
from app.security import ALGORITHM, create_access_token, hash_password, verify_password

router = APIRouter(tags=["Web"])

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 30 * 60


def get_cookie_options():
    return {
        "httponly": True,
        "secure": not settings.debug,
        "samesite": "lax",
        "max_age": COOKIE_MAX_AGE,
        "path": "/",
    }


@router.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    token = request.cookies.get(COOKIE_NAME)

    if token:
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[ALGORITHM],
            )
            user_id = payload.get("sub")

            if user_id is not None:
                async with AsyncSessionLocal() as db:
                    user = await db.scalar(select(User).where(User.id == int(user_id)))

                if user:
                    destination = (
                        "/home/admin" if user.role == "admin" else "/home/user"
                    )
                    return RedirectResponse(destination, status_code=303)
        except (InvalidTokenError, ValueError):
            pass

    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"error": None},
    )


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
    password_confirm: str = Form(),
):
    if password != password_confirm:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Паролі не збігаються."},
            status_code=400,
        )

    try:
        user_data = UserRegister.model_validate(
            {
                "username": username.strip(),
                "email": email.strip(),
                "password": password,
            }
        )
    except ValidationError:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Перевірте ім’я користувача, email і пароль."},
            status_code=400,
        )

    async with AsyncSessionLocal() as db:
        existing_user = await db.scalar(
            select(User).where(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
        )

        if existing_user:
            return templates.TemplateResponse(
                request=request,
                name="register.html",
                context={"error": "Це ім’я користувача або email уже зайняті."},
                status_code=400,
            )

        user = User(
            username=user_data.username,
            email=str(user_data.email),
            hashed_password=hash_password(user_data.password),
            role="user",
        )

        db.add(user)
        await db.commit()

    return RedirectResponse(
        url="/login?registered=1",
        status_code=303,
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
            "registered": request.query_params.get("registered") == "1",
        },
    )


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(),
    password: str = Form(),
):
    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.username == username.strip()))

        if user is None or not verify_password(
            password,
            user.hashed_password,
        ):
            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "error": "Неправильне ім’я користувача або пароль.",
                    "registered": False,
                },
                status_code=401,
            )

        token = create_access_token(
            {
                "sub": str(user.id),
                "role": user.role,
                "token_version": user.token_version,
            }
        )

        destination = "/home/admin" if user.role == "admin" else "/home/user"

    response = RedirectResponse(
        url=destination,
        status_code=303,
    )

    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        **get_cookie_options(),
    )

    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        secure=not settings.debug,
        samesite="lax",
    )
    return response


@router.post("/vehicles/add")
async def add_vehicle_from_form(
    brand: str = Form(),
    model: str = Form(),
    license_plate: str = Form(),
    current_user: User = Depends(get_current_user),
):
    brand = brand.strip()
    model = model.strip()
    license_plate = license_plate.strip()

    if (
        not brand
        or not model
        or not license_plate
        or len(brand) > 100
        or len(model) > 100
        or len(license_plate) > 20
    ):
        return RedirectResponse(
            "/home/user?error=Перевірте поля форми",
            status_code=303,
        )

    async with AsyncSessionLocal() as db:
        vehicle = Vehicle(
            user_id=current_user.id,
            brand=brand,
            model=model,
            license_plate=license_plate,
            status="active",
        )

        db.add(vehicle)

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            return RedirectResponse(
                "/home/user?error=Такий номерний знак уже зареєстровано",
                status_code=303,
            )

    return RedirectResponse(
        "/home/user?message=Автомобіль успішно додано",
        status_code=303,
    )


@router.post("/vehicles/{vehicle_id}/status")
async def update_vehicle_status_from_form(
    vehicle_id: int,
    status: str = Form(),
    current_user: User = Depends(get_current_user),
):
    if status not in {"active", "inactive"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid vehicle status",
        )

    async with AsyncSessionLocal() as db:
        vehicle = await db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id))

        if vehicle is None:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found",
            )

        if vehicle.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this vehicle",
            )

        vehicle.status = status
        await db.commit()

    return RedirectResponse(
        "/home/user?message=Статус автомобіля оновлено",
        status_code=303,
    )


@router.post("/vehicles/{vehicle_id}/delete")
async def delete_vehicle_from_form(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
):
    async with AsyncSessionLocal() as db:
        vehicle = await db.scalar(select(Vehicle).where(Vehicle.id == vehicle_id))

        if vehicle is None:
            return RedirectResponse(
                "/home/user?error=Автомобіль не знайдено",
                status_code=303,
            )

        if vehicle.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this vehicle",
            )

        await db.delete(vehicle)
        await db.commit()

    return RedirectResponse(
        "/home/user?message=Автомобіль успішно видалено",
        status_code=303,
    )


@router.post("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str = Form(),
    current_user: User = Depends(require_admin),
):
    if role not in {"user", "admin"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid user role",
        )

    if user_id == current_user.id:
        return RedirectResponse(
            "/home/admin?error=Не можна змінювати власну роль",
            status_code=303,
        )

    async with AsyncSessionLocal() as db:
        user = await db.scalar(select(User).where(User.id == user_id))

        if user is None:
            return RedirectResponse(
                "/home/admin?error=Користувача не знайдено",
                status_code=303,
            )

        if user.role == role:
            return RedirectResponse(
                "/home/admin?message=Роль не змінилася",
                status_code=303,
            )

        user.role = role
        user.token_version += 1

        await db.commit()

    return RedirectResponse(
        "/home/admin?message=Роль користувача успішно змінено",
        status_code=303,
    )
