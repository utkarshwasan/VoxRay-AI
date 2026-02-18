import os
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.api.main import app
# import backend.api.routes.v2_clinical  # Removed unused import, patching works via string path


client = TestClient(app)
FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


# --- Mocks ---
@pytest.fixture
def mock_auth():
    """Mock authentication for successful tests"""
    from backend.api.deps import get_current_user

    app.dependency_overrides[get_current_user] = lambda: {"sub": "test_user_123"}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def mock_model():
    """Mock ML model to avoid loading real heavy model"""
    mock_pred = MagicMock()
    # Return [0.1, 0.8, 0.1] -> Max index 1 (Pneumonia in mocked list)
    mock_pred.predict.return_value = [[0.1, 0.8, 0.1]]

    with patch("backend.api.main.medical_model", mock_pred) as m_model:
        # Also patch class names in main module
        with patch(
            "backend.api.main.MEDICAL_CLASS_NAMES", ["Normal", "Pneumonia", "Other"]
        ):
            yield m_model


@pytest.fixture
def mock_dicom_bytes():
    """Create a dummy DICOM byte stream structure or load fixture"""
    # Since we can't easily generate a valid binary DICOM without pydicom installed in test env
    # (and we want to test without relying on external fixtures if possible),
    # we will mock the dcmread in the handler OR rely on a real file if available.
    # But wait, we want to test the full stack.
    # Let's mock `backend.clinical.dicom.dicom_handler.pydicom`?
    # No, that's too deep.
    # Start simple: Mock `dicom_handler.read_and_extract`
    pass


@pytest.fixture
def mock_dicom_handler():
    from backend.clinical.dicom.dicom_handler import DicomExtractResult

    # Patch new location in v2_clinical
    with patch(
        "backend.api.routes.v2_clinical.dicom_handler.read_and_extract"
    ) as mock_read:
        # Return success with a random image
        rgb = np.zeros((224, 224, 3), dtype=np.uint8)
        mock_read.return_value = DicomExtractResult(
            ok=True,
            message="OK",
            image_rgb=rgb,
            metadata={
                "patient_id": "PID123",
                "modality": "DX",
                "study_instance_uid": "1.2.3",
            },
        )
        yield mock_read


# --- Tests ---


def test_dicom_endpoint_disabled_by_default(mock_auth):
    """Should return 503 if FF_DICOM_SUPPORT is false (default)"""
    with patch.dict(os.environ, {"FF_DICOM_SUPPORT": "false"}):
        # Reload flags if necessary, but require_feature checks dynamically
        # Actually require_feature uses check_flag -> _feature_flags_instance
        # We need to reload the singleton instance
        from backend.core.feature_flags import get_feature_flags

        get_feature_flags().reload()

        # Valid dummy content type
        files = {"dicom_file": ("test.dcm", b"FAKE_DICOM_BYTES", "application/dicom")}
        r = client.post("/v2/predict/dicom", files=files)

        assert r.status_code == 503
        assert r.json()["detail"]["error"] == "FEATURE_NOT_ENABLED"


def test_dicom_endpoint_success_flow(mock_auth, mock_model, mock_dicom_handler):
    """Should return 200 with diagnosis if enabled"""
    with patch.dict(
        os.environ,
        {
            "FF_DICOM_SUPPORT": "true",
            "FF_DATA_ANONYMIZATION": "true",
            "FF_AUDIT_LOGGING": "true",
        },
    ):
        from backend.core.feature_flags import get_feature_flags

        get_feature_flags().reload()

        files = {"dicom_file": ("test.dcm", b"FAKE_DICOM_BYTES", "application/dicom")}
        r = client.post("/v2/predict/dicom", files=files)

        assert r.status_code == 200
        data = r.json()
        assert data["diagnosis"] == "Pneumonia"
        assert data["image_extracted"] is True
        assert data["anonymization_applied"] is True

        # Check anonymization
        assert "patient_id" not in data["dicom_metadata"]
        assert "patient_id_hash" in data["dicom_metadata"]


def test_dicom_parsing_error_handling(mock_auth):
    """Should return 422 if DICOM handler fails (real handler or mocked fail)"""
    with patch.dict(os.environ, {"FF_DICOM_SUPPORT": "true"}):
        from backend.core.feature_flags import get_feature_flags

        get_feature_flags().reload()

        # We rely on real handler here failing on junk bytes
        # Just need to ensure main_app.medical_model is not None for the check
        with patch("backend.api.main.medical_model", MagicMock()):
            files = {"dicom_file": ("test.dcm", b"NOT_A_DICOM", "application/dicom")}
            r = client.post("/v2/predict/dicom", files=files)

            # If pydicom installed, it returns DicomExtractResult(False...).
            # If not installed, same.
            # The endpoint maps ok=False to 422.
            assert r.status_code == 422
            assert "processing failed" in r.json()["detail"]
