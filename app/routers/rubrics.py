from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.db import get_db
from app.models.rubric import Rubric
from app.models.question import Question
from app.schemas.rubric_schemas import RubricCreate, RubricResponse

router = APIRouter(prefix="/rubrics", tags=["rubrics"])


@router.post("/", response_model=RubricResponse, status_code=status.HTTP_201_CREATED)
async def create_rubric(
    rubric_data: RubricCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a rubric for a question"""
    # Verify question exists
    result = await db.execute(
        select(Question).where(Question.id == rubric_data.question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    rubric = Rubric(
        question_id=rubric_data.question_id,
        criterion=rubric_data.criterion,
        weight=rubric_data.weight
    )
    
    db.add(rubric)
    await db.commit()
    await db.refresh(rubric)
    
    return rubric


@router.get("/question/{question_id}", response_model=List[RubricResponse])
async def get_rubrics_for_question(
    question_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all rubrics for a question"""
    result = await db.execute(
        select(Rubric).where(Rubric.question_id == question_id)
    )
    rubrics = result.scalars().all()
    return rubrics


@router.put("/{rubric_id}", response_model=RubricResponse)
async def update_rubric(
    rubric_id: int,
    rubric_data: RubricCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update a rubric"""
    result = await db.execute(
        select(Rubric).where(Rubric.id == rubric_id)
    )
    rubric = result.scalar_one_or_none()
    
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rubric not found"
        )
    
    # Verify question exists if changed
    if rubric_data.question_id != rubric.question_id:
        question_result = await db.execute(
            select(Question).where(Question.id == rubric_data.question_id)
        )
        if not question_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Question not found"
            )
    
    rubric.question_id = rubric_data.question_id
    rubric.criterion = rubric_data.criterion
    rubric.weight = rubric_data.weight
    
    await db.commit()
    await db.refresh(rubric)
    
    return rubric


@router.delete("/{rubric_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rubric(
    rubric_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a rubric"""
    result = await db.execute(
        select(Rubric).where(Rubric.id == rubric_id)
    )
    rubric = result.scalar_one_or_none()
    
    if not rubric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rubric not found"
        )
    
    await db.delete(rubric)
    await db.commit()
    
    return None

