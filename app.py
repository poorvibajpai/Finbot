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
