import requests
import json

try:
    response = requests.get("http://127.0.0.1:8000/api/feature-flags", timeout=2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        flags = response.json()
        print(f"\nFeature Flags:")
        print(json.dumps(flags, indent=2))
        print(f"\nmultilingual_voice = {flags.get('multilingual_voice', 'NOT FOUND')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Failed: {e}")
