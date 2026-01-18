from backend.intent_router import classify_intent
from backend.mock_interview.session import is_session_active

# AGENT CAPABILITY MAP 
# Defines what each agent is ALLOWED to handle
AGENT_CAPABILITIES = {
    "academic": {"academic", "general"},   # greetings, study, interviews
    "content": {"content", "general"},     # scripts + feedback
    "code": {"code", "general"},            # programming + feedback
    "general": {"general"}                  # only casual talk
}


async def route_agent(message: str, forced_role: str | None, user_id: int) -> str:
    """
    Decide which agent should handle the message.

    Rules:
    1. If in active mock interview → ALWAYS stay with academic (session protected)
    2. If no agent selected → trust classifier (first message)
    3. If agent selected AND it can handle the intent → stay
    4. If agent selected BUT cannot handle intent → AUTO SWITCH to better agent
    """

    # CRITICAL: During active mock interview, NEVER auto-switch
    # The academic agent is handling the interview session itself
    if is_session_active(str(user_id)):
        return "academic"

    detected_intent = await classify_intent(message)

    # CASE 1: User did NOT select an agent (first message)
    if not forced_role:
        return detected_intent

    # CASE 2: Current agent CAN handle this intent → STAY
    allowed_intents = AGENT_CAPABILITIES.get(forced_role, set())
    if detected_intent in allowed_intents:
        return forced_role

    # CASE 3: Current agent CANNOT handle → AUTO SWITCH
    return detected_intent
