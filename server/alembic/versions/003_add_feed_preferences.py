"""Add feed preferences table for personalized feeds.

Revision ID: 003_add_feed_preferences
Revises: 002_add_constraints
Create Date: 2025-10-13 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_add_feed_preferences'
down_revision: Union[str, None] = '002_add_constraints'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create feed_preference table
    op.create_table(
        'feed_preference',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('parsed_filters', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('last_applied_at', sa.DateTime(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['member_id'], ['member.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('member_id', name='uq_feed_preference_member_id')
    )
    
    # Create index for efficient lookups
    op.create_index('ix_feed_preference_member_id', 'feed_preference', ['member_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_feed_preference_member_id', table_name='feed_preference')
    op.drop_table('feed_preference')
