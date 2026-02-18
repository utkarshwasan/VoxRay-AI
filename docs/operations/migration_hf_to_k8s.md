# Migration Guide: HF Spaces to Kubernetes

## 1. Executive Summary

This guide details the steps to migrate VoxRay AI from a standalone Hugging Face Space to a managed Kubernetes cluster.

## 2. Prerequisites

- [x] Dockerized Application (`voxray-backend:v2`)
- [x] K8s Manifests (`k8s/base`, `k8s/overlays`)
- [ ] Kubernetes Cluster (EKS/GKE/AKS/Minikube)
- [ ] Domain Name (optional)

## 3. Phase 1: Parallel Deployment (Canary)

1. **Deploy to K8s:**
   ```bash
   kubectl apply -k k8s/overlays/staging
   ```
2. **Verify Health:**
   ```bash
   kubectl port-forward svc/voxray-backend 7860:80
   curl http://localhost:7860/health
   ```
3. **Smoke Test:**
   - Send test inference request to K8s endpoint.
   - Compare results with Production (HF Spaces).

## 4. Phase 2: Traffic Shifting

1. **Update DNS:**
   - Create a weighted DNS record/Load Balancer.
   - Route 10% traffic to K8s.
2. **Monitor:**
   - Check Prometheus metrics for latency/errors.
   - Watch logs for 500s.
3. **Scale:**
   - If stable with 10%, increase to 50%, then 100%.

## 5. Phase 3: Decommission Legacy

1. **Keep HF Warm:**
   - Do not delete HF Space immediately. Keep as fallback.
2. **Finalize:**
   - After 48 hours of 100% K8s traffic, mark migration complete.

## 6. Rollback Plan

If critical errors occur > 1%:

1. Revert DNS to point 100% to Hugging Face Spaces.
2. Scale down K8s deployment.
3. Investigate logs.
