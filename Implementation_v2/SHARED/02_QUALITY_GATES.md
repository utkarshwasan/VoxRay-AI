---

## File 5: SHARED/02_QUALITY_GATES.md

```markdown
# VoxRay AI v2.0 - Quality Gates

**Purpose:** Define pass/fail criteria for each phase to ensure production readiness

---

## 🎯 Quality Gate Philosophy

**Blocking Gates:** MUST pass 100% before proceeding (Phases 0, 1, 2, 4, 7)  
**Non-Blocking Gates:** Should pass but can proceed with documented exceptions (Phases 3, 5, 6)  
**Escape Hatch:** Available for non-blocking gates via feature flags

---

## Quality Gate 0: Migration Foundation (BLOCKING)

**Phase:** 0  
**Owner:** AG-00  
**Duration:** Days 1-2  
**Blocking:** YES - No other agent can start until this passes

### Criteria

| Metric                           | Threshold | Current | Status | Command                                                                                  |
| -------------------------------- | --------- | ------- | ------ | ---------------------------------------------------------------------------------------- |
| Backward Compatibility Tests     | 100% pass | -       | ⏳     | `pytest tests/migration/test_backward_compatibility.py -v`                               |
| Feature Flag System Operational  | TRUE      | -       | ⏳     | `python -c "from backend.core.feature_flags import feature_flags; print(feature_flags)"` |
| API Versioning Implemented       | TRUE      | -       | ⏳     | `curl http://localhost:8000/v1/health && curl http://localhost:8000/v2/health`           |
| CTX_SYNC.md Created              | TRUE      | -       | ⏳     | `test -f shared_context/CTX_SYNC.md`                                                     |
| Rollback Procedures Documented   | TRUE      | -       | ⏳     | `test -f docs/migration/rollback_procedures.md`                                          |
| All Current Endpoints Functional | 100%      | -       | ⏳     | `pytest tests/migration/ -k "test_predict or test_transcribe or test_chat"`              |

### Pass Criteria

