from app.models.base import Base
from app.models.user import User
from app.models.income import Income
from app.models.expense import Expense
from app.models.transaction import Transaction

# Re-export metadata for Alembic
target_metadata = Base.metadata
