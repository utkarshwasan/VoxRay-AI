"""
VoxRay AI — Multilingual Fix Verification Tests

All runtime findings are incorporated:
- Latin text through hi-IN-SwaraNeural succeeds (27 chunks) — not blocked
- Arabic text through hi-IN-SwaraNeural raises NoAudioReceived — blocked with 422
- forced_decoder_ids alone prevents Urdu token — suppress_tokens omitted intentionally
- pytest.ini already has asyncio_mode = strict — no new config needed

Run: venv\Scripts\python.exe -m pytest tests/test_multilingual_fix.py -v
Auth: set VOXRAY_TEST_TOKEN=<your_stack_auth_jwt> in environment before running
"""

import unicodedata
import os
import httpx
import pytest
import pytest_asyncio

BASE_URL = os.getenv("VOXRAY_TEST_URL", "http://127.0.0.1:8000")
TEST_TOKEN = os.getenv("VOXRAY_TEST_TOKEN", "")


# ── Utilities ─────────────────────────────────────────────────────────────────


def detect_script(text: str) -> str:
    counts = {"devanagari": 0, "arabic": 0, "latin": 0}
    for ch in text:
        n = unicodedata.name(ch, "")
        if "DEVANAGARI" in n:
            counts["devanagari"] += 1
        elif "ARABIC" in n:
            counts["arabic"] += 1
        elif ch.isascii() and ch.isalpha():
            counts["latin"] += 1
    dominant = max(counts, key=counts.get)
    return dominant if counts[dominant] > 0 else "unknown"


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient(timeout=30) as c:
        yield c


@pytest.fixture
def auth_headers():
    if not TEST_TOKEN:
        pytest.skip("VOXRAY_TEST_TOKEN not set — skipping auth-required tests")
    return {"Authorization": f"Bearer {TEST_TOKEN}"}


# ── Unit: Script Detection (no server needed) ─────────────────────────────────


def test_detect_devanagari():
    assert detect_script("फेफड़ों में कैंसर") == "devanagari"


def test_detect_arabic():
    assert detect_script("اس بماری کے سمٹمس") == "arabic"


def test_detect_latin():
    assert detect_script("lung cancer symptoms") == "latin"


def test_urdu_not_devanagari():
    """Core regression: Urdu text must never be detected as Devanagari."""
    assert detect_script("اس بماری کے سمٹمس کیا ہوتے ہیں") != "devanagari"


def test_empty_text_unknown():
    assert detect_script("") == "unknown"


def test_devanagari_dominant_with_digits():
    """Mixed text with digits — Devanagari should still dominate."""
    assert detect_script("फेफड़ों 100% कैंसर") == "devanagari"


# ── Integration: Endpoints ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get(f"{BASE_URL}/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_feature_flags_now_exists(client):
    """Was 404 before fix — must return 200 with expected keys."""
    r = await client.get(f"{BASE_URL}/api/feature-flags")
    assert r.status_code == 200, "feature-flags route still missing"
    data = r.json()
    assert data.get("multilingual_stt") is True
    assert data.get("multilingual_tts") is True


# ── TTS Tests ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tts_english(client):
    r = await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "The scan shows lung cancer findings.", "language": "en"},
    )
    assert r.status_code == 200
    assert len(r.content) > 200


@pytest.mark.asyncio
@pytest.mark.skip(reason="Hindi disabled — whisper-base STT limitation")
async def test_tts_hindi_devanagari_succeeds(client):
    """Hindi voice with correct Devanagari text must produce audio."""
    r = await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "फेफड़ों के कैंसर के लक्षण क्या हैं", "language": "hi"},
    )
    assert r.status_code == 200
    assert len(r.content) > 200


@pytest.mark.asyncio
@pytest.mark.skip(reason="Hindi disabled — whisper-base STT limitation")
async def test_tts_hindi_latin_also_succeeds(client):
    """
    Runtime-verified: Latin text through hi-IN-SwaraNeural produces 27 chunks.
    The pre-flight check must NOT block this — only Arabic is blocked.
    If this returns 422, TTS_INCOMPATIBLE_SCRIPTS is over-blocking.
    """
    r = await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "The lungs show signs of cancer.", "language": "hi"},
    )
    assert r.status_code == 200, (
        f"Got {r.status_code} — Latin text through Hindi voice should succeed. "
        "TTS_INCOMPATIBLE_SCRIPTS is blocking too aggressively."
    )


