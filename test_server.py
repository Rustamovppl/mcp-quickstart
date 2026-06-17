"""Unit tests for the MCP tool implementations.

The tools are plain functions registered with FastMCP, so we call them directly.
"""
import math
from datetime import datetime

import pytest

from server import (
    compound_interest,
    loan_payment,
    moving_average,
    percentage_change,
    summary_stats,
    utc_now,
)


def test_summary_stats():
    s = summary_stats([1, 2, 3, 4])
    assert s["count"] == 4
    assert s["mean"] == 2.5
    assert s["median"] == 2.5
    assert math.isclose(s["stdev"], 1.1180339887, rel_tol=1e-6)


def test_summary_stats_empty():
    with pytest.raises(ValueError):
        summary_stats([])


def test_compound_interest_monthly():
    # 1000 at 12% APR compounded monthly for 1 year -> 1000 * 1.01**12.
    out = compound_interest(1000, 0.12, 1)
    assert out["final_amount"] == pytest.approx(1126.83, abs=0.01)
    assert out["interest_earned"] == pytest.approx(126.83, abs=0.01)


def test_compound_interest_zero_rate():
    out = compound_interest(1000, 0.0, 5)
    assert out["final_amount"] == 1000.0
    assert out["interest_earned"] == 0.0


def test_compound_interest_rejects_negative():
    with pytest.raises(ValueError):
        compound_interest(-1, 0.05, 1)


def test_loan_payment():
    out = loan_payment(10000, 0.06, 12)
    assert out["monthly_payment"] == pytest.approx(860.66, abs=0.01)
    assert out["total_interest"] == pytest.approx(out["total_paid"] - 10000, abs=0.01)


def test_loan_payment_zero_rate():
    out = loan_payment(1200, 0.0, 12)
    assert out["monthly_payment"] == 100.0
    assert out["total_interest"] == 0.0


def test_loan_payment_rejects_bad_input():
    with pytest.raises(ValueError):
        loan_payment(0, 0.05, 12)


def test_percentage_change():
    assert percentage_change(100, 150) == 50.0
    assert percentage_change(200, 100) == -50.0


def test_percentage_change_rejects_zero():
    with pytest.raises(ValueError):
        percentage_change(0, 10)


def test_moving_average():
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]
    assert moving_average([5, 5, 5], 3) == [5.0]


def test_moving_average_rejects_bad_window():
    with pytest.raises(ValueError):
        moving_average([1, 2], 5)


def test_utc_now_is_iso():
    # Should parse back without error.
    datetime.fromisoformat(utc_now())
