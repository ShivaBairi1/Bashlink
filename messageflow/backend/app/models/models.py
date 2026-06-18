@@
 class Template(Base):
     __tablename__ = "templates"
     id = Column(UUID(as_uuid=True), primary_key=True, default=gen_uuid)
     company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
     template_name = Column(Text, nullable=False)
+    template_version = Column(Text, nullable=True)
     channel = Column(Text, nullable=False)  # 'whatsapp' or 'email'
     template_content = Column(Text, nullable=False)
     status = Column(Text, nullable=False, default="active")
     created_at = Column(DateTime(timezone=True), server_default=func.now())
