# Complete Deployment Guide

This guide walks you through deploying the entire stack from scratch.

---

## Prerequisites

- GitHub account
- Credit card for cloud signups (most have free tiers)
- Node.js 18+ installed locally
- Python 3.11+ installed locally

---

## Step 1: Create Supabase Project (10 minutes)

### 1.1 Sign Up
1. Go to https://supabase.com
2. Click "Start your project" → Sign in with GitHub
3. Click "New Project"
4. Choose organization (create one if needed)
5. Fill in:
   - **Name**: `demo-project`
   - **Database Password**: Generate a strong one → **SAVE THIS**
   - **Region**: Frankfurt (eu-central-1)
6. Click "Create new project" → Wait 2 minutes

### 1.2 Get Connection Details
1. Go to Project Settings → Database
2. Copy the **Connection string (URI)** under "Connection pooling"
   - It looks like: `postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres`
3. Save this as `SUPABASE_DB_URL`

### 1.3 Get API Keys
1. Go to Project Settings → API
2. Copy:
   - **Project URL** → Save as `SUPABASE_URL`
   - **anon public** key → Save as `SUPABASE_ANON_KEY`
   - **service_role** key → Save as `SUPABASE_SERVICE_KEY` (keep secret!)

### 1.4 Run Database Migrations
1. Go to SQL Editor in Supabase dashboard
2. Copy contents of `database/001_initial_schema.sql`
3. Paste and click "Run"

---

## Step 2: Create Anthropic API Key (2 minutes)

1. Go to https://console.anthropic.com
2. Sign up / Sign in
3. Go to API Keys → Create Key
4. Name it `demo-project`
5. Copy the key → Save as `ANTHROPIC_API_KEY`
   - Looks like: `sk-ant-api03-...`

---

## Step 3: Create Cloudflare R2 Bucket (5 minutes)

### 3.1 Sign Up
1. Go to https://dash.cloudflare.com
2. Sign up (free tier includes 10GB R2 storage)
3. In sidebar, click R2 Object Storage

### 3.2 Create Bucket
1. Click "Create bucket"
2. Name: `demo-models`
3. Location: Automatic
4. Click "Create bucket"

### 3.3 Create API Token
1. Go to R2 → Overview → Manage R2 API Tokens
2. Click "Create API token"
3. Name: `demo-backend`
4. Permissions: Object Read & Write
5. Specify bucket: `demo-models`
6. Click "Create API Token"
7. Copy:
   - **Access Key ID** → Save as `R2_ACCESS_KEY_ID`
   - **Secret Access Key** → Save as `R2_SECRET_ACCESS_KEY`
   - **Endpoint** → Save as `R2_ENDPOINT` (looks like `https://[account_id].r2.cloudflarestorage.com`)

---

## Step 4: Deploy Backend to Render (10 minutes)

### 4.1 Push Code to GitHub
1. Create a new GitHub repo: `cloud-demo`
2. Push this entire project to the repo

### 4.2 Create Render Account
1. Go to https://render.com
2. Sign up with GitHub

### 4.3 Deploy Backend
1. Click "New" → "Web Service"
2. Connect your GitHub repo
3. Configure:
   - **Name**: `demo-api`
   - **Region**: Frankfurt (EU Central)
   - **Branch**: main
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: Free

4. Add Environment Variables (click "Advanced" → "Add Environment Variable"):
   ```
   SUPABASE_DB_URL=postgresql://postgres.[ref]:[password]@...
   SUPABASE_URL=https://[ref].supabase.co
   SUPABASE_SERVICE_KEY=eyJ...
   ANTHROPIC_API_KEY=sk-ant-api03-...
   R2_ACCESS_KEY_ID=...
   R2_SECRET_ACCESS_KEY=...
   R2_ENDPOINT=https://[account_id].r2.cloudflarestorage.com
   R2_BUCKET_NAME=demo-models
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

5. Click "Create Web Service"
6. Wait for deploy → Copy the URL (e.g., `https://demo-api.onrender.com`)
7. Save this as `BACKEND_URL`

---

## Step 5: Deploy Frontend to Vercel (5 minutes)

### 5.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

