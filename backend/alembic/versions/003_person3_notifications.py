"""003_person3_notifications

Revision ID: 003_person3_notifications
Revises: 002_person3_investments
Create Date: 2026-10-06 13:05:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_person3_notifications'
down_revision: Union[str, None] = '002_person3_investments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('userId', sa.String(length=64), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.String(length=1024), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('createdAt', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['userId'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_userId'), 'notifications', ['userId'], unique=False)
    op.create_index(op.f('ix_notifications_read'), 'notifications', ['read'], unique=False)
    op.create_index(op.f('ix_notifications_createdAt'), 'notifications', ['createdAt'], unique=False)
    op.create_index('idx_notification_user_created', 'notifications', ['userId', 'createdAt'], unique=False)
    op.create_index('idx_notification_user_read', 'notifications', ['userId', 'read'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_notification_user_read', table_name='notifications')
    op.drop_index('idx_notification_user_created', table_name='notifications')
    op.drop_index(op.f('ix_notifications_createdAt'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_read'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_userId'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
