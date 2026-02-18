"""
Comprehensive Regression Test Suite
Tests all functionality to ensure nothing broke
"""

import requests
import json
import time

API_BASE = "http://127.0.0.1:8000"


def test_health_endpoint():
    """Test basic health check"""
    print("\n1. Testing /health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}")
            return True
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False


def test_feature_flags():
    """Test feature flags endpoint"""
    print("\n2. Testing /api/feature-flags endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/feature-flags", timeout=5)
        if response.status_code == 200:
            flags = response.json()
            multilingual = flags.get("multilingual_voice", False)
            print(f"   ✅ Feature flags retrieved")
            print(f"   multilingual_voice: {multilingual}")
            return multilingual == True
        else:
            print(f"   ❌ Feature flags failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Feature flags error: {e}")
        return False


def test_tts_english():
    """Test English TTS (baseline)"""
    print("\n3. Testing English TTS...")
    try:
        response = requests.post(
            f"{API_BASE}/generate/speech",
            json={
                "text": "Pneumonia typically presents with cough and fever.",
                "language": "en",
            },
            timeout=10,
            stream=True,
        )
        if response.status_code == 200:
            chunks = list(response.iter_content(chunk_size=8192))
            print(f"   ✅ English TTS works - {len(chunks)} chunks")
            return True
        else:
            print(f"   ❌ English TTS failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ English TTS error: {e}")
        return False


def test_tts_chinese():
    """Test Chinese TTS (previously failing)"""
    print("\n4. Testing Chinese TTS...")
    try:
        response = requests.post(
            f"{API_BASE}/generate/speech",
            json={"text": "肺炎通常表现为咳嗽和发热。", "language": "zh"},
            timeout=10,
            stream=True,
        )
        if response.status_code == 200:
            chunks = list(response.iter_content(chunk_size=8192))
            print(f"   ✅ Chinese TTS works - {len(chunks)} chunks")
            return True
        else:
            print(f"   ❌ Chinese TTS failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                pass
            return False
    except Exception as e:
        print(f"   ❌ Chinese TTS error: {e}")
        return False


def test_tts_hindi():
    """Test Hindi TTS (previously failing)"""
    print("\n5. Testing Hindi TTS...")
    try:
        response = requests.post(
            f"{API_BASE}/generate/speech",
            json={
                "text": "निमोनिया आमतौर पर खांसी और बुखार के साथ प्रस्तुत होता है।",
                "language": "hi",
            },
            timeout=10,
            stream=True,
        )
        if response.status_code == 200:
            chunks = list(response.iter_content(chunk_size=8192))
            print(f"   ✅ Hindi TTS works - {len(chunks)} chunks")
            return True
        else:
            print(f"   ❌ Hindi TTS failed: {response.status_code}")
            try:
                print(f"   Error: {response.json()}")
            except:
                pass
            return False
    except Exception as e:
        print(f"   ❌ Hindi TTS error: {e}")
        return False


def test_tts_spanish():
    """Test Spanish TTS"""
    print("\n6. Testing Spanish TTS...")
    try:
        response = requests.post(
            f"{API_BASE}/generate/speech",
            json={
                "text": "La neumonía típicamente presenta tos y fiebre.",
                "language": "es",
            },
            timeout=10,
            stream=True,
        )
        if response.status_code == 200:
            chunks = list(response.iter_content(chunk_size=8192))
            print(f"   ✅ Spanish TTS works - {len(chunks)} chunks")
            return True
        else:
            print(f"   ❌ Spanish TTS failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Spanish TTS error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("VoxRay AI - Comprehensive Regression Test Suite")
    print("=" * 60)

    results = {
        "Health Check": test_health_endpoint(),
        "Feature Flags": test_feature_flags(),
        "English TTS": test_tts_english(),
        "Chinese TTS": test_tts_chinese(),
        "Hindi TTS": test_tts_hindi(),
        "Spanish TTS": test_tts_spanish(),
    }

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} - {status}")

    all_passed = all(results.values())
    critical_passed = results["Chinese TTS"] and results["Hindi TTS"]

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - No regressions detected!")
    elif critical_passed:
        print("⚠️  CRITICAL FIXES WORKING - Chinese & Hindi TTS now functional")
        print("   Some other tests failed - review above")
    else:
        print("❌ CRITICAL TESTS FAILED - Chinese/Hindi TTS still broken")
    print("=" * 60)
