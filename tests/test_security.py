from app.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "secret123"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrong-password", hashed_password)


def test_password_hashes_are_different():
    password = "secret123"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert verify_password(password, first_hash)
    assert verify_password(password, second_hash)


def test_create_access_token():
    data = {
        "sub": "1",
        "role": "user",
    }

    token = create_access_token(data)

    assert isinstance(token, str)
    assert len(token) > 0
