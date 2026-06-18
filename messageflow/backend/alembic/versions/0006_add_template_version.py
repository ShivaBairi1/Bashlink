"""add template_version to templates

Revision ID: 0006_add_template_version
Revises: 0005_add_whatsapp_concurrency_and_analytics
Create Date: 2026-06-18 01:25:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '0006_add_template_version'
down_revision = '0005_add_whatsapp_concurrency_and_analytics'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('templates', sa.Column('template_version', sa.String(length=64), nullable=True))


def downgrade():
    op.drop_column('templates', 'template_version')
