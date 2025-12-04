from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    openai_api_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

GENERAL_RUBRIC = """
Criteria and weights (applied to all questions):

1. Understanding (25%):
   - Does the student show clear understanding of the question and underlying concept?

2. Key Points (35%):
   - Does the answer cover the essential ideas, steps, or facts expected for this question?

3. Structure (15%):
   - Is the answer well-organized, coherent, and easy to follow?

4. Accuracy (25%):
   - Are the statements factually and logically correct, without major errors?

Scoring:
- understanding, key_points, structure, accuracy are all scored from 0 to 100.
- final_score is an overall score from 0 to 100, reflecting the weighted combination.
"""

