from __future__ import annotations
import os, json, hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class AuditLogger:
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.salt = os.getenv("AUDIT_SALT", "voxray_audit_salt")

    def _hash(self, value: str) -> str:
        return hashlib.sha256(f"{self.salt}{value}".encode()).hexdigest()[:16]

    def log_event(self, event: Dict[str, Any]) -> None:
        ts = datetime.utcnow().isoformat() + "Z"
        event["timestamp"] = ts
        filename = self.log_dir / f"audit-{datetime.utcnow().date().isoformat()}.jsonl"
        with filename.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

    def log_prediction(
        self,
        user_id: str,
        request_id: str,
        model_version: str,
        prediction: Dict[str, Any],
        input_hash: str,
        extra: Optional[Dict[str, Any]] = None,
    ):
        event = {
            "event_type": "prediction",
            "user_id_hash": self._hash(user_id),
            "request_id": request_id,
            "model_version": model_version,
            "input_hash": input_hash,
            "prediction": prediction,
        }
        if extra:
            event["extra"] = extra
        self.log_event(event)
