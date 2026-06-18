from typing import Optional
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Float
)
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = "companies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_name = Column(Text, nullable=False)
    subscription_plan = Column(Text, nullable=False, default="starter")
    credits = Column(Float, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(Text, nullable=False, default="AGENT")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    company = relationship("Company", back_populates="users")

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    dataset_name = Column(Text, nullable=False)
    uploaded_file_name = Column(Text)
    column_map = Column(JSON, nullable=True)  # list/dict of detected columns
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CustomerRecord(Base):
    __tablename__ = "customer_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    phone = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    dynamic_fields = Column(JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Template(Base):
    __tablename__ = "templates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    template_name = Column(Text, nullable=False)
    channel = Column(Text, nullable=False)  # 'whatsapp' or 'email'
    template_content = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False)
    campaign_name = Column(Text, nullable=False)
    status = Column(Text, nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    customer_record_id = Column(UUID(as_uuid=True), ForeignKey("customer_records.id"), nullable=False)
    channel = Column(Text, nullable=False)
    generated_message = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="queued")  # queued, sending, sent, delivered, read, failed
    provider_message_id = Column(Text, nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Reply(Base):
    __tablename__ = "replies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    customer_record_id = Column(UUID(as_uuid=True), ForeignKey("customer_records.id"), nullable=True)
    message_text = Column(Text, nullable=False)
    provider_event = Column(JSON, nullable=True)
    received_at = Column(DateTime(timezone=True), server_default=func.now())

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    credits_added = Column(Float, nullable=True, default=0)
    credits_used = Column(Float, nullable=True, default=0)
    balance_after = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
