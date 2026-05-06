# Render Deployment Guide - The Alchemist

This guide explains how to deploy **The Alchemist** as two microservices on Render.com.

## Architecture Overview

```
┌─────────────────────────────────────┐
│  GitHub Repository                  │
│  ├── Backend/                       │
│  │   ├── app/                      │
│  │   ├── mcp_server.py             │
│  │   ├── requirements.txt          │
│  │   └── render.yaml               │
│  └── Frontend/                      │
└─────────────────────────────────────┘
            │
            ├─────────────────────────────────┬────────────────────────────────┐
            │                                 │                                │
    ┌──────────────────┐          ┌──────────────────────┐
    │ Backend Service  │          │ MCP Service          │
    ├──────────────────┤          ├──────────────────────┤
    │ Port: 8000       │  HTTP    │ Port: 8010           │
    │ uvicorn          │◄────────►│ FastMCP              │
    │ app.main:app     │          │ mcp_server.py        │
    └──────────────────┘          └──────────────────────┘
            │                               │
            ▼                               ▼
    alchemist-backend            alchemist-mcp
    .onrender.com                .onrender.com
```

---

## Prerequisites

- GitHub account with the repository connected
- Render.com account (free tier available)
- All environment variables/secrets from `.env`

---

## Step 1: Prepare Your Repository

1. Ensure `Backend/render.yaml` exists (already created)
2. Ensure `.env.example` is in `Backend/` (already created)
3. Commit these files:

```bash
cd /Users/prateekrauniyar/Documents/SeniorDeisgn-The-Alchemist
git add Backend/render.yaml Backend/.env.example
git commit -m "Add Render deployment configuration"
git push
```

---

## Step 2: Create First Service - MCP Server

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Select your GitHub repository
4. Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `alchemist-mcp` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r Backend/requirements.txt` |
| **Start Command** | `cd Backend && python mcp_server.py` |
| **Instance Type** | `Free` |

5. Click **"Create Web Service"**
6. Wait for deployment to complete (~2-3 minutes)
7. Note your URL: `https://alchemist-mcp.onrender.com`

### Add Environment Variables for MCP Service

Once deployed, go to **Settings** → **Environment**:

| Key | Value |
|-----|-------|
| `MINDAT_API_KEY` | `your_actual_mindat_key` |

---

## Step 3: Create Second Service - Backend

1. Click **"New +"** → **"Web Service"** again
2. Select the same repository
3. Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `alchemist-backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r Backend/requirements.txt` |
| **Start Command** | `cd Backend && uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| **Instance Type** | `Free` |

4. Click **"Create Web Service"**
5. Wait for deployment (~2-3 minutes)
6. Note your URL: `https://alchemist-backend.onrender.com`

### Add Environment Variables for Backend Service

Once deployed, go to **Settings** → **Environment** and add all these variables:

| Key | Value |
|-----|-------|
| `MCP_SERVER_URL` | `https://alchemist-mcp.onrender.com/mcp` |
| `AZURE_DEPLOYMENT_NAME` | `gpt-4o` |
| `AZURE_OPENAI_API_VERSION` | `2025-01-01-preview` |
| `AZURE_OPENAI_API_ENDPOINT` | `your_actual_azure_endpoint` |
| `AZURE_OPENAI_API_KEY` | `your_actual_azure_key` |
| `MINDAT_API_KEY` | `your_actual_mindat_key` |
| `MINDAT_HOST` | `https://api.mindat.org/v1/` |
| `SUPABASE_URL` | `your_actual_supabase_url` |
| `SUPABASE_KEY` | `your_actual_supabase_key` |
| `DATABASE_URL` | `your_actual_database_url` |
| `LANGSMITH_API_KEY` | `your_actual_langsmith_key` |
| `LANGSMITH_TRACING` | `true` |
| `LANGSMITH_ENDPOINT` | `https://api.smith.langchain.com` |
| `LANGSMITH_PROJECT` | `your_project_name` |

After adding variables, Render will automatically redeploy the service.

---

## Step 4: Verify Deployment

Test both services are running:

```bash
# Test backend health
curl https://alchemist-backend.onrender.com/api/agent/health

# Expected response:
# {"ok": true, "lat_ms": 250.5}

# Test backend root
curl https://alchemist-backend.onrender.com/

# Expected response:
# {"status": "success", "message": "Welcome to...", "timestamp": "..."}
```

If both requests succeed , your deployment is working!

---

## Step 5: Connect Frontend

Update your Frontend `.env` to use the deployed backend:

```javascript
// Frontend/.env or vite.config.js
VITE_API_URL=https://alchemist-backend.onrender.com
```

Then deploy Frontend (on Vercel, Netlify, or Render).

---

## Troubleshooting

### MCP Service fails to start

1. Check **Logs** in Render dashboard
2. Verify `MINDAT_API_KEY` is set correctly
3. Check `Backend/mcp_server.py` has correct imports

**Common error:** `ModuleNotFoundError: No module named 'app'`
- Solution: Ensure `Build Command` is: `pip install -r Backend/requirements.txt`

### Backend can't reach MCP

1. Check `MCP_SERVER_URL` environment variable is exactly: `https://alchemist-mcp.onrender.com/mcp`
2. Check MCP service is still running (check its logs)
3. Click redeploy on backend service

**Common error:** `Could not connect to MCP server at...`
- Solution: Wait 2-3 min for MCP service to fully start, then redeploy backend

### Service keeps restarting

1. Go to service **Settings** → **Instance Type**
2. Upgrade from `Free` to `Starter Plus` ($7/month)
3. Free instances auto-suspend after 15 min of inactivity

### High latency

- Both services are on `Free` tier with limited resources
- Upgrade to `Starter Plus` for better performance

---

## Cost Summary

| Service | Instance Type | Cost/Month |
|---------|---------------|-----------|
| MCP | Free | $0 (auto-hibernates) |
| Backend | Free | $0 (auto-hibernates) |
| **Total** | — | **$0/month** |

**For Production (Recommended):**
- Each on `Starter Plus`: 2 × $7 = **$14/month**
- Includes 750 compute hours + better specs

---

## Local Development (No Changes Needed)

When running locally:

1. **Terminal 1 - Start MCP:**
   ```bash
   cd Backend
   python mcp_server.py
   ```

2. **Terminal 2 - Start Backend:**
   ```bash
   cd Backend
   uvicorn app.main:app --reload --port 8000
   ```

The code automatically uses `http://localhost:8010/mcp` because `MCP_SERVER_URL` is not set in your local `.env`.

---

## Summary of Changes Made

1.  Updated `app/agents/initialize_agent.py` to use `MCP_SERVER_URL` environment variable
2.  Created `Backend/render.yaml` with both service configurations
3.  Updated `Backend/.env.example` with all required variables
4.  Added detailed inline comments to explain the setup

**No other code changes needed!** Your app is ready to deploy. 
