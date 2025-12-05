"""
Seed script to load questions from seed.json into the database.
"""
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal, init_db
from app.models.question import Question
from app.services.embeddings import generate_embedding


async def question_exists(db: AsyncSession, text: str) -> bool:
    """Check if a question with the same text already exists"""
    result = await db.execute(select(Question).where(Question.text == text))
    return result.scalar_one_or_none() is not None


async def seed_questions():
    """Seed questions from seed.json file"""
    # Initialize database
    await init_db()
    
    # Load seed.json
    seed_file = Path(__file__).parent.parent / "seed.json"
    if not seed_file.exists():
        print(f"Error: {seed_file} not found!")
        return
    
    with open(seed_file, "r", encoding="utf-8") as f:
        questions_data = json.load(f)
    
    print(f"Loaded {len(questions_data)} questions from seed.json")
    
    async with AsyncSessionLocal() as db:
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, q_data in enumerate(questions_data, start=1):
            try:
                # Check if question already exists
                if await question_exists(db, q_data["text"]):
                    print(f"[{idx}/{len(questions_data)}] Skipped (already exists): {q_data['text'][:50]}...")
                    skipped_count += 1
                    continue
                
                # Generate embedding for reference answer
                print(f"[{idx}/{len(questions_data)}] Processing: {q_data['text'][:50]}...")
                embedding = await generate_embedding(q_data["reference_answer"])
                
                # Create question
                question = Question(
                    text=q_data["text"],
                    reference_answer=q_data["reference_answer"],
                    category=q_data.get("category", "General"),
                    embedding=embedding
                )
                
                db.add(question)
                await db.commit()
                
                created_count += 1
                
                # Progress update every 50 questions
                if idx % 50 == 0:
                    print(f"Progress: {idx}/{len(questions_data)} (Created: {created_count}, Skipped: {skipped_count}, Errors: {error_count})")
                    
            except Exception as e:
                error_count += 1
                print(f"[{idx}/{len(questions_data)}] Error processing question: {str(e)}")
                await db.rollback()
                continue
        
        print("\n" + "="*50)
        print("Seeding completed!")
        print(f"Total questions in file: {len(questions_data)}")
        print(f"Created: {created_count}")
        print(f"Skipped (already exists): {skipped_count}")
        print(f"Errors: {error_count}")
        print("="*50)


if __name__ == "__main__":
    asyncio.run(seed_questions())

