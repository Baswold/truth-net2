"""Initial schema with all tables, indexes, and constraints.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-10-13 13:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create member table
    op.create_table(
        'member',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=320), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=120), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('roles', sa.String(length=120), nullable=False),
        sa.Column('trust_score', sa.Integer(), nullable=False),
        sa.Column('strike_count', sa.Integer(), nullable=False),
        sa.Column('public_key', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('timezone', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_member_email', 'member', ['email'], unique=True)
    op.create_index('ix_member_username', 'member', ['username'], unique=True)

    # Create site table
    op.create_table(
        'site',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=120), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('theme', sa.String(length=64), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('feature_flags', sa.JSON(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('primary_language', sa.String(length=8), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['member.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_site_slug', 'site', ['slug'], unique=True)
    op.create_index('ix_site_status', 'site', ['status'])
    op.create_index('ix_site_created_at', 'site', ['created_at'])
    # GIN index for tags JSONB search (PostgreSQL specific)
    op.execute('CREATE INDEX IF NOT EXISTS ix_site_tags_gin ON site USING GIN (tags)')

    # Create page table
    op.create_table(
        'page',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('path', sa.String(length=512), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('layout_json', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('live_version_id', sa.Integer(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('site_id', 'path', name='uq_page_site_path')
    )
    op.create_index('ix_page_status', 'page', ['status'])
    op.create_index('ix_page_created_at', 'page', ['created_at'])
    op.execute('CREATE INDEX IF NOT EXISTS ix_page_metadata_gin ON page USING GIN (metadata)')

    # Create content_version table
    op.create_table(
        'content_version',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('layout_json', sa.JSON(), nullable=False),
        sa.Column('editor_id', sa.Integer(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('change_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['editor_id'], ['member.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['page_id'], ['page.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_content_version_page_id', 'content_version', ['page_id'])

    # Create fact_check_run table
    op.create_table(
        'fact_check_run',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=32), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('primary_checker_result', sa.JSON(), nullable=False),
        sa.Column('auditor_checker_result', sa.JSON(), nullable=False),
        sa.Column('agreement_score', sa.Float(), nullable=True),
        sa.Column('final_verdict', sa.String(length=64), nullable=True),
        sa.Column('web_search_queries', sa.JSON(), nullable=False),
        sa.Column('web_search_results', sa.JSON(), nullable=False),
        sa.Column('curator_reviewed', sa.Boolean(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reviewer_id'], ['member.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_fact_check_run_target', 'fact_check_run', ['target_type', 'target_id'])
    op.create_index('ix_fact_check_run_curator_reviewed', 'fact_check_run', ['curator_reviewed'])

    # Create truth_assertion table
    op.create_table(
        'truth_assertion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('page_id', sa.Integer(), nullable=False),
        sa.Column('claim_text', sa.Text(), nullable=False),
        sa.Column('verdict', sa.String(length=64), nullable=False),
        sa.Column('citation', sa.Text(), nullable=True),
        sa.Column('fact_check_run_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['fact_check_run_id'], ['fact_check_run.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['page_id'], ['page.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_truth_assertion_page_id', 'truth_assertion', ['page_id'])

    # Create truth_post table
    op.create_table(
        'truth_post',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(length=32), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('citations', sa.JSON(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('published', sa.Boolean(), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('trust_score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['member.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_truth_post_published', 'truth_post', ['published'])
    op.create_index('ix_truth_post_created_at', 'truth_post', ['created_at'])
    op.create_index('ix_truth_post_trust_score', 'truth_post', ['trust_score'])
    op.execute('CREATE INDEX IF NOT EXISTS ix_truth_post_tags_gin ON truth_post USING GIN (tags)')

    # Create truth_thread table
    op.create_table(
        'truth_thread',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('topic', sa.String(length=120), nullable=True),
        sa.Column('locked', sa.Boolean(), nullable=False),
        sa.Column('trust_score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['member.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['truth_post.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_truth_thread_created_at', 'truth_thread', ['created_at'])
    op.create_index('ix_truth_thread_topic', 'truth_thread', ['topic'])

    # Create thread_comment table
    op.create_table(
        'thread_comment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('thread_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('citations', sa.JSON(), nullable=False),
        sa.Column('trust_score', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['member.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['thread_comment.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['thread_id'], ['truth_thread.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_thread_comment_thread_id', 'thread_comment', ['thread_id'])
    op.create_index('ix_thread_comment_created_at', 'thread_comment', ['created_at'])

    # Create reaction table
    op.create_table(
        'reaction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('comment_id', sa.Integer(), nullable=True),
        sa.Column('reaction_type', sa.String(length=32), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['comment_id'], ['thread_comment.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['member_id'], ['member.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['truth_post.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reaction_post_id', 'reaction', ['post_id'])
    op.create_index('ix_reaction_comment_id', 'reaction', ['comment_id'])

    # Create follow table
    op.create_table(
        'follow',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('following_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['follower_id'], ['member.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['following_id'], ['member.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('follower_id', 'following_id', name='uq_follow_follower_following')
    )

    # Create community_verdict table
    op.create_table(
        'community_verdict',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(length=32), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=False),
        sa.Column('verdict', sa.String(length=64), nullable=False),
        sa.Column('vote_count', sa.Integer(), nullable=False),
        sa.Column('curator_approved', sa.Boolean(), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_community_verdict_target', 'community_verdict', ['target_type', 'target_id'])

    # Create import_source table
    op.create_table(
        'import_source',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('original_url', sa.Text(), nullable=False),
        sa.Column('snapshot_path', sa.String(length=512), nullable=True),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.Column('refresh_interval_hours', sa.Integer(), nullable=True),
        sa.Column('last_refresh_at', sa.DateTime(), nullable=True),
        sa.Column('next_refresh_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('import_metadata', sa.JSON(), nullable=False),
        sa.Column('submitted_by', sa.Integer(), nullable=True),
        sa.Column('page_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['page_id'], ['page.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submitted_by'], ['member.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_import_source_status', 'import_source', ['status'])
    op.create_index('ix_import_source_next_refresh', 'import_source', ['next_refresh_at'])

    # Create site_membership table
    op.create_table(
        'site_membership',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['member_id'], ['member.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['site_id'], ['site.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('site_id', 'member_id', name='uq_site_membership_site_member')
    )

    # Create feature_toggle table
    op.create_table(
        'feature_toggle',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scope', sa.String(length=32), nullable=False),
        sa.Column('scope_id', sa.Integer(), nullable=True),
        sa.Column('key', sa.String(length=120), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('value_type', sa.String(length=32), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['updated_by'], ['member.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_feature_toggle_scope', 'feature_toggle', ['scope', 'scope_id'])

    # Create submission table
    op.create_table(
        'submission',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_type', sa.String(length=32), nullable=False),
        sa.Column('submitted_by', sa.Integer(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('state', sa.String(length=32), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['submitted_by'], ['member.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_submission_state', 'submission', ['state'])
    op.create_index('ix_submission_created_at', 'submission', ['created_at'])

    # Create review_action table
    op.create_table(
        'review_action',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('submission_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('decision', sa.String(length=32), nullable=False),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('penalties', sa.JSON(), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['reviewer_id'], ['member.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['submission_id'], ['submission.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_review_action_submission_id', 'review_action', ['submission_id'])

    # Create penalty_ledger table
    op.create_table(
        'penalty_ledger',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.Column('penalty_type', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('issued_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['issued_by'], ['member.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['member_id'], ['member.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_penalty_ledger_member_id', 'penalty_ledger', ['member_id'])
    op.create_index('ix_penalty_ledger_resolved', 'penalty_ledger', ['resolved'])

    # Create audit_log table
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=120), nullable=False),
        sa.Column('target_type', sa.String(length=32), nullable=True),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('ip_address', sa.String(length=64), nullable=True),
        sa.Column('user_agent', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['actor_id'], ['member.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_log_created_at', 'audit_log', ['created_at'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])


def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('penalty_ledger')
    op.drop_table('review_action')
    op.drop_table('submission')
    op.drop_table('feature_toggle')
    op.drop_table('site_membership')
    op.drop_table('import_source')
    op.drop_table('community_verdict')
    op.drop_table('follow')
    op.drop_table('reaction')
    op.drop_table('thread_comment')
    op.drop_table('truth_thread')
    op.drop_table('truth_post')
    op.drop_table('truth_assertion')
    op.drop_table('fact_check_run')
    op.drop_table('content_version')
    op.drop_table('page')
    op.drop_table('site')
    op.drop_table('member')
