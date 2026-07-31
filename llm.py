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


