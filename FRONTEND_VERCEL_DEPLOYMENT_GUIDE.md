# Frontend Vercel Deployment Guide - The Alchemist

This guide explains how to deploy the **React frontend** of The Alchemist on Vercel.com.

## Architecture Overview

```
┌──────────────────────────────────────────┐
│  GitHub Repository                       │
│  ├── Backend/                            │
│  ├── Frontend/                           │
│  │   ├── src/                           │
│  │   ├── public/                        │
│  │   ├── package.json                   │
│  │   ├── vite.config.js                 │
│  │   └── .env.example                   │
│  └── README.md                           │
└──────────────────────────────────────────┘
            │
            ▼
    ┌──────────────────────┐
    │ Vercel Deployment    │
    ├──────────────────────┤
    │ Frontend (React+Vite)│
    │ alchemist.vercel.app │
    │                      │
    │ → Connects to →      │
    │ Backend on Render    │
    └──────────────────────┘
            │
            ▼
    https://alchemist-backend.onrender.com
    (FastAPI Backend)
```

---

## Prerequisites

- GitHub account with the repository connected
- Vercel account (free tier available at [vercel.com](https://vercel.com))
- Backend already deployed on Render (see `RENDER_DEPLOYMENT_GUIDE.md`)
- Node.js 18+ installed locally (for testing)

---

## Step 1: Commit All Changes to GitHub

All frontend files have been updated with proper environment variable support. Commit these changes before deploying:

```bash
cd /Users/prateekrauniyar/Documents/SeniorDeisgn-The-Alchemist

# Stage changes
git add Frontend/

# Commit
git commit -m "Update frontend configuration for production deployment"

# Push to GitHub
git push origin main
```

Wait for the push to complete and verify your files are on GitHub before proceeding to Step 2.

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Connect GitHub Repository

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New..."** → **"Project"**
3. Click **"Import Git Repository"**
4. Select your GitHub repository
5. Click **"Import"**

### 2.2 Configure Project Settings

Vercel will auto-detect it's a React/Vite project. Verify the settings:

| Field | Value |
|-------|-------|
| **Framework Preset** | `Vite` |
| **Root Directory** | `Frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |
| **Install Command** | `npm install` |

**Make sure "Root Directory" is set to `Frontend`** 

### 2.3 Add Environment Variables

Click **"Environment Variables"** and add your 3 keys:

| Name | Value |
|------|-------|
| `VITE_API_URL` | Your backend URL (e.g., `https://your-backend.onrender.com`) |
| `VITE_SUPABASE_URL` | Your Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Your Supabase anonymous key |

### 2.4 Deploy

Click **"Deploy"** button. Vercel will automatically:
1. Clone your repository
2. Install dependencies
3. Build the project
4. Deploy to Vercel CDN

Deployment usually takes 1-3 minutes.

### 2.5 Get Your Frontend URL

Once deployed, Vercel displays your live URL (typically `https://[project-name].vercel.app`).

---

## Step 3: Verify Deployment

### 3.1 Test Frontend is Loading

```bash
curl https://your-app.vercel.app/
# Should return HTML content
```

### 3.2 Test Backend Connection

1. Open your frontend: `https://your-app.vercel.app`
2. Open **Developer Console** (F12)
3. Look for network requests going to your backend
4. Verify successful API calls (no 404 or CORS errors)

### 3.3 Test Authentication

1. Try to log in with a test account
2. Check browser console for any errors
3. Verify Supabase connection is working

---

## Step 4: Set Up Custom Domain (Optional)

If you want a custom domain instead of `vercel.app`:

1. Go to Vercel **Project Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain (e.g., `alchemist.com`)
4. Follow DNS setup instructions
5. Wait for DNS propagation (5-30 minutes)

---

## Step 5: Configure Continuous Deployment

Vercel automatically deploys on every push to `main` branch.

To customize:

1. Go to **Project Settings** → **Git**
2. Configure:
   - **Production Branch:** `main`
   - **Preview Branches:** All branches (for testing)

Now every push to `main` auto-deploys!

---

## Troubleshooting

### Frontend loads but backend calls fail

**Error:** `Failed to fetch from /api/agent/chat`

**Possible causes:**
1. `VITE_API_URL` environment variable not set or incorrect
2. Backend service is not running on Render
3. CORS not configured on backend

**Solution:**
1. Check environment variables in Vercel dashboard
2. Verify your Render backend is running (check Render dashboard)
3. Ensure CORS is properly configured in backend's `app/core/app.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-vercel-domain.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Build fails

**Error:** Build fails on Vercel

**Solution:**
1. Check Vercel build logs (Deployments tab)
2. Ensure `Frontend` is set as **Root Directory**
3. Run locally and verify build works: `npm run build`

### Supabase authentication not working

**Error:** Invalid Supabase URL or key

**Solution:**
1. Double-check environment variables in Vercel
2. Ensure keys are marked as **"Secret"**
3. Redeploy after changing env vars

### Environment variables not picked up

**Error:** `VITE_API_URL is undefined`

**Solution:**
1. Variables must start with `VITE_` for Vite
2. Redeploy Vercel after adding/changing env vars
3. Use Vercel dashboard (not `.env` file) for production

---

## Local Development (Before Deploying)

To test your frontend locally before deploying to Vercel:

```bash
# Terminal 1 - Start Backend (if testing locally)
cd Backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Start Frontend
cd Frontend
npm install  # Only needed first time
npm run dev
```

Then open `http://localhost:5173` in your browser.

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `VITE_API_URL` | Backend API endpoint | `https://your-backend.onrender.com` |
| `VITE_SUPABASE_URL` | Supabase project URL | `https://xxxxx.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase public key | Your anon key from Supabase |

---

## Complete Deployment Checklist

- ✅ All changes committed and pushed to GitHub
- ✅ Vercel project created and connected to GitHub
- ✅ Root directory set to `Frontend`
- ✅ Environment variables added in Vercel dashboard
- ✅ Frontend deployed to Vercel
- ✅ Backend (Render) is running and accessible
- ✅ CORS configured on backend
- ✅ Frontend → Backend connection tested
- ✅ Authentication working (Supabase)

---

## What Next?

After successful deployment:

1. **Monitor deployments:**
   - Check Vercel Deployments dashboard for build status
   - Monitor Render for backend health

2. **Optimize:**
   - Enable Vercel Analytics for performance data
   - Check browser console for any client-side errors

3. **Scale up when needed:**
   - Upgrade to paid plans if necessary
   - Add monitoring and error tracking (Sentry, etc.)
   - Set up CI/CD with GitHub Actions

---

## Summary

Your application is now:
- ✅ Frontend deployed on Vercel
- ✅ Backend deployed on Render
- ✅ Auto-deploying on every git push
- ✅ Secured with environment variables
- ✅ Live and accessible

**Your application is ready!** 🎉