### 5.2 Deploy
1. Click "Add New" → "Project"
2. Import your GitHub repo
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`

4. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://demo-api.onrender.com
   NEXT_PUBLIC_SUPABASE_URL=https://[ref].supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
   ```

5. Click "Deploy"
6. Copy your deployment URL (e.g., `https://cloud-demo.vercel.app`)

### 5.3 Update Backend CORS
1. Go back to Render dashboard
2. Update `ALLOWED_ORIGINS` to your actual Vercel URL
3. Redeploy

---

## Step 6: Deploy Metabase to Render (10 minutes)

### 6.1 Create Metabase Service
1. In Render, click "New" → "Web Service"
2. Choose "Deploy an existing image from a registry"
3. Image URL: `metabase/metabase:latest`
4. Configure:
   - **Name**: `demo-metabase`
   - **Region**: Frankfurt
   - **Instance Type**: Free (or Starter for better performance)

5. Add Environment Variables:
   ```
   MB_DB_TYPE=postgres
   MB_DB_CONNECTION_URI=postgresql://postgres.[ref]:[password]@...
   MB_SITE_URL=https://demo-metabase.onrender.com
   MB_EMBEDDING_SECRET_KEY=<generate-a-64-char-random-string>
   ```

   Generate secret key with: `openssl rand -hex 32`

6. Click "Create Web Service"
7. Wait 5-10 minutes for first boot
8. Access Metabase at your Render URL
9. Complete setup wizard:
   - Create admin account
   - Add database connection (use same Supabase connection string)
   - Enable embedding in Admin → Settings → Embedding

### 6.2 Add Metabase Secret to Backend
1. Go to Render → demo-api → Environment
2. Add: `METABASE_SECRET_KEY=<same-64-char-key>`
3. Add: `METABASE_URL=https://demo-metabase.onrender.com`
4. Redeploy

---

## Step 7: Configure GitHub Actions (5 minutes)

### 7.1 Add Repository Secrets
1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Add these secrets:
   ```
   SUPABASE_DB_URL=postgresql://...
   R2_ACCESS_KEY_ID=...
   R2_SECRET_ACCESS_KEY=...
   R2_ENDPOINT=https://...
   R2_BUCKET_NAME=demo-models
   ```

### 7.2 Enable Workflows
1. Go to Actions tab in your repo
2. Click "I understand my workflows, go ahead and enable them"

The workflow runs daily at 2 AM UTC. To test manually:
1. Go to Actions → "Nightly ETL and ML Pipeline"
2. Click "Run workflow"

---

## Step 8: Test Everything (5 minutes)

### 8.1 Test Auth
1. Open your Vercel URL
2. Click "Sign Up"
3. Create an account
4. Verify you're logged in

### 8.2 Test Database
1. Click "Test Database" button
2. Should show connection success

### 8.3 Test AI
1. Type a message in the chat
2. Should get a response from Claude

### 8.4 Test File Storage
1. Click "Test R2 Upload"
2. Should show upload success

### 8.5 Test Metabase
1. Click "View Dashboard"
2. Should show embedded Metabase chart

---

## Troubleshooting

### "CORS error" in browser console
- Verify `ALLOWED_ORIGINS` in Render matches your Vercel URL exactly
- Redeploy backend after changing

### "Connection refused" to database
- Check Supabase is not paused (free tier pauses after 1 week inactivity)
- Verify connection string is correct

### Claude returns error
- Check API key is valid at console.anthropic.com
- Verify you have credits/billing set up

### Metabase embed not loading
- Verify embedding is enabled in Metabase admin
- Check secret keys match between Metabase and backend

---

## Cost Estimate (Monthly)

| Service | Tier | Cost |
|---------|------|------|
| Vercel | Free | $0 |
| Render (API) | Free | $0 |
| Render (Metabase) | Free | $0 |
| Supabase | Free | $0 |
| Cloudflare R2 | Free (10GB) | $0 |
| GitHub Actions | Free (2000 min) | $0 |
| Anthropic | Pay-as-you-go | ~$1-5 |

**Total: ~$1-5/month** (only Claude API costs money)

---

## Next Steps

After confirming everything works:
1. Add real data to Supabase
2. Create Metabase dashboards
3. Customize the chatbot prompts
4. Add more API endpoints
5. Set up custom domain
