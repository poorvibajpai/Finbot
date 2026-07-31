import os
import re

from flask import Flask, render_template, request, jsonify, session

from calculators import loan_tenure, sip_for_target, CalculatorError
import llm

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

GREETING = (
    "Hi, I'm FinBot \U0001F4B0 — I can chat about savings, loans, investing, "
    "interest and budgeting, and I can run two calculators for you:\n\n"
    "1. Loan Tenure — how long it'll take to pay off a loan\n"
    "2. SIP for a Target Amount — how much to invest monthly to hit a goal\n\n"
    "Ask me a finance question any time, or say \"calculate loan tenure\" / "
    "\"help me plan an SIP\" to get started."
)

LOAN_FIELDS = [
    ("P", "What's the loan amount (principal)? e.g. 500000"),
    ("E", "What's your monthly EMI amount? e.g. 12000"),
    ("R", "What's the annual interest rate, in %? e.g. 9.5"),
]

SIP_FIELDS = [
    ("target", "What's the target amount you want to reach? e.g. 1000000"),
    ("R", "What annual return rate (%) do you expect? e.g. 12"),
    ("years", "Over how many years will you invest? e.g. 10"),
]

FIELD_LABELS = {
    "P": "Loan amount",
    "E": "Monthly EMI",
    "R": "Annual rate (%)",
    "target": "Target amount",
    "years": "Investment period (years)",
}

YES_WORDS = {"yes", "y", "yeah", "yep", "correct", "confirm", "sure", "go ahead"}
NO_WORDS = {"no", "n", "nope", "cancel", "restart"}


# ---------------------------------------------------------------------------
# Session-backed conversation state
# ---------------------------------------------------------------------------

def fresh_state():
    return {"stage": None, "step": 0, "inputs": {}, "confirming": False}


def get_state():
    if "calc_state" not in session:
        session["calc_state"] = fresh_state()
    return session["calc_state"]


def save_state(state):
    session["calc_state"] = state
    session.modified = True


def push_history(role, content):
    hist = session.get("history", [])
    hist.append({"role": role, "content": content})
    session["history"] = hist[-10:]
    session.modified = True


def fields_for(stage):
    return LOAN_FIELDS if stage == "loan_tenure" else SIP_FIELDS


def ask_current_field(state):
    _, question = fields_for(state["stage"])[state["step"]]
    return question


def confirmation_text(state):
    fields = fields_for(state["stage"])
    lines = [f"  • {FIELD_LABELS[k]}: {state['inputs'][k]:,.2f}" for k, _ in fields]
    calc_name = "Loan Tenure" if state["stage"] == "loan_tenure" else "SIP"
    return (
        f"Got it — here's what I have for the {calc_name} calculation:\n"
        + "\n".join(lines)
        + "\n\nShall I go ahead and calculate? (yes/no)"
    )


def run_calculation(state):
    inputs = state["inputs"]
    if state["stage"] == "loan_tenure":
        years, months = loan_tenure(inputs["P"], inputs["E"], inputs["R"])
        return (
            f"With a loan of {inputs['P']:,.0f} at {inputs['R']:g}% annual interest, "
            f"paying an EMI of {inputs['E']:,.0f}/month, it will take "
            f"**{years} year(s) & {months} month(s)** to pay it off."
        )
    else:
        sip = sip_for_target(inputs["target"], inputs["R"], inputs["years"])
        return (
            f"To reach {inputs['target']:,.0f} in {inputs['years']:g} year(s) at an "
            f"expected {inputs['R']:g}% annual return, you'd need to invest "
            f"**{sip:,.2f}/month** via SIP."
        )


def parse_number(text):
    match = re.search(r"-?\d+(\.\d+)?", text.replace(",", ""))
    if not match:
        return None
    return float(match.group())


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
