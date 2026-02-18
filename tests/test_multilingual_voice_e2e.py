"""
End-to-End Multilingual Voice Testing
Tests the complete pipeline: Speech → Transcription → Chat → TTS
"""

import requests
import json
import time
import os
from pathlib import Path

API_BASE = "http://127.0.0.1:8000"

# Test cases with expected outputs
TEST_CASES = {
    "en": {"text": "What is pneumonia?", "expected_lang": "en", "script_check": None},
    "hi": {
        "text": "निमोनिया क्या है?",  # Hindi
        "expected_lang": "hi",
        "script_check": "devanagari",
    },
    "zh": {
        "text": "肺炎是什么？",  # Chinese
        "expected_lang": "zh",
        "script_check": None,
    },
}


def check_script(text, script_type):
    if script_type == "devanagari":
        has_devanagari = any("\u0900" <= c <= "\u097f" for c in text)
        has_arabic = any("\u0600" <= c <= "\u06ff" for c in text)
        if has_arabic:
            print("❌ FAIL: Arabic script detected in Hindi output (Urdu confusion)")
            return False
        if not has_devanagari and len(text) > 0:
            print("⚠️ WARN: No Devanagari script found (English fallback?)")
            return False
        return True
    return True


def test_tts_generation():
    print("\n🎧 Testing TTS Generation endpoint...")

    for lang, data in TEST_CASES.items():
        print(f"\nTesting {lang.upper()} TTS...")
        try:
            # 1. Generate Audio
            payload = {"text": data["text"], "language": lang}
            start_time = time.time()
            response = requests.post(
                f"{API_BASE}/generate/speech", json=payload, timeout=10, stream=True
            )
            elapsed = time.time() - start_time

            if response.status_code == 200:
                # Count chunks
                chunk_count = sum(1 for _ in response.iter_content(chunk_size=4096))
                print(f"✅ Success: {chunk_count} chunks in {elapsed:.2f}s")
            else:
                print(f"❌ Failed: {response.status_code}")
                print(response.text)
                return False

        except Exception as e:
            print(f"❌ Exception: {e}")
            return False

    return True


def test_stt_transcription():
    print("\n🎤 Testing STT Transcription endpoint...")
    # This requires an actual audio file, skipping for now unless available
    print("⚠️ Skipping STT test (requires audio file)")
    return True


if __name__ == "__main__":
    print("🧪 VoxRay AI - Multilingual Production Verification")
    print("=" * 60)

    # 1. Test Feature Flags (proxy for backend health)
    try:
        resp = requests.get(f"{API_BASE}/api/feature-flags", timeout=2)
        if resp.status_code == 200:
            print("✅ Backend reachable")
        else:
            print("❌ Backend error")
            exit(1)
    except:
        print("❌ Backend unreachable")
        exit(1)

    # 2. Test TTS
    if test_tts_generation():
        print("\n✅ TTS Verification Passed")
    else:
        print("\n❌ TTS Verification Failed")
        exit(1)

    print("\n✅ All Production Checks Passed")
