import traceback
import sys

print(f"Python: {sys.version}")
try:
    print("Attempting to import fastapi.testclient.TestClient...")
    from fastapi.testclient import TestClient

    print("SUCCESS: TestClient imported.")
except ImportError:
    print("FAILED: ImportError caught.")
    traceback.print_exc()
except Exception:
    print("FAILED: Generic Exception.")
    traceback.print_exc()
