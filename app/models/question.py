from sqlalchemy import Column, Integer, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_number = Column(Integer, unique=True, nullable=True, index=True)
    text = Column(Text, nullable=False)
    reference_answer = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)

    # Relationships
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

