"""
Script to drop all tables and recreate the database schema.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db import engine, Base
from app.models.question import Question
from app.models.answer import Answer


async def reset_database():
    """Drop all tables and recreate them"""
    async with engine.begin() as conn:
        print("Dropping all tables...")
        
        # Drop all tables in reverse order of dependencies
        await conn.execute(text("DROP TABLE IF EXISTS answers CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS questions CASCADE"))
        
        # Drop any other tables that might exist
        await conn.execute(text("""
            DO $$ 
            DECLARE 
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
                LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """))
        
        print("All tables dropped successfully!")
        
        # Recreate all tables
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        print("Database reset completed successfully!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database())

