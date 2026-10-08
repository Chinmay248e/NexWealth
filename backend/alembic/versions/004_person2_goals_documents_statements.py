"""004_person2_goals_documents_statements

Revision ID: 004_person2_init
Revises: 003_person3_notifications
Create Date: 2026-10-08 04:40:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '004_person2_init'
down_revision: Union[str, None] = '003_person3_notifications'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create 'goals' table
    op.create_table(
        'goals',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('targetAmount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('currentAmount', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('targetDate', sa.Date(), nullable=False),
        sa.Column('monthlyContribution', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('"targetAmount" > 0', name='check_positive_target_amount'),
        sa.CheckConstraint('"currentAmount" >= 0', name='check_non_negative_current_amount'),
        sa.CheckConstraint('"monthlyContribution" >= 0', name='check_non_negative_monthly_contribution'),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goals_id'), 'goals', ['id'], unique=False)
    op.create_index(op.f('ix_goals_userId'), 'goals', ['userId'], unique=False)
    op.create_index(op.f('ix_goals_targetDate'), 'goals', ['targetDate'], unique=False)
    op.create_index('idx_goal_user_target_date', 'goals', ['userId', 'targetDate'], unique=False)

    # 2. Create 'documents' table
    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('fileName', sa.String(length=255), nullable=False),
        sa.Column('documentType', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='uploaded'),
        sa.Column('uploadedAt', sa.DateTime(timezone=True), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_userId'), 'documents', ['userId'], unique=False)
    op.create_index(op.f('ix_documents_documentType'), 'documents', ['documentType'], unique=False)
    op.create_index(op.f('ix_documents_uploadedAt'), 'documents', ['uploadedAt'], unique=False)
    op.create_index('idx_document_user_date', 'documents', ['userId', 'uploadedAt'], unique=False)

    # 3. Create 'bank_statements' table
    op.create_table(
        'bank_statements',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('fileName', sa.String(length=255), nullable=False),
        sa.Column('accountName', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='uploaded'),
        sa.Column('uploadedAt', sa.DateTime(timezone=True), nullable=False),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_statements_id'), 'bank_statements', ['id'], unique=False)
    op.create_index(op.f('ix_bank_statements_userId'), 'bank_statements', ['userId'], unique=False)
    op.create_index(op.f('ix_bank_statements_uploadedAt'), 'bank_statements', ['uploadedAt'], unique=False)
    op.create_index('idx_statement_user_date', 'bank_statements', ['userId', 'uploadedAt'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_statement_user_date', table_name='bank_statements')
    op.drop_index(op.f('ix_bank_statements_uploadedAt'), table_name='bank_statements')
    op.drop_index(op.f('ix_bank_statements_userId'), table_name='bank_statements')
    op.drop_index(op.f('ix_bank_statements_id'), table_name='bank_statements')
    op.drop_table('bank_statements')

    op.drop_index('idx_document_user_date', table_name='documents')
    op.drop_index(op.f('ix_documents_uploadedAt'), table_name='documents')
    op.drop_index(op.f('ix_documents_documentType'), table_name='documents')
    op.drop_index(op.f('ix_documents_userId'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')

    op.drop_index('idx_goal_user_target_date', table_name='goals')
    op.drop_index(op.f('ix_goals_targetDate'), table_name='goals')
    op.drop_index(op.f('ix_goals_userId'), table_name='goals')
    op.drop_index(op.f('ix_goals_id'), table_name='goals')
    op.drop_table('goals')
