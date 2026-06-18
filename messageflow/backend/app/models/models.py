@@
 class CreditTransaction(Base):
@@
     created_at = Column(DateTime(timezone=True), server_default=func.now())
+
+
+class WhatsAppConfig(Base):
+    __tablename__ = "whatsapp_configs"
+    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
+    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
+    phone_number_id = Column(Text, nullable=False)
+    access_token = Column(Text, nullable=False)
+    created_at = Column(DateTime(timezone=True), server_default=func.now())
+
+
+class ProviderFailedMessage(Base):
+    __tablename__ = "provider_failed_messages"
+    id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
+    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
+    message_id = Column(UUID(as_uuid=True), nullable=True)
+    channel = Column(Text, nullable=False)
+    payload = Column(JSON, nullable=True)
+    error = Column(Text, nullable=True)
+    created_at = Column(DateTime(timezone=True), server_default=func.now())
