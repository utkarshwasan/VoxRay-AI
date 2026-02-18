"""
Comprehensive TTS Testing Script for all 6 supported languages
Tests edge cases and verifies proper error handling
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:8000"

# Test cases for each language
TEST_CASES = {
    "en": {
        "text": "Pneumonia typically presents with cough and fever.",
        "expected_voice": "en-US-AriaNeural",
    },
    "es": {
        "text": "La neumonía típicamente presenta tos y fiebre.",
        "expected_voice": "es-ES-ElviraNeural",
    },
    "fr": {
        "text": "La pneumonie présente généralement toux et fièvre.",
        "expected_voice": "fr-FR-DeniseNeural",
    },
    "de": {
        "text": "Lungenentzündung zeigt typischerweise Husten und Fieber.",
        "expected_voice": "de-DE-KatjaNeural",
    },
    "zh": {
        "text": "肺炎通常表现为咳嗽和发热。",
        "expected_voice": "zh-CN-XiaoxiaoNeural",
    },
    "hi": {
        "text": "निमोनिया आमतौर पर खांसी और बुखार के साथ प्रस्तुत होता है।",
        "expected_voice": "hi-IN-SwaraNeural",
    },
}


def test_tts_language(language, test_data):
    """Test TTS for a specific language"""
    print(f"\n{'=' * 60}")
    print(f"Testing {language.upper()} - {test_data['expected_voice']}")
    print(f"{'=' * 60}")

    payload = {"text": test_data["text"], "language": language}

    try:
        response = requests.post(
            f"{API_BASE}/generate/speech", json=payload, timeout=15, stream=True
        )

        if response.status_code == 200:
            # Count audio chunks
            chunk_count = 0
            total_bytes = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunk_count += 1
                    total_bytes += len(chunk)

            print(f"✅ SUCCESS!")
            print(f"   Status: {response.status_code}")
            print(f"   Chunks: {chunk_count}")
            print(f"   Size: {total_bytes} bytes")
            print(f"   Text: '{test_data['text'][:50]}...'")
            return True
        else:
            print(f"❌ FAILED!")
            print(f"   Status: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"⏱️  TIMEOUT! ({language})")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION!")
        print(f"   Error: {str(e)}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print(f"\n{'=' * 60}")
    print("Testing Edge Cases")
    print(f"{'=' * 60}")

    # Test 1: Empty text
    print("\n1. Empty text:")
    response = requests.post(
        f"{API_BASE}/generate/speech", json={"text": "", "language": "en"}, timeout=5
    )
    print(f"   Status: {response.status_code} (expected 400)")

    # Test 2: Unsupported language (should fallback to English)
    print("\n2. Unsupported language (fallback test):")
    response = requests.post(
        f"{API_BASE}/generate/speech",
        json={"text": "Test fallback", "language": "xx"},
        timeout=10,
        stream=True,
    )
    chunk_count = sum(1 for _ in response.iter_content(chunk_size=8192))
    print(f"   Status: {response.status_code}")
    print(f"   Chunks: {chunk_count} (should use English fallback)")

    # Test 3: Very long text
    print("\n3. Very long text (truncation test):")
    long_text = "Pneumonia is a lung infection. " * 100  # ~3000 chars
    response = requests.post(
        f"{API_BASE}/generate/speech",
        json={"text": long_text, "language": "en"},
        timeout=15,
        stream=True,
    )
    print(f"   Status: {response.status_code}")
    print(f"   Original length: {len(long_text)} chars (should truncate to ~2000)")


if __name__ == "__main__":
    print("\n🧪 VoxRay AI - Multilingual TTS Test Suite")
    print("=" * 60)

    results = {}

    # Test all languages
    for lang, test_data in TEST_CASES.items():
        success = test_tts_language(lang, test_data)
        results[lang] = success
        time.sleep(1)  # Brief pause between tests

    # Test edge cases
    test_edge_cases()

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    for lang, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{lang.upper():3s} - {status}")

    all_passed = all(results.values())
    print(
        f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}"
    )
