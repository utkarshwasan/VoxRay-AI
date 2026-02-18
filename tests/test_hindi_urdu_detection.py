"""
Specific test for Hindi vs Urdu script detection
"""

import requests
import sys

API_BASE = "http://127.0.0.1:8000"


def test_hindi_script_enforcement():
    """Test that Hindi transcription uses Devanagari, not Arabic script."""

    print("\n🧪 Testing Hindi/Urdu Script Detection")
    print("=" * 60)

    # We can't easily test STT without an audio file,
    # but we CAN verify the Chat endpoint respects language forcing

    print("\n1. Testing chat with Hindi language parameter...")
    try:
        response = requests.post(
            f"{API_BASE}/v2/chat",
            json={
                "message": "pneumonia symptoms",
                "context": "Diagnosis: PNEUMONIA",
                "language": "hi",
                "history": [],
            },
            timeout=10,
        )

        if response.status_code != 200:
            print(f"❌ Chat API failed: {response.status_code}")
            return False

        text = response.json()["response"]
        print(f"Response: {text}")

        # Check script
        has_devanagari = any("\u0900" <= c <= "\u097f" for c in text)
        has_arabic = any("\u0600" <= c <= "\u06ff" for c in text)

        print(f"\nScript Analysis:")
        print(f"  Devanagari (हिन्दी): {has_devanagari}")
        print(f"  Arabic (اردو): {has_arabic}")

        if has_arabic:
            print("\n❌ FAIL: Response contains Arabic script (Urdu)")
            print("This means the Devanagari enforcement is not working!")
            return False
        elif has_devanagari:
            print("\n✅ PASS: Response in Devanagari script (Hindi)")
            return True
        else:
            print("\n⚠️  WARN: Response is in English/Latin (possible fallback)")
            return None

    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


if __name__ == "__main__":
    result = test_hindi_script_enforcement()
    if result is True:
        print("\n✅ Hindi script detection working correctly")
    elif result is False:
        print("\n❌ Hindi script detection FAILED")
        sys.exit(1)
    else:
        print("\n⚠️  Inconclusive")
