"""create whatsapp concurrency column and analytics_aggregates table

Revision ID: 0005_add_whatsapp_concurrency_and_analytics
Revises: 0004_add_whatsapp_rate_limit
Create Date: 2026-06-18 01:10:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0005_add_whatsapp_concurrency_and_analytics'
down_revision = '0004_add_whatsapp_rate_limit'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('whatsapp_configs', sa.Column('concurrency', sa.Integer(), nullable=True))
    op.create_table(
        'analytics_aggregates',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('company_id', sa.UUID(as_uuid=True), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delivered_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )


def downgrade():
    op.drop_table('analytics_aggregates')
    op.drop_column('whatsapp_configs', 'concurrency')
