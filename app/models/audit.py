from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    endpoint = Column(String(200), nullable=True)
    ip_address = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_logs")

class Notification(BaseModel):
    __tablename__ = "notifications"

    recipient_user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(String(10), default="FALSE")

class Document(BaseModel):
    __tablename__ = "documents"

    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(36), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)