```yaml
gate_0_pass:
  all_tests_passing: true
  feature_flags_working: true
  api_versioning_working: true
  documentation_complete: true
On Failure
Bash

action: "BLOCK ALL PHASES"
message: "Phase 0 is the foundation. Cannot proceed until 100% complete."
rollback: "Revert all changes, start over"
notify: ["human_coordinator", "all_agents"]
Verification Script
Bash

#!/bin/bash
# Run this to check Gate 0 status

echo "=== Quality Gate 0 Verification ==="

# Test 1: Backward compatibility
echo "1. Running backward compatibility tests..."
pytest tests/migration/test_backward_compatibility.py -v --tb=short
TEST_RESULT=$?

# Test 2: Feature flags
echo "2. Checking feature flags..."
python -c "from backend.core.feature_flags import feature_flags; print('✅ Feature flags OK')" 2>/dev/null
FF_RESULT=$?

# Test 3: API versioning
echo "3. Checking API versioning..."
curl -s http://localhost:8000/v1/health > /dev/null && echo "✅ v1 endpoint OK"
V1_RESULT=$?

curl -s http://localhost:8000/v2/health > /dev/null && echo "✅ v2 endpoint OK"
V2_RESULT=$?

# Test 4: Files exist
echo "4. Checking required files..."
test -f shared_context/CTX_SYNC.md && echo "✅ CTX_SYNC.md exists"
CTX_RESULT=$?

test -f docs/migration/rollback_procedures.md && echo "✅ Rollback docs exist"
DOC_RESULT=$?

# Final result
if [ $TEST_RESULT -eq 0 ] && [ $FF_RESULT -eq 0 ] && [ $V1_RESULT -eq 0 ] && [ $V2_RESULT -eq 0 ] && [ $CTX_RESULT -eq 0 ] && [ $DOC_RESULT -eq 0 ]; then
  echo "✅ QUALITY GATE 0: PASSED"
  exit 0
else
  echo "❌ QUALITY GATE 0: FAILED"
  exit 1
fi
Quality Gate 1: ML Core & Architecture (BLOCKING)
Phase: 1
Owner: AG-01
Duration: Days 3-7
Blocking: YES - Required for Phases 2, 5, 6, 7

Criteria
Metric	Threshold	Current	Status	Command
Ensemble Model Accuracy	≥87%	-	⏳	python scripts/evaluate_ensemble.py
Uncertainty Correlation	≥70%	-	⏳	python scripts/evaluate_uncertainty.py
Inference Latency (p95)	<500ms	-	⏳	pytest tests/performance/test_latency.py
Cross-Validation Complete	TRUE	-	⏳	test -f shared_context/cv_results.json
Benchmark on ChestX-ray14	Complete	-	⏳	test -f shared_context/benchmark_chestxray14.json
Model Serving Abstraction	Functional	-	⏳	pytest tests/unit/test_model_server.py
V1 Endpoints Still Work	100%	-	⏳	pytest tests/migration/test_backward_compatibility.py
Unit Test Coverage	≥80%	-	⏳	pytest --cov=backend.models --cov-report=term
Detailed Metrics
1. Ensemble Model Accuracy
Python

# Evaluation script: scripts/evaluate_ensemble.py
# Expected output:
{
  "validation_accuracy": 0.89,  # Must be ≥0.87
  "per_class_accuracy": {
    "PNEUMONIA": 0.91,
    "LUNG_CANCER": 0.85,
    # ...
  },
  "ensemble_config": {
    "models": ["ResNet50V2", "EfficientNetB3"],
    "voting": "soft"
  }
}
Pass: accuracy ≥ 0.87
Fail: accuracy < 0.87

2. Uncertainty Correlation
Python

# Evaluation script: scripts/evaluate_uncertainty.py
# Measures: Does high uncertainty correlate with incorrect predictions?
{
  "misclassification_flagging_rate": 0.75,  # Must be ≥0.70
  "false_positive_rate": 0.15,
  "optimal_threshold": 0.3
}
Pass: flagging_rate ≥ 0.70
Fail: flagging_rate < 0.70

3. Inference Latency
Python

# Test: tests/performance/test_latency.py
# Measures p50, p95, p99 latency for ensemble prediction
{
  "p50": 200,  # ms
  "p95": 450,  # ms - Must be <500ms
  "p99": 600   # ms
}
Pass: p95 < 500ms
Fail: p95 ≥ 500ms

Pass Criteria
YAML

gate_1_pass:
  ensemble_accuracy: ">=0.87"
  uncertainty_correlation: ">=0.70"
  inference_latency_p95: "<500"
  cross_validation_complete: true
  benchmarks_complete: true
  backward_compat_tests: "100%"
  unit_test_coverage: ">=80%"
On Failure
Bash

action: "BLOCK Phases 2, 5, 6, 7"
message: "ML core is foundational for clinical features and integration"
options:
  - "Tune ensemble weights"
  - "Add more training data"
  - "Optimize inference pipeline"
  - "Rollback to ResNet50V2 only (disable ensemble flag)"
notify: ["AG-01", "AG-06", "AG-07", "human_coordinator"]
Escape Hatch
Bash

# If ensemble fails but ResNet50V2 works:
export FF_ENSEMBLE_MODEL=false  # Disable ensemble
export FF_UNCERTAINTY_QUANTIFICATION=false  # Disable uncertainty

# V1 endpoints will fallback to ResNet50V2
# Can proceed with limited v2 functionality
Quality Gate 2: Clinical Integration (BLOCKING)
Phase: 2
Owner: AG-03
Duration: Days 7-13
Blocking: YES - Required for Phase 7

Criteria
Metric	Threshold	Current	Status	Command
DICOM Parsing Success Rate	≥99%	-	⏳	pytest tests/integration/test_dicom.py
FHIR Client Connection	Functional	-	⏳	pytest tests/integration/test_fhir.py
Audit Log Coverage	100%	-	⏳	python scripts/check_audit_coverage.py
Data Anonymization Compliance	HIPAA Safe Harbor	-	⏳	pytest tests/security/test_anonymization.py
No PHI in Logs	0 violations	-	⏳	python scripts/scan_logs_for_phi.py
Regulatory Docs Draft	Complete	-	⏳	test -f docs/regulatory/ISO13485.md
Detailed Metrics
1. DICOM Parsing Success
Python

# Test: tests/integration/test_dicom.py
# Uses sample DICOM files from fixtures/
{
  "total_files": 100,
  "parsed_successfully": 99,  # Must be ≥99
  "parse_failures": 1,
  "failure_reasons": {
    "unsupported_transfer_syntax": 1
  }
}
Pass: success_rate ≥ 99%
Fail: success_rate < 99%

2. Audit Log Coverage
Python

# Script: scripts/check_audit_coverage.py
# Verifies all prediction endpoints are logged
{
  "endpoints_requiring_audit": [
    "/predict/image",
    "/v2/predict/image",
    "/v2/predict/dicom"
  ],
  "endpoints_with_logging": [
    "/predict/image",
    "/v2/predict/image",
    "/v2/predict/dicom"
  ],
  "coverage": "100%"  # Must be 100%
}
Pass: coverage == 100%
Fail: coverage < 100%

3. PHI Detection
Python

# Script: scripts/scan_logs_for_phi.py
# Scans logs for patterns matching PHI
{
  "logs_scanned": 1000,
  "phi_violations": 0,  # Must be 0
  "patterns_checked": [
    "patient_name",
    "patient_id (non-hashed)",
    "email_addresses",
    "phone_numbers",
    "addresses"
  ]
}
Pass: violations == 0
Fail: violations > 0

Pass Criteria
YAML

gate_2_pass:
  dicom_parsing_success: ">=99%"
  fhir_connection: true
  audit_coverage: "100%"
  phi_in_logs: 0
  anonymization_compliant: true
  regulatory_docs_drafted: true
On Failure
Bash

action: "BLOCK Phase 7 (frontend integration)"
message: "Clinical backend must be stable before UI integration"
options:
  - "Fix DICOM parsing for edge cases"
  - "Add PHI detection patterns"
  - "Complete audit logging"
  - "Disable DICOM/FHIR features (escape hatch)"
notify: ["AG-03", "AG-06", "human_coordinator"]
Escape Hatch
Bash

# Disable clinical features if not ready
export FF_DICOM_SUPPORT=false
export FF_FHIR_INTEGRATION=false

# Core prediction still works
# Can defer DICOM/FHIR to v2.1
Quality Gate 3: Voice Enhancement (NON-BLOCKING)
Phase: 3
Owner: AG-04
Duration: Days 10-16
Blocking: NO - Can proceed with flags disabled

Criteria
Metric	Threshold	Current	Status	Command
Wake Word Detection Accuracy	≥95%	-	⏳	pytest tests/voice/test_wake_word.py
Medical Term WER	≤15%	-	⏳	python scripts/evaluate_medical_vocab.py
Spanish Recognition Accuracy	≥90%	-	⏳	pytest tests/voice/test_spanish.py
Voice Command Recognition	≥95%	-	⏳	pytest tests/voice/test_commands.py
Noise Robustness	Functional in 3/4 levels	-	⏳	pytest tests/voice/test_noise.py
Detailed Metrics
1. Wake Word Detection
Python

# Test: tests/voice/test_wake_word.py
# Uses audio fixtures with/without wake word
{
  "true_positives": 95,  # Correctly detected "Hey VoxRay"
  "false_positives": 2,   # Triggered on non-wake-word
  "true_negatives": 98,   # Correctly ignored
  "false_negatives": 5,   # Missed "Hey VoxRay"
  "accuracy": 0.97,       # Must be ≥0.95
  "false_positive_rate": 0.02
}
Pass: accuracy ≥ 0.95
Fail (but non-blocking): accuracy < 0.95 → Can proceed with push-to-talk only

2. Medical Vocabulary WER
Python

# Script: scripts/evaluate_medical_vocab.py
# Word Error Rate for medical terms
{
  "total_words": 200,
  "errors": 25,
  "wer": 0.125,  # Must be ≤0.15 (15%)
  "common_errors": {
    "pleural": "plural",
    "consolidation": "consultation"
  }
}
Pass: WER ≤ 0.15
Fail (but non-blocking): WER > 0.15 → Can proceed with standard vocabulary

Pass Criteria
YAML

gate_3_pass:
  wake_word_accuracy: ">=0.95"
  medical_term_wer: "<=0.15"
  spanish_accuracy: ">=0.90"
  command_recognition: ">=0.95"
  noise_robustness: ">=3_of_4_levels"
On Failure (Non-Blocking)
Bash

action: "WARN but ALLOW to proceed"
message: "Voice enhancements are optional. Can ship with basic voice."
options:
  - "Disable wake word, use push-to-talk"
  - "Defer Spanish to v2.1"
  - "Defer medical vocabulary to v2.1"
fallback:
  - "FF_WAKE_WORD_DETECTION=false"
  - "FF_MULTILINGUAL_VOICE=false"
  - "FF_MEDICAL_VOCABULARY=false"
  - "Core voice (Whisper + Edge-TTS) still functional"
notify: ["AG-04", "AG-06"]
Quality Gate 4: DevOps & Infrastructure (BLOCKING)
Phase: 4
Owner: AG-05
Duration: Days 13-19
Blocking: YES - Required for production deployment

Criteria
Metric	Threshold	Current	Status	Command
Dockerfile Builds Successfully	TRUE	-	⏳	docker build -t voxray-backend .
Docker Image Size	<2GB	-	⏳	`docker images
K8s Manifests Valid	TRUE	-	⏳	kubectl apply --dry-run=client -f k8s/
Health Endpoint Responds	200 OK	-	⏳	curl http://localhost:8000/health
Prometheus Metrics Exposed	TRUE	-	⏳	curl http://localhost:8000/metrics
DR Procedures Documented	TRUE	-	⏳	test -f docs/operations/disaster_recovery.md
Migration Runbook Complete	TRUE	-	⏳	test -f docs/operations/migration_hf_to_k8s.md
Detailed Metrics
1. Docker Build
Bash

