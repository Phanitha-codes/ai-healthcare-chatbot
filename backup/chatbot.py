import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ------------------------------------------------------------------
# SYSTEM PROMPT — this is the main guardrail. It defines the bot's
# scope, tone, and what it should do when asked off-topic questions.
# ------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Healthcare Assistant chatbot. Your ONLY purpose is to
answer questions related to healthcare, medicine, wellness, symptoms,
treatments, medications, nutrition, mental health, fitness, and general
health guidance.

Rules you must always follow:
1. Only answer questions related to healthcare/medical/wellness topics.
2. If a user asks something unrelated to healthcare (e.g. coding, sports,
   politics, entertainment, general trivia), politely decline and say:
   "I'm a healthcare assistant, so I can only help with health-related
   questions. Could you ask me something about health, symptoms, or
   wellness instead?"
3. You are NOT a licensed doctor. Always include a brief reminder for
   any medical advice that the user should consult a licensed healthcare
   professional for diagnosis or treatment.
4. Never provide dosages for controlled substances, instructions for
   self-harm, or any dangerous medical guidance.
5. Keep answers clear, simple, and easy to understand for a general audience.
"""

conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# ------------------------------------------------------------------
# KEYWORD-BASED PRE-FILTER (second guardrail layer)
# This catches obviously off-topic messages before calling the API,
# saving cost/latency and giving instant, consistent refusals.
# Note: this is a simple heuristic, not perfect — the system prompt
# above is the main line of defense.
# ------------------------------------------------------------------
HEALTHCARE_KEYWORDS = [
    "health", "doctor", "medicine", "medical", "symptom", "disease",
    "treatment", "therapy", "hospital", "nurse", "diagnosis", "pain",
    "fever", "cold", "flu", "infection", "diet", "nutrition", "vitamin",
    "mental health", "anxiety", "depression", "stress", "sleep", "exercise",
    "fitness", "injury", "wound", "vaccine", "medication", "drug",
    "prescription", "surgery", "pregnancy", "allergy", "blood pressure",
    "diabetes", "cancer", "heart", "covid", "virus", "bacteria", "clinic",
    "wellness", "headache", "cough", "skin", "diet plan", "calories",
]

OFF_TOPIC_REPLY = (
    "I'm a healthcare assistant, so I can only help with health-related "
    "questions. Could you ask me something about health, symptoms, or "
    "wellness instead?"
)


def is_healthcare_related(message: str) -> bool:
    """Quick check: does the message contain any healthcare-related keyword?"""
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in HEALTHCARE_KEYWORDS)


def get_bot_response(user_message: str) -> str:
    """
    Takes the user's message, checks if it's healthcare-related,
    and only then sends it to the Groq API along with conversation
    history. Off-topic messages get an instant canned reply.
    """
    # Guardrail 1: quick keyword filter (fast, no API cost)
    if not is_healthcare_related(user_message):
        return OFF_TOPIC_REPLY

    conversation_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # change to whichever Groq model you used
            messages=conversation_history,
            temperature=0.5,
            max_tokens=1024,
        )
        bot_reply = response.choices[0].message.content

        conversation_history.append({"role": "assistant", "content": bot_reply})
        return bot_reply

    except Exception as e:
        return f"Sorry, something went wrong: {str(e)}"
