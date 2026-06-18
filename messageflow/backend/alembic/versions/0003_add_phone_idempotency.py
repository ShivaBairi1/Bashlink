"""add normalized_phone and idempotency index

Revision ID: 0003_add_phone_idempotency
Revises: 0002_add_provider_and_tokens
Create Date: 2026-06-18 00:45:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '0003_add_phone_idempotency'
down_revision = '0002_add_provider_and_tokens'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('customer_records', sa.Column('normalized_phone', sa.Text(), nullable=True))
    op.create_index('ix_customer_records_normalized_phone', 'customer_records', ['normalized_phone'])
    op.add_column('messages', sa.Column('idempotency_key', sa.Text(), nullable=True))
    op.create_unique_constraint('uq_messages_idempotency_key', 'messages', ['idempotency_key'])


def downgrade():
    op.drop_constraint('uq_messages_idempotency_key', 'messages', type_='unique')
    op.drop_column('messages', 'idempotency_key')
    op.drop_index('ix_customer_records_normalized_phone', table_name='customer_records')
    op.drop_column('customer_records', 'normalized_phone')