# Must complete without errors
docker build -t voxray-backend:test -f Dockerfile .

# Check image size
SIZE=$(docker images voxray-backend:test --format "{{.Size}}")
# Must be <2GB (2048MB)
Pass: Build succeeds, size < 2GB
Fail: Build fails or size ≥ 2GB

2. K8s Validation
Bash

# All manifests must be valid
kubectl apply --dry-run=client -f k8s/base/
kubectl apply --dry-run=client -f k8s/overlays/production/

# Expected: No errors, all resources validated
Pass: All manifests valid
Fail: Any validation error

3. Monitoring
Bash

# Metrics endpoint must return Prometheus format
curl http://localhost:8000/metrics

# Expected output (example):
# inference_latency_seconds_bucket{le="0.5"} 100
# inference_latency_seconds_bucket{le="1.0"} 150
# prediction_confidence_score 0.95
Pass: Metrics endpoint returns valid Prometheus format
Fail: Endpoint missing or invalid format

Pass Criteria
YAML

gate_4_pass:
  docker_build_success: true
  docker_image_size: "<2GB"
  k8s_manifests_valid: true
  health_endpoint_working: true
  metrics_exposed: true
  dr_documented: true
  migration_runbook_complete: true
On Failure
Bash

action: "BLOCK production deployment"
message: "Infrastructure must be solid before deploying"
options:
  - "Optimize Docker image (multi-stage build, remove dev deps)"
  - "Fix K8s manifests"
  - "Add health/metrics endpoints"
  - "Complete DR documentation"
  - "Stay on HuggingFace Spaces (fallback)"
