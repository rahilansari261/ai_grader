from pydantic import BaseModel


class QuestionCreate(BaseModel):
    text: str
    reference_answer: str
    category: str


class QuestionResponse(BaseModel):
    id: int
    text: str
    reference_answer: str
    category: str

    class Config:
        from_attributes = True

