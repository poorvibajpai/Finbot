"""
LLM integration layer. Supports two providers, chosen via the LLM_PROVIDER
env var: "ollama" (default, local, free) or "gemini" (needs GEMINI_API_KEY).

This module never lets an LLM failure crash the app: call_llm() returns
None on any error, and callers fall back to a keyword-based classifier or
a friendly "try again" message.
"""
import os
import requests

PROVIDER = os.environ.get("LLM_PROVIDER", "ollama").lower()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

GEMINI_MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

_gemini_client = None
if PROVIDER == "gemini" and GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
    _gemini_client = genai.GenerativeModel(GEMINI_MODEL_NAME)


def _call_ollama(system_prompt: str, user_prompt: str) -> str:
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    resp = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": full_prompt, "stream": False},
        timeout=30,
    )
    resp.raise_for_status()
    return (resp.json().get("response") or "").strip()


def _call_gemini(system_prompt: str, user_prompt: str) -> str:
    if _gemini_client is None:
        raise RuntimeError("Gemini client not configured (missing GEMINI_API_KEY).")
    prompt = f"{system_prompt}\n\n{user_prompt}"
    response = _gemini_client.generate_content(prompt)
    return (response.text or "").strip()


def call_llm(system_prompt: str, user_prompt: str):
    """Returns the model's reply, or None if the call failed for any reason."""
    try:
        if PROVIDER == "gemini":
            return _call_gemini(system_prompt, user_prompt)
        return _call_ollama(system_prompt, user_prompt)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

INTENT_SYSTEM = """You are an intent classifier for a personal-finance chatbot.
Classify the user's latest message into exactly ONE of these labels:

LOAN_TENURE - user wants to know how long it will take to pay off a loan
SIP - user wants to know how much to invest monthly (SIP) to reach a target amount
OFF_TOPIC - the message has nothing to do with personal finance (weather, coding help, trivia, etc.)
FINANCE - a general finance question or discussion (savings, budgeting, interest, investing concepts, etc.)

Reply with ONLY the single label word, nothing else."""

_LOAN_KEYWORDS = [
    "loan tenure", "pay off my loan", "loan term", "how long to pay off",
    "loan calculator", "years to repay", "repay my loan", "how long will it take to pay", "months to repay", "loan duration",
]
_SIP_KEYWORDS = [
    "sip", "systematic investment", "target amount", "invest monthly",
    "monthly investment", "reach my goal", "how much should i invest",
    "monthly sip", "investment plan for",
]
_FINANCE_KEYWORDS = [
    "save", "saving", "invest", "interest", "budget", "loan", "emi", "stock",
    "mutual fund", "credit", "debt", "tax", "retirement", "insurance",
    "expense", "income", "finance", "financial", "money",
]


def _keyword_fallback(message: str) -> str:
    m = message.lower()
    if any(k in m for k in _LOAN_KEYWORDS):
        return "LOAN_TENURE"
    if any(k in m for k in _SIP_KEYWORDS):
        return "SIP"
    if any(k in m for k in _FINANCE_KEYWORDS):
        return "FINANCE"
    return "OFF_TOPIC"


def classify_intent(message: str) -> str:
    raw = call_llm(INTENT_SYSTEM, message)
    if raw:
        label = raw.strip().upper().split()[0].strip(".:,!")
        if label in ("LOAN_TENURE", "SIP", "OFF_TOPIC", "FINANCE"):
            return label
    return _keyword_fallback(message)


# ---------------------------------------------------------------------------
# General finance conversation
# ---------------------------------------------------------------------------

FINANCE_SYSTEM = """You are FinBot, a friendly assistant that ONLY discusses personal
finance topics: savings, loans, investing, interest, budgeting, taxes, insurance,
and related subjects. Keep replies concise (3-5 sentences), clear, and practical.
Give general education, not personalized investment/legal advice — suggest a
qualified professional for that. If the message turns out not to be about finance,
politely say you can only help with finance topics."""


def finance_chat(message: str, history: list) -> str:
    context_lines = []
    for turn in history[-6:]:
        speaker = "User" if turn.get("role") == "user" else "FinBot"
        context_lines.append(f"{speaker}: {turn.get('content', '')}")
    context_lines.append(f"User: {message}")
    prompt = "\n".join(context_lines)

    reply = call_llm(FINANCE_SYSTEM, prompt)
    if reply:
        return reply
    return (
        "I'm having trouble reaching the language model right now. I can still run "
        "my calculators, or you can try your question again in a moment."
    )
