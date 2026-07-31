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


def loan_tenure(P: float, E: float, R: float):
    """
    Loan Tenure calculator.

    P: loan principal
    E: monthly EMI
    R: annual interest rate (%)

    Returns (years, months).
    Raises CalculatorError if inputs are invalid or the EMI never covers
    the monthly interest (loan would never be paid off).
    """
    if P <= 0 or E <= 0:
        raise CalculatorError("Loan amount and EMI must both be positive numbers.")
    if R <= 0 or R > 100:
        raise CalculatorError("Annual interest rate should be between 0 and 100.")

    r = _monthly_rate(R)

    if E - P * r <= 0:
        raise CalculatorError(
            f"An EMI of {E:,.2f} does not even cover the monthly interest on this loan "
            f"(monthly interest ≈ {P * r:,.2f}), so the balance would never go down. "
            f"Try a higher EMI."
        )

    n = math.log(E / (E - P * r)) / math.log(1 + r)
    n = max(n, 0.0)

    years = int(n // 12)
    months = round(n - years * 12)
    if months == 12:
        months = 0
        years += 1

    return years, months