@pytest.mark.asyncio
@pytest.mark.skip(reason="Hindi disabled — whisper-base STT limitation")
async def test_tts_hindi_arabic_script_blocked(client):
    """
    Arabic/Urdu-script text through hi-IN-SwaraNeural must return 422.
    Without the pre-flight check this causes NoAudioReceived + ASGI crash.
    """
    r = await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "اس بماری کے سمٹمس کیا ہوتے ہیں", "language": "hi"},
    )
    assert r.status_code == 422, (
        f"Expected 422 SCRIPT_MISMATCH, got {r.status_code}. "
        "Pre-flight TTS script check is missing or not applying TTS_INCOMPATIBLE_SCRIPTS."
    )
    assert r.json().get("error") == "SCRIPT_MISMATCH"


@pytest.mark.asyncio
@pytest.mark.skip(reason="Hindi disabled — whisper-base STT limitation")
async def test_tts_server_survives_bad_input(client):
    """
    Most critical stability test.
    Sends Arabic text to Hindi voice (was crashing ASGI via 'raise' in generator).
    Server must be alive after — confirms raise→return fix is applied.
    """
    await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "اس بماری", "language": "hi"},
        timeout=10,
    )
    r = await client.get(f"{BASE_URL}/health")
    assert r.status_code == 200, (
        "Server CRASHED after bad TTS input. "
        "The raise→return fix inside audio_stream() was not applied."
    )


@pytest.mark.asyncio
async def test_tts_french(client):
    r = await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "Les résultats de l'analyse pulmonaire", "language": "fr"},
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_tts_german(client):
    r = await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "Die Lunge zeigt Anzeichen von Krebs", "language": "de"},
    )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_tts_spanish(client):
    r = await client.post(
        f"{BASE_URL}/generate/speech",
        json={"text": "Los pulmones muestran signos de cáncer", "language": "es"},
    )
    assert r.status_code == 200


# ── Chat Language Enforcement ─────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.skip(reason="Hindi disabled — whisper-base STT limitation")
async def test_chat_hindi_responds_devanagari(client, auth_headers):
    """
    Core regression test for the full bug cascade.
    Sends Urdu-script text (simulating the STT bug) with language=hi.
    LLM must respond in Devanagari because LANG_LLM_INSTRUCTIONS forces it.
    """
    r = await client.post(
        f"{BASE_URL}/chat",
        json={
            "message": "اس بماری کے سمٹمس کیا ہوتے ہیں",
            "context": "Diagnosis: 04_LUNG_CANCER, Confidence: 100.0%",
            "history": [],
            "language": "hi",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    response_text = r.json()["response"]
    script = detect_script(response_text)
    assert script == "devanagari", (
        f"LLM responded in '{script}' not 'devanagari'.\n"
        f"Response: {response_text[:120]}\n"
        "LANG_LLM_INSTRUCTIONS not injected into system prompt, or language field not passed."
    )


@pytest.mark.asyncio
async def test_chat_language_field_does_not_break_english(client, auth_headers):
    """Verify the new language field doesn't break existing English chat flow."""
    r = await client.post(
        f"{BASE_URL}/chat",
        json={
            "message": "What are the symptoms of lung cancer?",
            "context": "Diagnosis: 04_LUNG_CANCER, Confidence: 100.0%",
            "history": [],
            "language": "en",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200, f"Chat rejected language field: {r.text}"
    assert detect_script(r.json()["response"]) == "latin"


@pytest.mark.asyncio
async def test_chat_confidence_reaches_llm(client, auth_headers):
    """
    Regression for the stale closure bug where confidence showed as 0.0%.
    Sends 100.0% confidence — response must not contain '0%' as the primary value.
    """
    r = await client.post(
        f"{BASE_URL}/chat",
        json={
            "message": "How confident is the AI in this result?",
            "context": "Diagnosis: 04_LUNG_CANCER, Confidence: 100.0%",
            "history": [],
            "language": "en",
        },
        headers=auth_headers,
    )
    assert r.status_code == 200
    text = r.json()["response"]
    # LLM receiving 0.0% would say "0%" or "no confidence" — 100% would say "100"
    assert "100" in text or "high" in text.lower() or "certain" in text.lower(), (
        f"LLM response suggests confidence was 0.0%: {text[:150]}"
    )
