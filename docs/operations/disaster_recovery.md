e# VoxRay AI - Disaster Recovery Plan

## 1. Overview

This document outlines the procedures for recovering the VoxRay AI system in the event of a catastrophic failure.

**RPO (Recovery Point Objective):** 24 hours (for data), 0 hours for code (Git)
**RTO (Recovery Time Objective):** 4 hours

## 2. Backup Strategy

### 2.1 Code and Configuration

- **Source:** GitHub Repository
- **Frequency:** Continuous (Git Push)
- **Recovery:** `git clone`

### 2.2 Model Artifacts

- **Source:** Hugging Face Hub (LFS)
- **ID:** `witty22/voxray-model`
- **Backup:** Models are versioned on HF Hub. Local cache is transient.
- **Recovery:** Automatic download on container startup.

### 2.3 User Data & Logs

- **Source:** Application Logs (stdout/stderr), Audit Logs (Volume)
- **Backup:** Configured to push to external logging service (e.g., CloudWatch, Datadog) or persistent volume.
- **Action:** Ensure persistent volumes are snapshotted daily.

## 3. Recovery Scenarios

### 3.1 Region Failure (K8s Cluster Down)

1. **Trigger:** Monitoring alerts site down > 5 mins.
2. **Action:**
   - Deploy K8s cluster in backup region (aws/gcp).
   - Apply K8s manifests: `kubectl apply -k k8s/overlays/production`
   - Update DNS to point to new Load Balancer IP.
3. **Validation:** Check `/health` endpoint.

### 3.2 Bad Deployment (CrashLoopBackOff)

1. **Trigger:** `kubectl get pods` shows restarts.
2. **Action:**
   - Rollback: `kubectl rollout undo deployment/voxray-backend`
   - Verify previous version active.

### 3.3 Model Corruption

1. **Trigger:** Model load failure logs or low prediction confidence.
2. **Action:**
   - Update env var `HF_TOKEN` and restart pods to trigger fresh model download from HF Hub.
   - Model is automatically re-downloaded from `witty22/voxray-model` on startup.

## 4. Contacts

- **Repository:** https://github.com/utkarshwasan/VoxRay-AI
- **Model Registry:** https://huggingface.co/witty22/voxray-model
- **Issues:** https://github.com/utkarshwasan/VoxRay-AI/issues
