import importlib.util
import sys

FORBIDDEN_PACKAGES = ["gradio", "gradio_client"]

found_forbidden = []
for package in FORBIDDEN_PACKAGES:
    spec = importlib.util.find_spec(package)
    if spec is not None:
        found_forbidden.append(package)

if found_forbidden:
    print(f"❌ Forbidden dependencies present: {found_forbidden}")
    print(
        "Please uninstall them to prevent dependency conflicts (e.g. pydantic version mismatch)."
    )
    sys.exit(1)
else:
    print("✅ No forbidden deps detected")
    sys.exit(0)
