from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.database import AsyncSessionLocal
from app.main import app
from app.models.user import User
from app.models.vehicle import Vehicle


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_users(client):
    unique_id = uuid4().hex[:8]

    user1 = {
        "username": f"testuser_{unique_id}",
        "email": f"testuser_{unique_id}@example.com",
        "password": "123",
    }

    user2 = {
        "username": f"user2_{unique_id}",
        "email": f"user2_{unique_id}@example.com",
        "password": "1234",
    }

    for user in (user1, user2):
        response = client.post("/auth/register", json=user)
        assert response.status_code == 201

    yield {"user1": user1, "user2": user2}

    usernames = [user1["username"], user2["username"]]

    async def cleanup_test_data():
        async with AsyncSessionLocal() as session:
            user_ids = select(User.id).where(User.username.in_(usernames))

            await session.execute(delete(Vehicle).where(Vehicle.user_id.in_(user_ids)))

            await session.execute(delete(User).where(User.username.in_(usernames)))

            await session.commit()

    client.portal.call(cleanup_test_data)


@pytest.fixture
def test_vehicle(client, test_users):
    response = client.post(
        "/auth/login",
        json={
            "username": test_users["user1"]["username"],
            "password": test_users["user1"]["password"],
        },
    )
    assert response.status_code == 200

    token = response.json()["access_token"]

    unique_id = uuid4().hex[:8]

    response = client.post(
        "/vehicles",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "brand": "Toyota",
            "model": "Camry",
            "license_plate": f"TEST-{unique_id}",
        },
    )

    assert response.status_code == 201

    return response.json()
