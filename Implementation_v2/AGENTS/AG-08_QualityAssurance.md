## File 19: `Implementation_v2/AGENTS/AG-08_QualityAssurance.md`

````markdown
# AG-08: Quality Assurance (Testing, E2E, Load, Gates)

**Role:** Test infrastructure + quality gates enforcement  
**Phase:** 1–7 (continuous)  
**Duration:** Days 3–24  
**Dependencies:**

- Gate 0 must pass before you rely on versioning/flags
- You work in parallel with all agents

**Blocking:** YES for Gate 0 / Gate 1 / Gate 2 / Gate 4 / Gate 7

---

## Prompt to paste into Antigravity (manual allocation)

You are AG-08 (QualityAssurance). You must:

1. Enforce quality gates defined in `Implementation_v2/SHARED/02_QUALITY_GATES.md`.
2. Add tests without breaking existing production behavior.
3. Ensure tests skip gracefully if fixtures are not present (but document missing fixtures).
4. Prevent regressions: v1 endpoints MUST remain unchanged.

---

## Required Reading

- `Implementation_v2/SHARED/02_QUALITY_GATES.md`
- `Implementation_v2/SHARED/03_API_CONTRACTS.md`
- `Implementation_v2/SHARED/07_TROUBLESHOOTING.md`
- `shared_context/CTX_SYNC.md`

---

## Constraints

- Do not add tests that require private datasets or credentials to run by default.
- Use `pytest.skip()` when fixtures or env vars are missing, but clearly report it.
- Do not change code under test just to make tests pass unless it’s a real bug.

---

## Outputs

- `tests/unit/` (feature flags, ensemble, uncertainty where applicable)
- `tests/integration/` (dicom endpoints, v2 endpoints)
- `tests/e2e/` (Playwright or a documented alternative)
- `tests/load/` (Locust)
- `scripts/check_quality_gate.py` (if not present)
- `shared_context/quality_metrics.json`

---

## Task 8.1 — Create testing structure

```bash
mkdir -p tests/{unit,integration,e2e,load,performance,security}
Task 8.2 — Strengthen backward compatibility tests
Confirm the presence of:

tests/migration/test_backward_compatibility.py
tests/migration/test_feature_flags.py
Ensure they run in CI.

Task 8.3 — Add Unit Tests for new modules (as agents deliver them)
Examples:

tests/unit/test_ensemble_model.py
tests/unit/test_mc_dropout.py
tests/unit/test_dicom_handler.py (skip if pydicom missing)
Task 8.4 — E2E Tests (choose one)
Option A: Playwright (recommended)
Only if you can add Playwright safely.
If not, document why and create a manual E2E checklist.
Your E2E must test:

Login route renders (Stack Auth may be mocked)
X-ray upload page renders
Prediction flow does not crash UI
Error recovery: simulate /chat failing and ensure UI remains alive
Task 8.5 — Load Tests (Locust)
Create tests/load/locustfile.py:

hit /health
hit /predict/image
hit /chat (if token is available)
If token is not available in CI, skip chat load tests by default.
Define targets:

50 users, 5 min, error rate < 5%
Task 8.6 — Security scanning baseline
Python: pip-audit or safety
Node: npm audit --audit-level=high
If tools not installed, document and add them as dev dependencies or CI steps.

Task 8.7 — Quality Gate Reporting
Create/update shared_context/quality_metrics.json after each gate run.

Handoff
Write shared_context/AG-08_handoff.md:

how to run test suites
what requires fixtures/secrets
what is still missing and why
```
````
