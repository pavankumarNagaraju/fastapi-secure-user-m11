from app.auth import hash_password, verify_password


def test_hash_password_produces_different_value():
    plain = "mysecretpassword"
    hashed = hash_password(plain)

    assert hashed != plain
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_verify_password_success():
    plain = "anothersecret"
    hashed = hash_password(plain)

    assert verify_password(plain, hashed) is True


def test_verify_password_failure():
    plain = "correct"
    wrong = "incorrect"
    hashed = hash_password(plain)

    assert verify_password(wrong, hashed) is False
