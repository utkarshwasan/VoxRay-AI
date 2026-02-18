from __future__ import annotations
from typing import Dict, Any, Optional


class FHIRTransformer:
    """
    Minimal transformer: VoxRay result -> FHIR DiagnosticReport JSON.
    """

    def diagnosis_to_snomed(self, diagnosis: str) -> Optional[Dict[str, str]]:
        # Minimal mapping (extend later)
        mapping = {
            "06_PNEUMONIA": {
                "system": "http://snomed.info/sct",
                "code": "233604007",
                "display": "Pneumonia",
            },
            "04_LUNG_CANCER": {
                "system": "http://snomed.info/sct",
                "code": "363346000",
                "display": "Malignant neoplasm of lung",
            },
            "05_FRACTURED": {
                "system": "http://snomed.info/sct",
                "code": "125605004",
                "display": "Fracture of bone",
            },
        }
        return mapping.get(diagnosis)

    def to_diagnostic_report(
        self, patient_ref: str, conclusion: str, diagnosis: str
    ) -> Dict[str, Any]:
        snomed = self.diagnosis_to_snomed(diagnosis)
        report: Dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "status": "final",
            "subject": {"reference": patient_ref},
            "conclusion": conclusion,
        }
        if snomed:
            report["conclusionCode"] = [{"coding": [snomed]}]
        return report
