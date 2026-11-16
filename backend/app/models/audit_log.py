"""Audit logging and resume file storage metadata models."""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    """System audit trail for security-critical admin actions and allocation decisions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    target_type = Column(String(100), nullable=True)  # e.g., 'INTERNSHIP', 'ALLOCATION', 'APPLICATION'
    target_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action='{self.action}' user_id={self.user_id}>"


class ResumeFile(Base):
    """Uploaded PDF resume documents with extraction metadata."""
    __tablename__ = "resume_files"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    stored_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    extracted_text = Column(Text, nullable=True)
    parsing_status = Column(String(50), default="PENDING", nullable=False)  # PENDING, PROCESSED, FAILED
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship
    student_profile = relationship("StudentProfile", back_populates="resume_files")

    def __repr__(self) -> str:
        return f"<ResumeFile id={self.id} student_id={self.student_profile_id} filename='{self.original_filename}'>"
