import pytest
from pipeline.validation.fairness_indicators import compute_fairness


def test_missing_demographics():
    report = compute_fairness([0, 1], [0, 1], None)
    assert report.status == "skipped"
    assert "No demographic" in report.message


def test_empty_demographics():
    report = compute_fairness([0, 1], [0, 1], {})
    assert report.status == "skipped"


def test_valid_demographics():
    demos = {"gender": ["m", "f"], "age": [20, 30]}
    report = compute_fairness([0, 0], [0, 0], demos)
    assert report.status == "ok"
    assert "demographic_parity_diff" in report.metrics
