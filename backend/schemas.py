from pydantic import BaseModel
from typing import Optional


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TransactionCreate(BaseModel):
    transaction_type: str
    category: str
    amount: float


class BudgetCreate(BaseModel):
    category: str
    amount: float


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: Optional[float] = 0