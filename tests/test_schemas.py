import pytest
from pydantic import ValidationError

from app.schemas import UserCreate, UserRead


def test_usercreate_valid_data():
    data = {
        "username": "pavan",
        "email": "pavan@example.com",
        "password": "secret123",
    }

    user = UserCreate(**data)

    assert user.username == "pavan"
    assert user.email == "pavan@example.com"
    assert user.password == "secret123"


def test_usercreate_invalid_email_raises_validationerror():
    data = {
        "username": "pavan",
        "email": "not-an-email",
        "password": "secret123",
    }

    with pytest.raises(ValidationError):
        UserCreate(**data)


def test_userread_orm_mode_from_orm_object():
    from datetime import datetime, timezone

    class FakeUser:
        def __init__(self, id, username, email, created_at):
            self.id = id
            self.username = username
            self.email = email
            self.created_at = created_at

    fake = FakeUser(
        id=1,
        username="pavan",
        email="pavan@example.com",
        created_at=datetime.now(timezone.utc),
    )

    # Pydantic v2: use model_validate when from_attributes=True
    user_read = UserRead.model_validate(fake)

    assert user_read.id == 1
    assert user_read.username == "pavan"
    assert user_read.email == "pavan@example.com"
