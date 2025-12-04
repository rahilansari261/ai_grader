from pydantic import BaseModel


class RubricCreate(BaseModel):
    question_id: int
    criterion: str
    weight: float = 1.0


class RubricResponse(BaseModel):
    id: int
    question_id: int
    criterion: str
    weight: float

    class Config:
        from_attributes = True

