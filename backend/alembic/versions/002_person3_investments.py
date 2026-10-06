"""002_person3_investments

Revision ID: 002_person3_investments
Revises: 001_person1_init
Create Date: 2026-10-06 12:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_person3_investments'
down_revision: Union[str, None] = '001_person1_init'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'investments',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('investedAmount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('currentValue', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('\"investedAmount\" > 0', name='check_positive_invested_amount'),
        sa.CheckConstraint('\"currentValue\" >= 0', name='check_non_negative_current_value'),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_investments_id'), 'investments', ['id'], unique=False)
    op.create_index(op.f('ix_investments_userId'), 'investments', ['userId'], unique=False)
    op.create_index(op.f('ix_investments_date'), 'investments', ['date'], unique=False)
    op.create_index('idx_investment_user_date', 'investments', ['userId', 'date'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_investment_user_date', table_name='investments')
    op.drop_index(op.f('ix_investments_date'), table_name='investments')
    op.drop_index(op.f('ix_investments_userId'), table_name='investments')
    op.drop_index(op.f('ix_investments_id'), table_name='investments')
    op.drop_table('investments')
