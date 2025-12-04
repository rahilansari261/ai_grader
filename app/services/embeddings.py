from typing import List
from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI text-embedding-3-small (1536 dimensions)
    """
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

