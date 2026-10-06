def test_login_success(client, test_users):
    user = test_users["user1"]

    response = client.post(
        "/auth/login",
        json={
            "username": user["username"],
            "password": user["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_users):
    user = test_users["user1"]

    response = client.post(
        "/auth/login",
        json={
            "username": user["username"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
