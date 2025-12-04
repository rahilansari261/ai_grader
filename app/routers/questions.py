from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.db import get_db
from app.models.question import Question
from app.schemas.question_schemas import QuestionCreate, QuestionResponse
from app.services.embeddings import generate_embedding

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new question and generate embedding for reference answer"""
    # Get next question number
    result = await db.execute(select(func.max(Question.question_number)))
    max_number = result.scalar()
    next_question_number = (max_number or 0) + 1
    
    # Generate embedding for reference answer
    embedding = await generate_embedding(question_data.reference_answer)
    
    # Create question
    question = Question(
        question_number=next_question_number,
        text=question_data.text,
        reference_answer=question_data.reference_answer,
        embedding=embedding
    )
    
    db.add(question)
    await db.commit()
    await db.refresh(question)
    
    return question


@router.get("/", response_model=List[QuestionResponse])
async def list_questions(db: AsyncSession = Depends(get_db)):
    """List all questions"""
    result = await db.execute(select(Question))
    questions = result.scalars().all()
    return questions


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get question by ID"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update a question"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Store old reference answer before updating
    old_reference_answer = question.reference_answer
    
    # Update fields
    question.text = question_data.text
    question.reference_answer = question_data.reference_answer
    
    # Regenerate embedding if reference answer changed
    if old_reference_answer != question_data.reference_answer:
        question.embedding = await generate_embedding(question_data.reference_answer)
    
    await db.commit()
    await db.refresh(question)
    
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a question"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    await db.delete(question)
    await db.commit()
    
    return None

