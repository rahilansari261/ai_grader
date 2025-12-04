from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db import get_db
from app.models.answer import Answer
from app.models.question import Question
from app.schemas.answer_schemas import AnswerCreate, AnswerResponse
from app.services.embeddings import generate_embedding
from app.services.similarity import calculate_cosine_similarity, list_to_array
from app.services.grader import grade_answer
from app.config import GENERAL_RUBRIC

router = APIRouter(prefix="/answers", tags=["answers"])


@router.post("/", response_model=AnswerResponse, status_code=status.HTTP_201_CREATED)
async def submit_answer(
    answer_data: AnswerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit a student answer and trigger grading"""
    # Get question
    question_result = await db.execute(
        select(Question).where(Question.id == answer_data.question_id)
    )
    question = question_result.scalar_one_or_none()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )

    if not question.embedding:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question reference answer embedding not found",
        )

    # Use general rubric for all questions
    rubric_text = GENERAL_RUBRIC

    # Generate embedding for student answer
    student_embedding = await generate_embedding(answer_data.student_answer)

    # Calculate cosine similarity
    # Convert embedding to list if needed (pgvector returns list-like object)
    ref_embedding_list = list(question.embedding) if question.embedding else []
    if not ref_embedding_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question embedding is empty",
        )
    ref_embedding_array = list_to_array(ref_embedding_list)
    student_embedding_array = list_to_array(student_embedding)
    similarity = calculate_cosine_similarity(ref_embedding_array, student_embedding_array)

    # Grade the answer
    evaluation = await grade_answer(
        similarity=similarity,
        rubric=rubric_text,
        question=question.text,
        ref_answer=question.reference_answer,
        student_answer=answer_data.student_answer,
    )

    # Create answer record
    answer = Answer(
        question_id=answer_data.question_id,
        student_answer=answer_data.student_answer,
        embedding=student_embedding,
        similarity=similarity,
        final_score=evaluation.get("final_score", 0),
        evaluation=evaluation,
    )

    db.add(answer)
    await db.commit()
    await db.refresh(answer)

    return answer


@router.get("/{answer_id}", response_model=AnswerResponse)
async def get_answer(
    answer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get an answer with its evaluation"""
    result = await db.execute(
        select(Answer).where(Answer.id == answer_id)
    )
    answer = result.scalar_one_or_none()
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    
    return answer


@router.get("/question/{question_id}", response_model=List[AnswerResponse])
async def list_answers_for_question(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all answers for a question"""
    result = await db.execute(
        select(Answer).where(Answer.question_id == question_id)
    )
    answers = result.scalars().all()
    return answers

