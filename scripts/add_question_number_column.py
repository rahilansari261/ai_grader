"""
Migration script to add question_number column to questions table.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import engine


async def add_question_number_column():
    """Add question_number column to questions table if it doesn't exist"""
    async with engine.begin() as conn:
        # Check if column exists
        check_query = text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='questions' AND column_name='question_number'
        """)
        result = await conn.execute(check_query)
        column_exists = result.fetchone() is not None
        
        if column_exists:
            print("Column 'question_number' already exists. Skipping migration.")
            return
        
        # Add the column
        print("Adding 'question_number' column to questions table...")
        await conn.execute(text("""
            ALTER TABLE questions 
            ADD COLUMN question_number INTEGER UNIQUE
        """))
        
        # Create index
        print("Creating index on question_number...")
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_questions_question_number 
            ON questions(question_number)
        """))
        
        print("Migration completed successfully!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(add_question_number_column())

