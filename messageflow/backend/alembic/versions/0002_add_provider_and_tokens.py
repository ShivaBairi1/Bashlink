"""add whatsapp_configs and provider_failed_messages tables

Revision ID: 0002_add_provider_and_tokens
Revises: 0001_initial
Create Date: 2026-06-18 00:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '0002_add_provider_and_tokens'
down_revision = '0001_initial'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('whatsapp_configs',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('phone_number_id', sa.Text(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('provider_failed_messages',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('message_id', pg.UUID(as_uuid=True), nullable=True),
        sa.Column('channel', sa.Text(), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )


def downgrade():
    op.drop_table('provider_failed_messages')
    op.drop_table('whatsapp_configs')
