from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


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

    response = client.post(
        "/auth/register",
        json=user1,
    )
    assert response.status_code == 201

    response = client.post(
        "/auth/register",
        json=user2,
    )
    assert response.status_code == 201

    return {
        "user1": user1,
        "user2": user2,
    }


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
