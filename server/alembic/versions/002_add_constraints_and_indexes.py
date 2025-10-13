"""Add unique constraints, foreign keys, and performance indexes.

Revision ID: 002_add_constraints
Revises: 001_initial_schema
Create Date: 2025-10-13 13:50:00.000000

This migration adds:
- Unique constraints for Page (site_id, path), Reaction, Follow, CommunityVerdict
- Foreign key for Page.live_version_id
- Performance indexes on status fields and foreign keys
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_constraints'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add indexes to site table
    op.create_index('ix_site_status', 'site', ['status'], unique=False)
    op.create_index('ix_site_owner_id', 'site', ['owner_id'], unique=False)
    
    # Add unique constraint and indexes to page table
    op.create_unique_constraint('uq_page_site_path', 'page', ['site_id', 'path'])
    op.create_index('ix_page_status', 'page', ['status'], unique=False)
    op.create_index('ix_page_site_id', 'page', ['site_id'], unique=False)
    
    # Add foreign key constraint for Page.live_version_id
    # Note: This may fail if existing data has invalid references
    # You may need to clean data first: UPDATE page SET live_version_id = NULL WHERE live_version_id NOT IN (SELECT id FROM content_version);
    op.create_foreign_key(
        'fk_page_live_version_id',
        'page', 'content_version',
        ['live_version_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Add indexes to truth_post table
    op.create_index('ix_truth_post_published', 'truth_post', ['published'], unique=False)
    op.create_index('ix_truth_post_author_id', 'truth_post', ['author_id'], unique=False)
    
    # Add unique constraints and indexes to reaction table
    op.create_unique_constraint(
        'uq_reaction_member_post_type',
        'reaction',
        ['member_id', 'post_id', 'reaction_type']
    )
    op.create_unique_constraint(
        'uq_reaction_member_comment_type',
        'reaction',
        ['member_id', 'comment_id', 'reaction_type']
    )
    op.create_index('ix_reaction_post_id', 'reaction', ['post_id'], unique=False)
    op.create_index('ix_reaction_comment_id', 'reaction', ['comment_id'], unique=False)
    
    # Add unique constraint and indexes to follow table
    op.create_unique_constraint(
        'uq_follow_follower_following',
        'follow',
        ['follower_id', 'following_id']
    )
    op.create_index('ix_follow_follower_id', 'follow', ['follower_id'], unique=False)
    op.create_index('ix_follow_following_id', 'follow', ['following_id'], unique=False)
    
    # Add unique constraint and index to community_verdict table
    op.create_unique_constraint(
        'uq_community_verdict_target',
        'community_verdict',
        ['target_type', 'target_id']
    )
    op.create_index(
        'ix_community_verdict_target',
        'community_verdict',
        ['target_type', 'target_id'],
        unique=False
    )


def downgrade() -> None:
    # Remove indexes and constraints in reverse order
    op.drop_index('ix_community_verdict_target', table_name='community_verdict')
    op.drop_constraint('uq_community_verdict_target', 'community_verdict', type_='unique')
    
    op.drop_index('ix_follow_following_id', table_name='follow')
    op.drop_index('ix_follow_follower_id', table_name='follow')
    op.drop_constraint('uq_follow_follower_following', 'follow', type_='unique')
    
    op.drop_index('ix_reaction_comment_id', table_name='reaction')
    op.drop_index('ix_reaction_post_id', table_name='reaction')
    op.drop_constraint('uq_reaction_member_comment_type', 'reaction', type_='unique')
    op.drop_constraint('uq_reaction_member_post_type', 'reaction', type_='unique')
    
    op.drop_index('ix_truth_post_author_id', table_name='truth_post')
    op.drop_index('ix_truth_post_published', table_name='truth_post')
    
    op.drop_constraint('fk_page_live_version_id', 'page', type_='foreignkey')
    
    op.drop_index('ix_page_site_id', table_name='page')
    op.drop_index('ix_page_status', table_name='page')
    op.drop_constraint('uq_page_site_path', 'page', type_='unique')
    
    op.drop_index('ix_site_owner_id', table_name='site')
    op.drop_index('ix_site_status', table_name='site')
