import json
from typing import Dict, Any
from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

MAX_PENALTY = 40


def calculate_penalty(similarity: float) -> float:
    """
    Calculate penalty based on similarity score.
    Formula: ((0.60 - similarity) / 0.30) * MAX_PENALTY
    Only applies when 0.30 <= similarity < 0.60
    """
    if similarity < 0.30 or similarity >= 0.60:
        return 0.0
    
    penalty = ((0.60 - similarity) / 0.30) * MAX_PENALTY
    return penalty


async def grade_answer(
    similarity: float,
    rubric: str,
    question: str,
    ref_answer: str,
    student_answer: str
) -> Dict[str, Any]:
    """
    Grade student answer using LLM with penalty logic based on similarity.
    
    Case 1: similarity < 0.30 -> Auto-fail
    Case 2: 0.30 <= similarity < 0.60 -> Apply penalty
    Case 3: similarity >= 0.60 -> Normal grading
    """
    # Case 1: Auto-fail for very low similarity
    if similarity < 0.30:
        return {
            "understanding": 0,
            "key_points": 0,
            "structure": 5,
            "accuracy": 0,
            "final_score": 5,
            "feedback": "Answer is unrelated.",
            "isCorrect": False
        }
    
    # Calculate confidence score for prompt
    confidence_score = min(similarity * 100, 100)
    
    # Build prompt template
    prompt = f"""You are an experienced examiner. You will grade a student's answer using the rubric AND the similarity score.

Similarity Score: {similarity:.2f}
Confidence Score: {confidence_score:.2f}

Rules:
- If similarity < 0.50 → heavily penalize understanding and key points
- If similarity 0.50–0.70 → apply moderate penalty
- If similarity > 0.70 → grade normally
- Do NOT reward unrelated or incorrect answers

Rubric:
{rubric}

Question:
{question}

Reference Answer:
{ref_answer}

Student Answer:
{student_answer}

Return a JSON object ONLY:
{{
  "understanding": number,
  "key_points": number,
  "structure": number,
  "accuracy": number,
  "final_score": number,
  "feedback": "string",
  "isCorrect": boolean
}}

IMPORTANT: The "isCorrect" field must be included and should reflect whether the answer is factually/conceptually correct based on your evaluation, regardless of the final_score. For example:
- If the answer is numerically or factually correct but lacks explanation/format, set isCorrect: true
- If the answer is wrong or unrelated, set isCorrect: false
- Base isCorrect on the correctness of the answer itself, not on the scoring criteria like structure or completeness
"""

    # Call OpenAI GPT-4
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert grader. Always return valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    # Parse JSON response
    content = response.choices[0].message.content.strip()
    
    # Try to extract JSON if wrapped in markdown
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        result = {
            "understanding": 0,
            "key_points": 0,
            "structure": 0,
            "accuracy": 0,
            "final_score": 0,
            "feedback": "Error parsing LLM response.",
            "isCorrect": False
        }
    
    # Case 2: Apply penalty for moderate similarity
    if 0.30 <= similarity < 0.60:
        penalty = calculate_penalty(similarity)
        original_score = result.get("final_score", 0)
        result["final_score"] = max(0, original_score - penalty)
        
        # Also adjust individual criteria proportionally
        if original_score > 0:
            penalty_ratio = penalty / original_score
            for key in ["understanding", "key_points", "structure", "accuracy"]:
                if key in result:
                    result[key] = max(0, int(result[key] * (1 - penalty_ratio * 0.5)))
    
    # Clamp final score between 0 and 100
    result["final_score"] = max(0, min(100, int(result.get("final_score", 0))))
    
    # Ensure all scores are integers
    for key in ["understanding", "key_points", "structure", "accuracy", "final_score"]:
        if key in result:
            result[key] = int(result[key])
    
    # Ensure isCorrect is a boolean - LLM must generate it based on its evaluation
    # If LLM didn't provide it, we need to re-request or use a default
    if "isCorrect" not in result:
        # If LLM didn't provide isCorrect, raise an error or set a default
        # This should not happen if prompt is clear, but we'll set False as safe default
        result["isCorrect"] = False
    else:
        # Ensure it's a boolean (LLM might return it as string "true"/"false" or boolean)
        is_correct_value = result["isCorrect"]
        if isinstance(is_correct_value, str):
            # Handle string values explicitly - bool("false") would incorrectly return True
            result["isCorrect"] = is_correct_value.lower() in ("true", "1", "yes")
        else:
            # For boolean or numeric values, use bool() conversion
            result["isCorrect"] = bool(is_correct_value)
    
    return result
