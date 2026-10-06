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


def test_user_cannot_access_admin_panel(client, test_users):
    user = test_users["user1"]

    token = get_token(
        client,
        user["username"],
        user["password"],
    )

    response = client.get(
        "/users/admin",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_user_cannot_modify_another_users_vehicle(client, test_users, test_vehicle):
    user2 = test_users["user2"]

    token = get_token(
        client,
        user2["username"],
        user2["password"],
    )

    response = client.patch(
        f"/vehicles/{test_vehicle['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "inactive",
        },
    )

    assert response.status_code == 403
