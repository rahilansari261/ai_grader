from sqlalchemy import Column, Integer, Text, ForeignKey, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db import Base


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    student_answer = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    similarity = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    evaluation = Column(JSON, nullable=True)
    isCorrect = Column(Boolean, nullable=True)

    # Relationships
    question = relationship("Question", back_populates="answers")

