from __future__ import annotations
import os, hashlib
from typing import Dict, Any


class DicomAnonymizer:
    def __init__(self, salt: str | None = None):
        self.salt = salt or os.getenv("ANONYMIZATION_SALT", "voxray_default_salt")

    def hash_identifier(self, value: str) -> str:
        return hashlib.sha256(f"{self.salt}{value}".encode()).hexdigest()[:16]

    def anonymize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        meta = dict(metadata or {})
        pid = str(meta.get("patient_id", ""))
        if pid:
            meta["patient_id_hash"] = self.hash_identifier(pid)
        meta.pop("patient_id", None)
        return meta
