def is_greeting(message: str) -> bool:
    greetings = [
        "hello", "hi", "hey",
        "good morning", "good afternoon", "good evening",
        "how are you", "how r u"
    ]

    msg = message.lower().strip()
    return msg in greetings

def is_feedback_message(message: str) -> bool:
    feedback_phrases = [
        "thank you",
        "thanks",
        "awesome",
        "great",
        "nice",
        "good",
        "perfect",
        "amazing",
        "it was awesome",
        "it is working",
        "works perfectly",
        "cool",
        "ok",
        "okay",
        "fine",
        "got it",
        "understood"
    ]

    msg = message.lower().strip()
    return any(p in msg for p in feedback_phrases)