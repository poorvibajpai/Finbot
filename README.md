# FinBot — Financial Chatbot with Interactive Calculators

A small Flask chatbot that discusses personal finance topics and can walk a
user through two interactive calculators: **Loan Tenure** and **SIP for a
Target Amount**.

## What it does

- On start, greets the user and lists the calculators it can run.
- General finance questions (savings, budgeting, interest, investing, etc.)
  are answered conversationally by an LLM.
- Off-topic questions (weather, coding help, trivia, …) are politely
  declined and redirected back to finance.
- Calculator requests are handled interactively: the bot asks for each
  required input **one at a time**, echoes the values back for confirmation,
  then computes and shows the result.
- Bad inputs (negative numbers, out-of-range rates, an EMI that doesn't
  even cover the monthly interest) are caught and explained instead of
  crashing.

## Project layout

```
app.py            Flask routes + the calculator conversation state machine
calculators.py    Pure math: loan_tenure(), sip_for_target() — no LLM/Flask code
llm.py            LLM wrapper: intent classification + finance chat (Ollama or Gemini)
templates/        Chat page (Jinja)
static/           CSS + client-side JS for the chat UI
```

Calculator math and chat/LLM logic are kept in separate modules on purpose.

## Which LLM

Supports **either**:

- **Ollama** (default) — local, free, no API key. Requires Ollama running
  locally with a model pulled, e.g. `ollama pull llama3.1`.
- **Gemini** — set `LLM_PROVIDER=gemini` and `GEMINI_API_KEY` to use
  Google's Gemini API instead.

If the LLM call fails for any reason (model not running, no API key, network
issue), the bot falls back to a keyword-based classifier for intent
detection and a friendly "try again" message for open-ended chat, so it
never crashes even without an LLM configured.

## How to run

```bash
cd finbot
python3 -m venv venv && source venv/bin/activate     # optional but recommended
pip install -r requirements.txt

# Option A: Ollama (default)
ollama pull llama3.1        # once, if you don't already have a model
ollama serve                # if not already running
export LLM_PROVIDER=ollama

# Option B: Gemini
export LLM_PROVIDER=gemini
export GEMINI_API_KEY=your_key_here

python3 app.py
```

Then open **http://localhost:5000** in a browser.

See `.env.example` for all configurable environment variables.

