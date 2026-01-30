## File 16: `Implementation_v2/AGENTS/AG-05_DevOpsArchitect.md`

```markdown
# AG-05: DevOps Architect (Docker / K8s / Monitoring / DR)

**Role:** Infrastructure, Security, Observability  
**Phase:** 4  
**Duration:** Days 13–19  
**Dependencies:** AG-00 complete; AG-01 outputs helpful (resource sizing)  
**Blocking:** YES for production migration (Gate 4)

---

## Mission

Create production-grade ops foundation while keeping current deployments running:

- Dockerfile improvements (size, reproducibility)
- K8s manifests (base + overlays)
- Health + metrics strategy (Prometheus)
- Disaster Recovery documentation
- Migration runbook HF → K8s (warm standby)

---

## Required Reading

- `Implementation_v2/SHARED/02_QUALITY_GATES.md` (Gate 4)
- `Implementation_v2/SHARED/05_COST_ESTIMATION.md`
- `Implementation_v2/SHARED/07_TROUBLESHOOTING.md`
- `shared_context/CTX_SYNC.md`

---

## Constraints

- Do not require K8s migration to be immediate
- HF backend remains the fallback until K8s is proven
- Do not break current Dockerfile unless you can still run backend with it locally
- If you add /metrics, ensure it does not interfere with startup

---

## Outputs

- `Dockerfile` (optimized)
- `docker-compose.yml` (optional for local stack)
- `k8s/base/*` and `k8s/overlays/{dev,staging,production}/*`
- `docs/operations/disaster_recovery.md`
- `docs/operations/migration_hf_to_k8s.md`
- Monitoring:
  - `monitoring/prometheus.yml`
  - `monitoring/grafana/voxray-dashboard.json` (optional)

---

## Task 5.1 — Dockerfile Optimization (Multi-stage)

**Goal:** reduce image size, install required system libs (opencv/pydicom may need libgl)

Implementation rules:

- Use python:3.11-slim
- Install only required apt packages
- Use pip --no-cache-dir
- Copy only backend runtime files

---

## Task 5.2 — Add Metrics (Prometheus) WITHOUT Breaking App

If you add `prometheus-fastapi-instrumentator`, do it in a way that:

- doesn’t change existing endpoints
- exposes `/metrics`

If adding the dependency is not possible in current environment, document fallback.

---

## Task 5.3 — K8s Manifests

Create:

- Deployment (backend)
- Service
- Ingress (optional)
- ConfigMap/Secrets placeholders
- HPA (optional)

Include:

- readinessProbe: /health
- livenessProbe: /health
- high initialDelaySeconds (models load on startup)

---

## Task 5.4 — Disaster Recovery Doc

Create `docs/operations/disaster_recovery.md`:

- RPO/RTO
- backup model artifacts
- backup audit logs
- restore instructions

---

## Task 5.5 — Migration Runbook HF → K8s

Create `docs/operations/migration_hf_to_k8s.md`:

- keep HF warm
- canary traffic plan
- DNS cutover strategy
- rollback steps

---

## Verification (Gate 4 Prep)

- [ ] Docker build succeeds
- [ ] Image size under target (best effort)
- [ ] K8s dry-run apply works
- [ ] /health stable
- [ ] /metrics works if enabled
- [ ] Docs exist

Update CTX_SYNC.md and create `shared_context/AG-05_handoff.md`.
```
