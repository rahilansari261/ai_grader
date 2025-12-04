# AI-Powered Answer Grading System

A FastAPI backend that grades student answers using embeddings, similarity thresholds, and LLM-based rubric evaluation.

## Features

- Stores questions, reference answers, and rubrics
- Generates embeddings for semantic similarity comparison
- Calculates cosine similarity between reference and student answers
- Applies penalty logic based on similarity thresholds
- Uses LLM for rubric-based evaluation
- Stores all results in PostgreSQL with pgvector

## Setup

1. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start PostgreSQL with pgvector:**
   ```bash
   docker-compose up -d
   ```

4. **Configure environment:**
   Create a `.env` file with:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_grader
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

## API Endpoints

### Questions
- `POST /questions/` - Create a question
- `GET /questions/` - List all questions
- `GET /questions/{id}` - Get question with rubrics
- `PUT /questions/{id}` - Update question
- `DELETE /questions/{id}` - Delete question

### Rubrics
- `POST /rubrics/` - Create rubric for question
- `GET /rubrics/question/{question_id}` - Get rubrics for question
- `PUT /rubrics/{id}` - Update rubric
- `DELETE /rubrics/{id}` - Delete rubric

### Answers
- `POST /answers/` - Submit student answer (triggers grading)
- `GET /answers/{id}` - Get answer with evaluation
- `GET /answers/question/{question_id}` - List answers for question

## Grading Logic

The system uses three similarity thresholds:

1. **Similarity < 0.30**: Auto-fail with fixed low scores
2. **0.30 ≤ Similarity < 0.60**: Apply linear penalty to LLM score
3. **Similarity ≥ 0.60**: Normal grading without penalty

