"""add rate_limit to whatsapp_configs

Revision ID: 0004_add_whatsapp_rate_limit
Revises: 0003_add_phone_idempotency
Create Date: 2026-06-18 01:02:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0004_add_whatsapp_rate_limit'
down_revision = '0003_add_phone_idempotency'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('whatsapp_configs', sa.Column('rate_limit', sa.Float(), nullable=True))


def downgrade():
    op.drop_column('whatsapp_configs', 'rate_limit')
