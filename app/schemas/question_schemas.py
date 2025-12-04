from pydantic import BaseModel
from typing import List, Optional
from app.schemas.rubric_schemas import RubricResponse


class QuestionCreate(BaseModel):
    text: str
    reference_answer: str


class QuestionResponse(BaseModel):
    id: int
    text: str
    reference_answer: str

    class Config:
        from_attributes = True


class QuestionWithRubric(QuestionResponse):
    rubrics: List[RubricResponse] = []

