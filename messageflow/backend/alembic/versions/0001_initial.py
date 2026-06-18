"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-06-18 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('companies',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_name', sa.Text(), nullable=False),
        sa.Column('subscription_plan', sa.Text(), nullable=False, server_default='starter'),
        sa.Column('credits', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('users',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('role', sa.Text(), nullable=False, server_default='AGENT'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_table('datasets',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dataset_name', sa.Text(), nullable=False),
        sa.Column('uploaded_file_name', sa.Text()),
        sa.Column('column_map', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('customer_records',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dataset_id', pg.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('phone', sa.Text(), nullable=True),
        sa.Column('email', sa.Text(), nullable=True),
        sa.Column('dynamic_fields', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('templates',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('template_name', sa.Text(), nullable=False),
        sa.Column('channel', sa.Text(), nullable=False),
        sa.Column('template_content', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False, server_default='active'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('campaigns',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('dataset_id', pg.UUID(as_uuid=True), sa.ForeignKey('datasets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('template_id', pg.UUID(as_uuid=True), sa.ForeignKey('templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_name', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('messages',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('campaign_id', pg.UUID(as_uuid=True), sa.ForeignKey('campaigns.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_record_id', pg.UUID(as_uuid=True), sa.ForeignKey('customer_records.id', ondelete='CASCADE'), nullable=False),
        sa.Column('channel', sa.Text(), nullable=False),
        sa.Column('generated_message', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False, server_default='queued'),
        sa.Column('provider_message_id', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('replies',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_record_id', pg.UUID(as_uuid=True), sa.ForeignKey('customer_records.id', ondelete='CASCADE'), nullable=True),
        sa.Column('message_text', sa.Text(), nullable=False),
        sa.Column('provider_event', sa.JSON(), nullable=True),
        sa.Column('received_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )
    op.create_table('credit_transactions',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', pg.UUID(as_uuid=True), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('credits_added', sa.Float(), nullable=True, server_default='0'),
        sa.Column('credits_used', sa.Float(), nullable=True, server_default='0'),
        sa.Column('balance_after', sa.Float(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'))
    )

def downgrade():
    op.drop_table('credit_transactions')
    op.drop_table('replies')
    op.drop_table('messages')
    op.drop_table('campaigns')
    op.drop_table('templates')
    op.drop_table('customer_records')
    op.drop_table('datasets')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_table('companies')
