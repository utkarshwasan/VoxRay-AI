import pytest
import yaml
from pipeline.validation.retraining_trigger import RetrainingTrigger


@pytest.fixture
def thresholds_file(tmp_path):
    f = tmp_path / "thresholds.yaml"
    config = {
        "thresholds": {
            "accuracy_min": 0.85,
            "drift_score_max": 0.3,
            "false_positive_rate_max_delta": 0.10,
        },
        "actions": {"on_fp_rate_breach": "alert_only"},
    }
    f.write_text(yaml.dump(config))
    return str(f)


def test_no_trigger(thresholds_file):
    trigger = RetrainingTrigger(thresholds_file)
    metrics = {"accuracy": 0.90, "drift_score": 0.1, "false_positive_rate_delta": 0.05}
    decision = trigger.evaluate(metrics)
    assert not decision.should_retrain
    assert "No triggers" in decision.reason


def test_accuracy_trigger(thresholds_file):
    trigger = RetrainingTrigger(thresholds_file)
    metrics = {
        "accuracy": 0.80,  # < 0.85
        "drift_score": 0.1,
    }
    decision = trigger.evaluate(metrics)
    assert decision.should_retrain
    assert "accuracy 0.8000 < 0.85" in decision.reason


def test_drift_trigger(thresholds_file):
    trigger = RetrainingTrigger(thresholds_file)
    metrics = {
        "accuracy": 0.90,
        "drift_score": 0.5,  # > 0.3
    }
    decision = trigger.evaluate(metrics)
    assert decision.should_retrain
    assert "drift_score 0.5" in decision.reason


def test_fp_alert_only(thresholds_file):
    trigger = RetrainingTrigger(thresholds_file)
    metrics = {
        "accuracy": 0.90,
        "drift_score": 0.1,
        "false_positive_rate_delta": 0.15,  # > 0.10
    }
    decision = trigger.evaluate(metrics)
    # actions says "alert_only", so should_retrain should remains False (unless logic overridden)
    # Our impl: "if action == 'trigger_retrain': should = True"
    assert not decision.should_retrain
    assert "false_positive_rate_delta" in decision.reason
    assert "(alert_only)" in decision.reason
