## File 20: `Implementation_v2/AGENTS/AG-09_DocumentationLead.md`

````markdown
# AG-09: Documentation Lead (API Docs, Deployment Guides, Research Artifacts)

**Role:** Technical writing + production documentation  
**Phase:** 6  
**Duration:** Days 18–22  
**Dependencies:** All core API contracts stabilized (AG-00/AG-01/AG-03/AG-04/AG-06)

**Blocking:** NO for code completion, but strongly recommended before submission

---

## Prompt to paste into Antigravity (manual allocation)

You are AG-09 (DocumentationLead). You must:

1. Document the system as it actually exists (no fabricated endpoints).
2. Pull API shapes from `Implementation_v2/SHARED/03_API_CONTRACTS.md` and code.
3. Ensure docs include troubleshooting for Netlify/HuggingFace deployment.
4. Ensure docs mention feature flags + versioning.

---

## Required Reading

- `Implementation_v2/SHARED/03_API_CONTRACTS.md`
- `Implementation_v2/SHARED/01_MUST_PRESERVE.md`
- `Implementation_v2/SHARED/07_TROUBLESHOOTING.md`
- `shared_context/CTX_SYNC.md`
- All agent handoff notes in `shared_context/AG-*_handoff.md`

---

## Constraints

- Do NOT document features that are not implemented.
- If a section is planned but not shipped, clearly label: “Planned (v2.1)” and do not present it as existing.
- Avoid PHI in screenshots, examples, logs.

---

## Outputs

- `docs/api/openapi.yaml` (if you choose OpenAPI)
- `docs/api/authentication.md`
- `docs/deployment/netlify.md`
- `docs/deployment/huggingface.md`
- `docs/deployment/kubernetes.md` (if AG-05 produced manifests)
- `docs/architecture/overview.md`
- `docs/operations/monitoring.md`
- `docs/operations/rollback.md` (reference Phase 0 rollback doc)
- `docs/troubleshooting.md` (aggregate)
- `shared_context/documentation_status.json`

---

## Task 9.1 — Docs skeleton

Create minimal docs tree:

```bash
mkdir -p docs/{api,deployment,architecture,operations}
Task 9.2 — Document Authentication (Stack Auth)
Write docs/api/authentication.md:

x-stack-access-token header
token origin (Stack Auth)
JWKS verification summary (without exposing secrets)
Task 9.3 — Document API endpoints
Use SHARED/03_API_CONTRACTS.md and confirm in code:

v1 endpoints (stable)
v2 endpoints (feature-gated)
/v1 aliases
/v2 endpoints
/api/feature-flags
If OpenAPI is too heavy, at least produce a markdown reference.

Task 9.4 — Deployment docs
Write:

docs/deployment/netlify.md (env vars, build steps, permalink vs main URL)
docs/deployment/huggingface.md (Space secrets: OPENROUTER_API_KEY, STACK_PROJECT_ID)
docs/deployment/kubernetes.md only if manifests exist
Task 9.5 — Troubleshooting consolidation
Create docs/troubleshooting.md referencing:

React #426 prevention
CORS and origins (Netlify deploy URLs vs main domain)
missing OpenRouter key causing /chat 500
model load issues on HF
Task 9.6 — Documentation status
Create shared_context/documentation_status.json with completion progress and what’s deferred.

Handoff
Create shared_context/AG-09_handoff.md:

List of docs created
What remains incomplete
Any known mismatch between docs and code to resolve
```
````
