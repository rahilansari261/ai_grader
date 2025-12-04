from sqlalchemy import Column, Integer, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db import Base


class Rubric(Base):
    __tablename__ = "rubrics"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    criterion = Column(Text, nullable=False)
    weight = Column(Float, nullable=False, default=1.0)

    # Relationships
    question = relationship("Question", back_populates="rubrics")

