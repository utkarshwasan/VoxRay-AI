from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class DicomExtractResult:
    ok: bool
    message: str
    image_rgb: Optional[np.ndarray] = None  # HxWx3 uint8
    metadata: Optional[Dict[str, Any]] = None


class DICOMHandler:
    def read_and_extract(self, file_bytes: bytes) -> DicomExtractResult:
        try:
            import pydicom
        except ImportError:
            return DicomExtractResult(False, "pydicom not installed")

        try:
            from io import BytesIO

            ds = pydicom.dcmread(BytesIO(file_bytes), force=True)

            metadata = {
                "study_instance_uid": str(ds.get((0x0020, 0x000D), "")),
                "modality": str(ds.get((0x0008, 0x0060), "")),
                "study_date": str(ds.get((0x0008, 0x0020), "")),
                "patient_id": str(
                    ds.get((0x0010, 0x0020), "")
                ),  # must be hashed before logging/returning
            }

            if not hasattr(ds, "pixel_array"):
                return DicomExtractResult(
                    False, "DICOM has no pixel data", metadata=metadata
                )

            arr = ds.pixel_array.astype(np.float32)

            # Normalize to 0..255
            arr = arr - np.min(arr)
            denom = np.max(arr) if np.max(arr) > 0 else 1.0
            arr = (arr / denom) * 255.0
            arr = arr.astype(np.uint8)

            # Convert grayscale to RGB
            if arr.ndim == 2:
                rgb = np.stack([arr, arr, arr], axis=-1)
            elif arr.ndim == 3 and arr.shape[-1] == 3:
                rgb = arr
            else:
                # Fallback: attempt squeeze
                arr2 = np.squeeze(arr)
                if arr2.ndim == 2:
                    rgb = np.stack([arr2, arr2, arr2], axis=-1)
                else:
                    return DicomExtractResult(
                        False,
                        f"Unsupported pixel array shape: {arr.shape}",
                        metadata=metadata,
                    )

            return DicomExtractResult(True, "OK", image_rgb=rgb, metadata=metadata)

        except Exception as e:
            return DicomExtractResult(False, f"DICOM parsing failed: {e}")
