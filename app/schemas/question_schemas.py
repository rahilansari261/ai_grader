from pydantic import BaseModel


class QuestionCreate(BaseModel):
    text: str
    reference_answer: str


class QuestionResponse(BaseModel):
    id: int
    question_number: int | None = None
    text: str
    reference_answer: str

    class Config:
        from_attributes = True

