from pydantic import BaseModel
from typing import Optional, Dict, Any


class EvaluationResult(BaseModel):
    understanding: int
    key_points: int
    structure: int
    accuracy: int
    final_score: int
    feedback: str


class AnswerCreate(BaseModel):
    question_id: int
    student_answer: str


class AnswerResponse(BaseModel):
    id: int
    question_id: int
    student_answer: str
    similarity: Optional[float] = None
    final_score: Optional[float] = None
    evaluation: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

