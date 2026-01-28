# VoxRay AI: Deployment Guide

## Overview

Deploy VoxRay AI with backend on **Hugging Face Spaces** and frontend on **Vercel**.

---

## Backend: Hugging Face Spaces

### 1. Create Hugging Face Space

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click "Create new Space"
3. Settings:
   - **Name**: voxray-ai (or your preferred name)
   - **SDK**: Docker
   - **Hardware**: CPU Basic (free tier)
   - **Visibility**: Public

### 2. Upload Code

```bash
# Clone your repo
cd VoxRay-ai

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/voxray-ai

# Push to Hugging Face
git lfs install
git lfs track "backend/models/*.keras"
git add .gitattributes
git commit -m "Add LFS tracking"
git push hf main
```

### 3. Configure Secrets

In Space Settings → Repository Secrets:

| Secret Name          | Value                          | Description             |
| -------------------- | ------------------------------ | ----------------------- |
| `OPENROUTER_API_KEY` | `sk-or-v1-...`                 | Your OpenRouter API key |
| `STACK_PROJECT_ID`   | Your Stack project ID          | Stack Auth project      |
| `FRONTEND_URL`       | `https://voxray-ai.vercel.app` | Your Vercel URL         |
| `TTS_VOICE`          | `en-US-ChristopherNeural`      | Optional: TTS voice     |

### 4. Dockerfile Used

The deployment uses `Dockerfile.hf`:

- Port: **7860** (Hugging Face standard)
- User: Non-root (`user` with UID 1000)
- Health check: Built-in using urllib
- Workers: 1 (optimized for free tier)

### 5. Verify Deployment

Once deployed, your backend will be at:

```
https://YOUR_USERNAME-voxray-ai.hf.space
```

Test the health endpoint:

```bash
curl https://YOUR_USERNAME-voxray-ai.hf.space/health
```

Expected response:

```json
{ "status": "healthy", "model_loaded": true }
```

---

## Frontend: Vercel

### 1. Import Repository

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your GitHub repository

### 2. Configure Environment Variables

In Project Settings → Environment Variables:

| Variable Name                       | Value                                      | Description                     |
| ----------------------------------- | ------------------------------------------ | ------------------------------- |
| `VITE_API_URL`                      | `https://YOUR_USERNAME-voxray-ai.hf.space` | Backend URL (no trailing slash) |
| `VITE_STACK_PUBLISHABLE_CLIENT_KEY` | Your Stack client key                      | Stack Auth public key           |
| `VITE_STACK_PROJECT_ID`             | Your Stack project ID                      | Stack Auth project              |

### 3. Build Configuration

Vercel should auto-detect:

- **Framework**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

### 4. Deploy

Click "Deploy" and wait for build to complete.

Your frontend will be at:

```
https://voxray-ai.vercel.app
```

---

## Stack Auth Configuration

### 1. Update Allowed Callback URLs

In Stack Auth Dashboard → Settings → Redirect URLs:

```
https://voxray-ai.vercel.app/handler
```

### 2. Update Allowed Origins

In Stack Auth Dashboard → Settings → CORS Origins:

```
https://voxray-ai.vercel.app
https://YOUR_USERNAME-voxray-ai.hf.space
```

### 3. Cookie Settings

Enable:

- ✅ Allow cross-domain cookies
- ✅ SameSite=None
- ✅ Secure=True

---

## Testing Deployment

### 1. Health Check

```bash
# Backend
curl https://YOUR_USERNAME-voxray-ai.hf.space/health

# Expected: {"status": "healthy", "model_loaded": true}
```

### 2. CORS Verification

Open browser console on `https://voxray-ai.vercel.app` and check for CORS errors.

### 3. End-to-End Test

1. Visit `https://voxray-ai.vercel.app`
2. Wait for "Initializing AI Engines..." message (cold start ~30s)
3. Log in via Stack Auth
4. Upload X-ray image
5. Get prediction
6. Click "Explain Diagnosis"
7. Test voice interaction

---

## Troubleshooting

### Backend Cold Start

- **Issue**: 504 Gateway Timeout on first request
- **Fix**: Frontend now includes 60-second timeout + loading message
- **Status**: "Initializing AI Engines... (this may take 30s)"

### CORS Errors

- **Issue**: CORS policy blocking requests
- **Fix**: Verify `FRONTEND_URL` secret is set correctly in Hugging Face
- **Check**: Backend logs should show "✅ Added frontend origin: ..."

### Model Not Loading

- **Issue**: Health check shows `"model_loaded": false`
- **Fix**: Ensure Git LFS is properly tracking model file
- **Verify**: `backend/models/medical_model_final.keras` exists

### Authentication Failures

- **Issue**: 401 Unauthorized errors
- **Fix**:
  1. Verify `STACK_PROJECT_ID` matches in both frontend and backend
  2. Check allowed origins in Stack Auth Dashboard
  3. Ensure cookies are enabled in browser

---

## Monitoring

### Hugging Face Spaces

- View logs: Space Settings → Logs
- Monitor usage: Space Settings → Analytics

### Vercel

- View deployments: Project → Deployments
- Check logs: Deployment → Build Logs / Function Logs

---

## Cost Optimization

### Free Tier Limits

- **Hugging Face**: CPU Basic (free, cold start ~30s)
- **Vercel**: 100GB bandwidth/month, unlimited deployments
- **Stack Auth**: 10,000 MAUs (Monthly Active Users)

### Recommendations

- Use Git LFS for model files (included in free tier)
- Keep backend response times under 30s
- Monitor Vercel bandwidth usage

---

## Next Steps

1. ✅ Deploy backend to Hugging Face Spaces
2. ✅ Deploy frontend to Vercel
3. ✅ Configure Stack Auth
4. ✅ Test end-to-end flow
5. ⚠️ Set up monitoring/alerts
6. ⚠️ Configure custom domain (optional)

---

**Deployment Complete!** 🚀

Your VoxRay AI application is now live and accessible worldwide.
