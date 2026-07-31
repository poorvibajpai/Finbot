"""
Pure financial calculators — no LLM or Flask code here on purpose,
so the math can be tested and reasoned about in isolation.
"""
import math


class CalculatorError(Exception):
    """Raised for invalid inputs / infeasible calculations (never let these crash the app)."""
    pass


def _monthly_rate(annual_rate_pct: float) -> float:
    """Convert an annual rate (%) into an equivalent monthly compounding rate."""
    return (1 + annual_rate_pct / 100) ** (1 / 12) - 1


