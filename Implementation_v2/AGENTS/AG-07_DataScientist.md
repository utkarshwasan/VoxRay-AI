## File 18: `Implementation_v2/AGENTS/AG-07_DataScientist.md`

````markdown
# AG-07: Data Scientist (Dataset, Validation, Augmentation, Provenance)

**Role:** Dataset management + validation + generalizability  
**Phase:** 5  
**Duration:** Days 15–20  
**Dependencies:**

- AG-01 model interfaces ready
- AG-02 pipeline tools ready (drift/validation hooks)

**Blocking:** NO for shipping v2.0 (but important for clinical credibility)

---

## Prompt to paste into Antigravity (manual allocation)

You are AG-07 (DataScientist). You must:

1. Not introduce real patient data into repo.
2. Implement augmentation and validation code that can run locally and skip gracefully when datasets are absent.
3. Produce reproducible reports and provenance metadata.

---

## Required Reading

- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/02_QUALITY_GATES.md` (Gate 5)
- `Implementation_v2/SHARED/07_TROUBLESHOOTING.md`
- `shared_context/AG-01_handoff.md`
- `shared_context/AG-02_handoff.md` (if present)

---

## Constraints

- Do NOT commit clinical datasets (ChestX-ray14 / CheXpert / MIMIC-CXR) into repo.
- All scripts must support:
  - dataset present → run evaluation/augmentation
  - dataset missing → exit with “SKIPPED” and code 0
- Focus for v2.0: classical augmentation + reporting.
- GAN training is optional and should be deferred unless you have the resources and time.

---

## Outputs

- `data/augmentation/augmentation.py` (classical augmentation pipeline)
- `data/provenance_tracker.py` (data lineage metadata template)
- `validation/external/multi_institutional.py` (external validation harness)
- `validation/reports/` (json summaries)
- `shared_context/dataset_status.json`
- `docs/data/` (data provenance & limitations)

---

## Task 7.1 — Directory setup

```bash
mkdir -p data/augmentation validation/{external,reports} docs/data
Task 7.2 — Augmentation Pipeline (no heavy assumptions)
Create data/augmentation/augmentation.py

Requirement:

Use minimal dependencies (prefer PIL / numpy / tensorflow image ops).
If you use albumentations, guard import and fallback.
Task 7.3 — External Validation Harness (skip gracefully)
Create validation/external/multi_institutional.py

Requirements:

Accept dataset path via CLI args
If path not found, print “SKIPPED” and exit 0
Output results JSON to validation/reports/
Task 7.4 — Provenance Tracking
Create data/provenance_tracker.py

Requirements:

Write a JSON template describing:
dataset sources
licensing / consent status
preprocessing steps
train/eval split logic
Do NOT include PHI
Task 7.5 — Reports + Summary
Write:

validation/reports/summary.json
docs/data/limitations.md
Verification
Run augmentation on a local folder of sample images (non-PHI).
Run external validation harness with missing dataset path and confirm SKIPPED exit 0.
Update shared_context/dataset_status.json with what you achieved and what’s deferred.
Handoff
Create shared_context/AG-07_handoff.md:

how to run the scripts
what dataset formats you assumed
what needs future work (GAN, multi-institution datasets, etc.)
```
````