notify: ["AG-05", "human_coordinator"]
Quality Gate 5: Data Pipeline (NON-BLOCKING)
Phase: 5
Owner: AG-07
Duration: Days 15-20
Blocking: NO - Can defer to v2.1

Criteria
Metric	Threshold	Current	Status	Command
Data Augmentation Functional	TRUE	-	⏳	pytest tests/data/test_augmentation.py
External Validation Complete	≥1 dataset	-	⏳	test -f validation/external/results.json
Data Provenance Tracked	TRUE	-	⏳	test -f data/provenance.json
Pass Criteria
YAML

gate_5_pass:
  augmentation_working: true
  external_validation: ">=1_dataset"
  provenance_tracked: true
On Failure (Non-Blocking)
Bash

action: "WARN but ALLOW to proceed"
message: "Data improvements can be deferred to v2.1"
fallback: "Use existing training data, defer augmentation"
notify: ["AG-07"]
Quality Gate 6: Documentation (NON-BLOCKING)
Phase: 6
Owner: AG-09
Duration: Days 18-22
Blocking: NO - But strongly recommended

Criteria
Metric	Threshold	Current	Status	Command
OpenAPI Spec Complete	100%	-	⏳	swagger-cli validate docs/api/openapi.yaml
Deployment Guide	Complete	-	⏳	test -f docs/deployment/guide.md
API Documentation Coverage	100%	-	⏳	python scripts/check_api_docs_coverage.py
Pass Criteria
YAML

