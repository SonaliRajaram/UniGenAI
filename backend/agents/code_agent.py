from typing import AsyncGenerator
from backend.llm_client import call_llm_stream
from backend.agents.agent_utils import is_feedback_message, is_greeting

async def respond(message: str, user_id: int) -> AsyncGenerator[str, None]:
    # Greetings
    if is_greeting(message):
        for ch in (
            "Hello! I'm your Code Assistant\n\n"
            "I can help you with:\n"
            "• Writing programs\n"
            "• Debugging errors\n"
            "• Algorithms & data structures\n"
            "• Clean and optimized code\n\n"
            "What would you like to code today?"
        ):
            yield ch
        return
    
    # HANDLE FEEDBACK FIRST
    if is_feedback_message(message):
        response = (
            "Thank you! I'm glad you liked it.\n\n"
            "If you'd like:\n"
            "• Changes or improvements\n"
            "• A different topic\n"
            "• A shorter or longer version\n\n"
            "Just let me know!"
        )
        for ch in response:
            yield ch
        return
    
    system_prompt = (
        "You are a coding assistant for students. "
        "Explain the logic first, then provide clean and correct code. "
        "When fixing errors, explain what was wrong."
    )

    prompt = f"{system_prompt}\n\nUser Code Request: {message}\nAssistant:"
    async for token in call_llm_stream(prompt):
        yield token
