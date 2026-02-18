from __future__ import annotations
from typing import Dict

DEFAULT_CORRECTIONS: Dict[str, str] = {
    "plural effusion": "pleural effusion",
    "consultation": "consolidation",
    "ammonia": "pneumonia",
    "numonia": "pneumonia",
    "nemomia": "pneumonia",
    "cardiomegaly": "cardiomegaly",
    "atelectasis": "atelectasis",
    "nodule": "nodule",
    "mass": "mass",
    "infiltration": "infiltration",
}


class MedicalVocabulary:
    def __init__(self, corrections: Dict[str, str] | None = None):
        self.corrections = corrections or DEFAULT_CORRECTIONS

    def post_process(self, text: str) -> str:
        if not text:
            return ""
        out = text
        # Simple case-insensitive replacement for now, can be improved with regex
        for wrong, right in self.corrections.items():
            # A more robust implementation would use regex to match whole words/phrases ignoring case
            # For this MVP, we'll do a simple lower-case check or just replace.
            # To preserve case of original text while matching case-insensitively is harder.
            # We'll stick to a simple replace for known lower-case phrases for now,
            # assuming input might be lower-cased by STT or we tolerate some casing changes.

            # Implementation Choice:
            # STT usually returns consistent casing. We will do a case-insensitive match
            # but for simplicity in this MVP:
            if wrong in out.lower():
                # This is a bit naive (replaces substrings) but safe for these specific medical terms
                # A better approach (regex with word boundaries): re.sub(r'\b' + re.escape(wrong) + r'\b', right, out, flags=re.IGNORECASE)
                # keeping it dependency-free and simple as requested.
                import re

                out = re.sub(r"(?i)\b" + re.escape(wrong) + r"\b", right, out)
        return out
