"""001_person1_initial_schema

Revision ID: 001_person1_init
Revises: 
Create Date: 2026-10-06 09:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_person1_init'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create 'users' table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('passwordHash', sa.String(length=255), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Create 'incomes' table
    op.create_table(
        'incomes',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incomes_id'), 'incomes', ['id'], unique=False)
    op.create_index(op.f('ix_incomes_userId'), 'incomes', ['userId'], unique=False)
    op.create_index(op.f('ix_incomes_date'), 'incomes', ['date'], unique=False)
    op.create_index('idx_income_user_date', 'incomes', ['userId', 'date'], unique=False)

    # 3. Create 'expenses' table
    op.create_table(
        'expenses',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "category IN ('Food', 'Shopping', 'Transport', 'Bills', 'Entertainment', 'Education', 'Medical', 'Travel', 'Other')",
            name='check_valid_expense_category'
        ),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_expenses_id'), 'expenses', ['id'], unique=False)
    op.create_index(op.f('ix_expenses_userId'), 'expenses', ['userId'], unique=False)
    op.create_index(op.f('ix_expenses_category'), 'expenses', ['category'], unique=False)
    op.create_index(op.f('ix_expenses_date'), 'expenses', ['date'], unique=False)
    op.create_index('idx_expense_user_date', 'expenses', ['userId', 'date'], unique=False)
    op.create_index('idx_expense_user_category', 'expenses', ['userId', 'category'], unique=False)

    # 4. Create 'transactions' table
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('amount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('category', sa.String(length=64), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('source', sa.String(length=255), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("type IN ('income', 'expense')", name='check_valid_transaction_type'),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_userId'), 'transactions', ['userId'], unique=False)
    op.create_index(op.f('ix_transactions_type'), 'transactions', ['type'], unique=False)
    op.create_index(op.f('ix_transactions_date'), 'transactions', ['date'], unique=False)
    op.create_index('idx_transaction_user_date', 'transactions', ['userId', 'date'], unique=False)
    op.create_index('idx_transaction_user_type', 'transactions', ['userId', 'type'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_transaction_user_type', table_name='transactions')
    op.drop_index('idx_transaction_user_date', table_name='transactions')
    op.drop_index(op.f('ix_transactions_date'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_type'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_userId'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_table('transactions')

    op.drop_index('idx_expense_user_category', table_name='expenses')
    op.drop_index('idx_expense_user_date', table_name='expenses')
    op.drop_index(op.f('ix_expenses_date'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_category'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_userId'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_id'), table_name='expenses')
    op.drop_table('expenses')

    op.drop_index('idx_income_user_date', table_name='incomes')
    op.drop_index(op.f('ix_incomes_date'), table_name='incomes')
    op.drop_index(op.f('ix_incomes_userId'), table_name='incomes')
    op.drop_index(op.f('ix_incomes_id'), table_name='incomes')
    op.drop_table('incomes')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
