"""Quick TTS test for Chinese and Hindi"""

import requests

API_BASE = "http://127.0.0.1:8000"

# Test Chinese
print("Testing Chinese (zh)...")
response = requests.post(
    f"{API_BASE}/generate/speech",
    json={"text": "肺炎通常表现为咳嗽和发热。", "language": "zh"},
    timeout=10,
    stream=True,
)
if response.status_code == 200:
    chunks = list(response.iter_content(chunk_size=8192))
    print(f"✅ Chinese SUCCESS - {len(chunks)} chunks")
else:
    print(f"❌ Chinese FAILED - Status {response.status_code}")
    print(response.text)

# Test Hindi
print("\nTesting Hindi (hi)...")
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
    print(f"✅ Hindi SUCCESS - {len(chunks)} chunks")
else:
    print(f"❌ Hindi FAILED - Status {response.status_code}")
    print(response.text)
