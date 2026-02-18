import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.getcwd())

try:
    print("Attempting imports...")
    from backend.api import v2

    print(" Imported backend.api.v2")
    from backend.clinical.dicom import dicom_handler

    print(" Imported backend.clinical.dicom.dicom_handler")
    from backend.security import anonymizer

    print(" Imported backend.security.anonymizer")
    from backend.audit import audit_logger

    print(" Imported backend.audit.audit_logger")

    # Try initializing classes
    dh = dicom_handler.DICOMHandler()
    an = anonymizer.DicomAnonymizer()
    al = audit_logger.AuditLogger()
    print(" Classes initialized successfully")

    print("IMPORTS SUCCESS")
except Exception as e:
    print(f"IMPORTS FAILED: {e}")
    import traceback

    traceback.print_exc()
