# app/models/student_answer.py
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class StudentAnswer(Base):
    __tablename__ = "student_answers"

    id                : Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    exam_id           : Mapped[int]           = mapped_column(Integer, ForeignKey("exams.id",               ondelete="CASCADE"), nullable=False, index=True)
    student_id        : Mapped[int]           = mapped_column(Integer, ForeignKey("students.id",            ondelete="CASCADE"), nullable=False, index=True)
    question_link_id  : Mapped[int]           = mapped_column(Integer, ForeignKey("exam_question_link.id", ondelete="CASCADE"), nullable=False)
    marked_label      : Mapped[Optional[str]] = mapped_column(String(1), nullable=True)
    is_correct        : Mapped[Optional[bool]]= mapped_column(Boolean,   nullable=True)
    scanned_at        : Mapped[datetime]      = mapped_column(DateTime,  default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", "question_link_id", name="uq_answer_per_question"),
    )
