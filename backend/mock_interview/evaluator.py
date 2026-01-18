from backend.llm_client import call_llm_stream
from typing import AsyncGenerator

async def evaluate_answer(question: str, answer: str) -> AsyncGenerator[str, None]:
    prompt = f"""
You are an expert interview evaluator for technical and behavioral interviews.
Step 1: Identify the core technical concepts required for the question.
Step 2: Check if the candidate mentioned those concepts.
Step 3: Rate the technical accuracy (1-10).
Step 4: Provide constructive feedback.

Question:
{question}

Candidate Answer:
{answer}

Provide a structured evaluation including:
- Strengths: What was good about the answer?
- Weaknesses: What was missing or incorrect?
- Key Points: Brief summary of the correct answer.
- Score: A numerical score out of 10, with justification.

Keep the response concise and professional.
"""

    try:
        async for token in call_llm_stream(prompt):
            yield token
    except Exception as e:
        yield f"Evaluation failed: {str(e)}"