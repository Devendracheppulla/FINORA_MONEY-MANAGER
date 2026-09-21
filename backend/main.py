from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)


# =====================================================
# DATABASE
# =====================================================

models.Base.metadata.create_all(bind=engine)


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(title="FINORA API")


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# AUTHENTICATION
# =====================================================

def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token."
        )

    token = authorization.replace("Bearer ", "", 1)

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token."
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token."
        )

    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID in token."
        )

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found."
        )

    return user


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():
    return {
        "message": "FINORA backend is running"
    }


# =====================================================
# REGISTER
# =====================================================

@app.post("/register")
def register(
    data: schemas.RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(models.User)
        .filter(models.User.email == data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    user = models.User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration successful",
        "user_id": user.id
    }


# =====================================================
# LOGIN
# =====================================================

@app.post("/login")
def login(
    data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(models.User)
        .filter(models.User.email == data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(
        data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": token,
        "user_id": user.id,
        "name": user.name,
        "email": user.email
    }


# =====================================================
# ADD TRANSACTION
# =====================================================

@app.post("/transactions")
def add_transaction(
    data: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transaction = models.Transaction(
        user_id=current_user.id,
        transaction_type=data.transaction_type,
        category=data.category,
        amount=data.amount
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {
        "message": "Transaction added successfully",
        "transaction": {
            "id": transaction.id,
            "type": transaction.transaction_type,
            "category": transaction.category,
            "amount": transaction.amount
        }
    }


# =====================================================
# GET CURRENT USER TRANSACTIONS
# =====================================================

@app.get("/transactions")
def get_transactions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == current_user.id
        )
        .order_by(models.Transaction.id.desc())
        .all()
    )

    return [
        {
            "id": transaction.id,
            "type": transaction.transaction_type,
            "category": transaction.category,
            "amount": transaction.amount,
            "created_at": transaction.created_at
        }
        for transaction in transactions
    ]


# =====================================================
# DASHBOARD
# =====================================================

@app.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    transactions = (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == current_user.id
        )
        .all()
    )

    total_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "income"
    )

    total_expense = sum(
        transaction.amount
        for transaction in transactions
        if transaction.transaction_type == "expense"
    )

    balance = total_income - total_expense

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "transaction_count": len(transactions)
    }