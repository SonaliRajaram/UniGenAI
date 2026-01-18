from typing import AsyncGenerator
from backend.llm_client import call_llm_stream
from backend.agents.agent_utils import is_feedback_message, is_greeting

async def respond(message: str, user_id: int) -> AsyncGenerator[str, None]:
    # Greetings
    if is_greeting(message):
        for ch in (
            "Hello! I'm your Content Creator\n\n"
            "I can help you with:\n"
            "• YouTube scripts\n"
            "• Essays & blogs\n"
            "• Stories & Speeches\n"
            "• Creative writing\n"
            "• Social media content\n\n"
            "What content would you like me to create today?"
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
    
    # CONTENT CREATION
    system_prompt = (
        "You are a creative content generator. "
        "You create YouTube scripts, essays, blogs, speeches, and social media content. "
        "Ensure clarity, structure, and engaging tone."
    )

    prompt = f"{system_prompt}\n\nRequest: {message}\nContent:"
    async for token in call_llm_stream(prompt):
        yield token
