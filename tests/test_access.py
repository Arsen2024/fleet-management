def get_token(client, username, password):
    response = client.post(
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_anonymous_access_to_profile(client):
    response = client.get("/users/me")

    assert response.status_code == 401


def test_user_cannot_access_admin_panel(client):
    token = get_token(
        client,
        "testuser",
        "123",
    )

    response = client.get(
        "/users/admin",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_user_cannot_modify_another_users_vehicle(client):
    token = get_token(
        client,
        "user2",
        "1234",
    )

    response = client.patch(
        "/vehicles/1/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "inactive",
        },
    )

    assert response.status_code == 403
