from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.api.auth import auth_router
from app.api.incomes import income_router
from app.api.expenses import expense_router
from app.api.transactions import transaction_router
from app.api.dashboard import dashboard_router
from app.api.investments import investment_router
from app.api.analytics import analytics_router
from app.api.profile import profile_router
from app.api.notifications import notification_router

api_router = APIRouter()

# Mount authentication endpoints under /auth
api_router.include_router(auth_router)

# Mount income CRUD endpoints under /incomes
api_router.include_router(income_router)

# Mount expense CRUD endpoints under /expenses
api_router.include_router(expense_router)

# Mount read-only transaction endpoints under /transactions
api_router.include_router(transaction_router)

# Mount dashboard endpoints under /dashboard
api_router.include_router(dashboard_router)

# Mount investment CRUD endpoints under /investments (Person 3)
api_router.include_router(investment_router)

# Mount analytics endpoints under /analytics (Person 3)
api_router.include_router(analytics_router)

# Mount user profile endpoints under /profile (Person 3)
api_router.include_router(profile_router)

# Mount notification endpoints under /notifications (Person 3)
api_router.include_router(notification_router)

@api_router.get("/health", tags=["System"])
def health_check():
    """System Health and Version Check."""
    return {
        "status": "healthy",
        "service": "NexWealth API",
        "version": "1.0.0",
        "currency": "INR (₹)",
        "contract": "NEXWEALTH_DATA_CONTRACT.md synced",
    }

@api_router.get("/health/db", tags=["System"])
def db_health_check(db: Session = Depends(get_db)):
    """Verifies live connectivity to the PostgreSQL database."""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        return {
            "status": "connected",
            "database": "PostgreSQL",
            "test_query_result": result,
            "message": "Successfully connected to PostgreSQL database 'nexwealth'",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PostgreSQL connection error: {str(e)}",
        )

@api_router.get("/contract-info", tags=["System"])
def get_contract_info():
    """Information on data contract ownership division."""
    return {
        "contract": "NEXWEALTH_DATA_CONTRACT.md",
        "teamOwnership": {
            "Person 1": ["User", "Income", "Expense", "Transaction"],
            "Person 2": ["Goal", "Document", "BankStatement"],
            "Person 3": ["Investment", "Budget", "Notification"],
        },
    }
