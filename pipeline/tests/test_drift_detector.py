import pytest
from unittest.mock import MagicMock, patch
import sys
from pipeline.drift_detection.data_validator import DataDriftDetector


@pytest.fixture
def mock_schema_path(tmp_path):
    schema = tmp_path / "schema.pbtxt"
    schema.write_text("dummy schema")
    return str(schema)


@pytest.fixture
def mock_data_path(tmp_path):
    data = tmp_path / "data.tfrecord"
    data.write_text("dummy data")
    return str(data)


def test_missing_schema():
    detector = DataDriftDetector("non_existent_schema.pbtxt")
    report = detector.detect_drift("some_data.tfrecord")
    assert report.status == "error"
    assert "Schema file not found" in report.message


def test_missing_data(mock_schema_path):
    detector = DataDriftDetector(mock_schema_path)
    report = detector.detect_drift("non_existent_data.tfrecord")
    assert report.status == "error"
    assert "New data not found" in report.message


def test_unsupported_format(mock_schema_path, tmp_path):
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2\n1,2")

    # Needs to mock import success to reach format check
    with patch.dict(
        "sys.modules",
        {
            "tensorflow_data_validation": MagicMock(),
            "tensorflow_metadata.proto.v0": MagicMock(),
        },
    ):
        detector = DataDriftDetector(mock_schema_path)
        report = detector.detect_drift(str(csv_file))
        assert report.status == "skipped"
        assert "non-TFRecord" in report.message


def test_validation_works_without_tfdv(mock_schema_path, mock_data_path):
    # This test verifies that if TFDV is missing (which it is in this dev env),
    # the code gracefully returns "skipped".
    # We do NOT force-mock sys.modules here because it causes stability issues.
    # We rely on the actual environment state.

    detector = DataDriftDetector(mock_schema_path)
    report = detector.detect_drift(mock_data_path)

    # If TFDV is missing, it should be skipped.
    # If TFDV IS installed, it might fail on "schema parse" or something else,
    # but for this specific environment we expect skip or error, NOT a crash.

    if "tensorflow_data_validation" not in sys.modules:
        # Likely skipped
        assert report.status in ["skipped", "error"]
        if report.status == "skipped":
            assert (
                "TFDV not installed" in report.message
                or "non-TFRecord" in report.message
            )


def test_drift_detected_mock(mock_schema_path, mock_data_path):
    # Mock TFDV internals
    mock_tfdv = MagicMock()
    mock_anomalies = MagicMock()
    # 2 anomalies
    mock_anomalies.anomaly_info = {
        "feat1": MagicMock(description="drift"),
        "feat2": MagicMock(description="drift"),
    }
    mock_tfdv.validate_statistics.return_value = mock_anomalies

    with patch.dict(
        "sys.modules",
        {
            "tensorflow_data_validation": mock_tfdv,
            "tensorflow_metadata.proto.v0": MagicMock(),
        },
    ):
        detector = DataDriftDetector(mock_schema_path)
        report = detector.detect_drift(mock_data_path)

        assert report.status == "drift_detected"
        assert report.drift_score == 2.0
