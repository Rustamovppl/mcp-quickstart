"""A small, tested MCP server: a finance toolkit.

Exposes finance and statistics tools over the Model Context Protocol so any MCP
client (Claude Code, Cursor, Windsurf) can call them. It also demonstrates the
full MCP surface — tools, a resource, and a prompt — not just tools.

Every tool delegates to a plain function with explicit input validation, so the
logic is unit-tested directly (see test_server.py) without going through MCP.

Run:
    python server.py          # stdio transport; or: uv run server.py
"""
from __future__ import annotations

import statistics
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("finance-toolkit")

# Rates are passed as decimals throughout: 0.05 means 5%.


@mcp.tool()
def summary_stats(numbers: list[float]) -> dict[str, float]:
    """Return basic statistics (count, mean, median, stdev) for a list of numbers."""
    if not numbers:
        raise ValueError("numbers must not be empty")
    return {
        "count": float(len(numbers)),
        "mean": statistics.fmean(numbers),
        "median": statistics.median(numbers),
        "stdev": statistics.pstdev(numbers),
    }


@mcp.tool()
def compound_interest(
    principal: float, annual_rate: float, years: float, compounds_per_year: int = 12
) -> dict[str, float]:
    """Future value of a principal under compound interest.

    annual_rate is a decimal (0.05 == 5%). Compounds monthly by default. Returns
    the final amount and the interest earned.
    """
    if principal < 0 or years < 0:
        raise ValueError("principal and years must be non-negative")
    if compounds_per_year <= 0:
        raise ValueError("compounds_per_year must be positive")
    n = compounds_per_year
    amount = principal * (1 + annual_rate / n) ** (n * years)
    return {
        "final_amount": round(amount, 2),
        "interest_earned": round(amount - principal, 2),
    }


@mcp.tool()
def loan_payment(principal: float, annual_rate: float, months: int) -> dict[str, float]:
    """Fixed monthly payment for an amortizing loan (standard annuity formula).

    annual_rate is a decimal (0.06 == 6% APR). Returns the monthly payment, the
    total paid over the term, and the total interest.
    """
    if principal <= 0 or months <= 0:
        raise ValueError("principal and months must be positive")
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        payment = principal / months
    else:
        payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)
    total = payment * months
    return {
        "monthly_payment": round(payment, 2),
        "total_paid": round(total, 2),
        "total_interest": round(total - principal, 2),
    }


@mcp.tool()
def percentage_change(old: float, new: float) -> float:
    """Percentage change from `old` to `new` (e.g. 100 -> 150 returns 50.0)."""
    if old == 0:
        raise ValueError("old must not be zero")
    return round((new - old) / old * 100, 4)


@mcp.tool()
def moving_average(numbers: list[float], window: int) -> list[float]:
    """Simple moving average over a sliding window — handy for smoothing series."""
    if window <= 0:
        raise ValueError("window must be positive")
    if window > len(numbers):
        raise ValueError("window must not exceed the number of points")
    return [
        round(statistics.fmean(numbers[i : i + window]), 6)
        for i in range(len(numbers) - window + 1)
    ]


@mcp.tool()
def utc_now() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


@mcp.resource("finance://reference")
def reference() -> str:
    """Conventions these tools assume — exposed as an MCP resource."""
    return (
        "Rates are decimals: 0.05 means 5%.\n"
        "compound_interest compounds monthly (compounds_per_year=12) by default.\n"
        "loan_payment uses the standard amortizing-annuity formula on a monthly rate."
    )


@mcp.prompt()
def savings_plan(goal_amount: float, years: float) -> str:
    """Reusable prompt: plan how to reach a savings goal using these tools."""
    return (
        f"I want to reach {goal_amount} in {years} years. "
        "Ask me for my expected annual return, then use the compound_interest tool "
        "to show the monthly contribution I'd need and the interest it would earn."
    )


if __name__ == "__main__":
    mcp.run()
