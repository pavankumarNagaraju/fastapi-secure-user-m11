from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, model_validator


# =========================
# User Schemas
# =========================

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int
    created_at: datetime

    # Pydantic v2: from_orm -> from_attributes
    model_config = ConfigDict(from_attributes=True)


# =========================
# Calculation Schemas
# =========================

class CalculationType(str, Enum):
    add = "add"
    sub = "sub"
    multiply = "multiply"
    divide = "divide"


class CalculationBase(BaseModel):
    a: float
    b: float
    type: CalculationType


class CalculationCreate(CalculationBase):
    @model_validator(mode="after")
    def check_zero_division(self):
        # At this point, self.type is a CalculationType and self.b is a float
        if self.type == CalculationType.divide and self.b == 0:
            raise ValueError("Division by zero is not allowed.")
        return self


class CalculationRead(CalculationBase):
    id: int
    result: Optional[float] = None
    user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
