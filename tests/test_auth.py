def test_login_success(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