gate_6_pass:
  openapi_valid: true
  deployment_guide_complete: true
  api_docs_coverage: "100%"
On Failure (Non-Blocking)
Bash

action: "WARN"
message: "Documentation is important but not blocking"
recommendation: "Complete before public launch"
notify: ["AG-09"]
Quality Gate 7: Full Integration (BLOCKING)
Phase: 7
Owner: AG-06, AG-08
Duration: Days 21-24
Blocking: YES - Required for production launch

Criteria
Metric	Threshold	Current	Status	Command
E2E Tests Passing	100%	-	⏳	pytest tests/e2e/ -v
Load Test (50 users)	<5% error rate	-	⏳	locust -f tests/load/locustfile.py
Backward Compatibility	100%	-	⏳	pytest tests/migration/test_backward_compatibility.py
All Feature Flags Tested	TRUE	-	⏳	pytest tests/feature_flags/ -v
Security Scan Clean	0 critical	-	⏳	safety check
Frontend Build Success	TRUE	-	⏳	cd frontend && npm run build
Deployment Test Success	TRUE	-	⏳	bash scripts/deploy_test.sh
Detailed Metrics
1. E2E Tests
Python

# Must cover critical workflows
tests_required = [
    "test_login_upload_predict_view",
    "test_voice_interaction_flow",
    "test_error_recovery",
    "test_ensemble_prediction (if enabled)",
    "test_dicom_upload (if enabled)"
]

# All must pass
pass_rate = 100%
2. Load Test
Python

# Test parameters
{
  "users": 50,
  "spawn_rate": 5,
  "duration": "5min",
  "endpoints_tested": [
    "/predict/image",
    "/chat",
    "/transcribe/audio"
  ],
  "results": {
    "total_requests": 1500,
    "failures": 15,
    "error_rate": 0.01,  # 1% - Must be <5%
    "p95_latency": 1800  # ms
  }
}
Pass: error_rate < 0.05 (5%)
Fail: error_rate ≥ 0.05

3. Security Scan
Bash

# Python dependencies
safety check --json > security_report.json

# Expected:
{
  "critical": 0,  # Must be 0
  "high": 0,      # Should be 0
  "medium": <5    # Acceptable if documented
}
Pass: critical == 0
Fail: critical > 0

Pass Criteria
YAML

gate_7_pass:
  e2e_tests_passing: "100%"
  load_test_error_rate: "<5%"
  backward_compat: "100%"
  feature_flags_tested: true
  security_critical: 0
  frontend_build: true
  deployment_test: true
On Failure
Bash

action: "BLOCK production launch"
message: "Integration must be perfect for production"
options:
  - "Fix failing E2E tests"
  - "Optimize for load test"
  - "Fix security vulnerabilities"
  - "Rollback problematic features"
notify: ["AG-06", "AG-08", "human_coordinator", "all_agents"]
📊 Quality Gate Dashboard
Track all gates in one place:

text

┌─────────────────────────────────────────────────────────────────┐
│                    QUALITY GATE STATUS                           │
├──────┬─────────────────┬──────────┬──────────┬──────────────────┤
│ Gate │ Phase           │ Blocking │ Status   │ Last Checked     │
├──────┼─────────────────┼──────────┼──────────┼──────────────────┤
│  0   │ Migration       │ YES      │ ⏳       │ Not started      │
│  1   │ ML Core         │ YES      │ ⏳       │ Not started      │
│  2   │ Clinical        │ YES      │ ⏳       │ Not started      │
│  3   │ Voice           │ NO       │ ⏳       │ Not started      │
│  4   │ DevOps          │ YES      │ ⏳       │ Not started      │
│  5   │ Data            │ NO       │ ⏳       │ Not started      │
│  6   │ Documentation   │ NO       │ ⏳       │ Not started      │
│  7   │ Integration     │ YES      │ ⏳       │ Not started      │
└──────┴─────────────────┴──────────┴──────────┴──────────────────┘

Legend: ⏳ Pending  🔄 In Progress  ✅ Passed  ❌ Failed
Update in: shared_context/quality_gates_status.json

Last Updated: 2025-01-31
Maintained By: AG-08 (QualityAssurance)
Review Frequency: Before completing each phase
```
