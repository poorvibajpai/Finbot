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

## Example conversations

### 1. General finance question

```
User: What's the difference between a fixed and a floating interest rate?
FinBot: A fixed rate stays the same for the whole loan term, so your EMI
never changes — good for predictable budgeting. A floating rate moves with
the market (e.g. tied to a benchmark rate), so your EMI can rise or fall
over time. Floating rates often start a bit lower but carry more risk if
rates climb. If you value certainty, fixed is usually the safer pick.
```

### 2. Off-topic question being declined

```
User: What's the weather like in Lucknow today?
FinBot: I'm only able to help with finance topics — savings, loans,
investing, interest, and budgeting. Is there something in that space I can
help with?
```

### 3. Full calculator walkthrough (Loan Tenure)

```
User: I want to calculate loan tenure
FinBot: Sure, let's work out your Loan Tenure.

What's the loan amount (principal)? e.g. 500000

User: 500000
FinBot: What's your monthly EMI amount? e.g. 12000

User: 12000
FinBot: What's the annual interest rate, in %? e.g. 9.5

User: 9.5
FinBot: Got it — here's what I have for the Loan Tenure calculation:
  • Loan amount: 500,000.00
  • Monthly EMI: 12,000.00
  • Annual rate (%): 9.50

Shall I go ahead and calculate? (yes/no)

User: yes
FinBot: With a loan of 500,000 at 9.5% annual interest, paying an EMI of
12,000/month, it will take 4 year(s) & 2 month(s) to pay it off.

Anything else — another calculation, or a finance question?
```

### 4. Invalid input handled gracefully (EMI too low)

```
User: loan tenure please
FinBot: Sure, let's work out your Loan Tenure. What's the loan amount
(principal)?

User: 500000
FinBot: What's your monthly EMI amount?

User: 1000
FinBot: What's the annual interest rate, in %?

User: 9.5
FinBot: An EMI of 1,000.00 does not even cover the monthly interest on
this loan (monthly interest ≈ 3,795.77), so the balance would never go
down. Try a higher EMI.

Let's start over — what would you like to calculate?
```

## Notes on the math

- **Loan Tenure**: monthly rate `r = (1 + R/100)^(1/12) - 1`; number of
  months `n = ln(E / (E - P·r)) / ln(1 + r)`. Only valid when `E > P·r`
  (EMI must exceed the monthly interest), which is checked explicitly.
- **SIP for a Target**: monthly rate `r` as above; required monthly SIP
  `= Target · r / (((1 + r)^(months) - 1) · (1 + r))`, assuming deposits at
  the start of each month (annuity-due).

## Not included

- No SWP calculator (task requires any two of three — Loan Tenure and SIP
  are implemented).
- No MCP tool exposure (listed as a bonus in the brief, not required).
- No user accounts, persistence, or auth — conversation state lives in the
  Flask session for the duration of the browser session, as allowed by the
  brief.
