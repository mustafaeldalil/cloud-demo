# Secrets Checklist

Use this checklist to track which secrets you've configured in each service.

---

## Supabase (source of truth)

After creating your Supabase project, you'll have:

| Secret | Where to find it | Used by |
|--------|------------------|---------|
| `SUPABASE_URL` | Project Settings → API → Project URL | Frontend, Backend |
| `SUPABASE_ANON_KEY` | Project Settings → API → **Publishable key** | Frontend |
| `SUPABASE_SERVICE_KEY` | Project Settings → API → **Secret key** | Backend |
| `SUPABASE_DB_URL` | Project Settings → Database → Connection string (pooler) | Backend, GitHub Actions |

---

## Anthropic

| Secret | Where to find it | Used by |
|--------|------------------|---------|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys | Backend |

---

## Cloudflare R2

| Secret | Where to find it | Used by |
|--------|------------------|---------|
| `R2_ACCESS_KEY_ID` | R2 → Manage API Tokens | Backend, GitHub Actions |
| `R2_SECRET_ACCESS_KEY` | R2 → Manage API Tokens | Backend, GitHub Actions |
| `R2_ENDPOINT` | R2 → Overview (account ID) | Backend, GitHub Actions |
| `R2_BUCKET_NAME` | R2 → Your bucket name | Backend, GitHub Actions |

---

## Metabase

| Secret | Where to find it | Used by |
|--------|------------------|---------|
| `METABASE_SECRET_KEY` | Generate with `openssl rand -hex 32` | Backend, Metabase |
| `METABASE_URL` | Your Render Metabase URL | Backend |

---

## Configuration by Service

### Vercel (Frontend)
```
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
```

### Render - Backend API
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_DB_URL=postgresql://...
ANTHROPIC_API_KEY=sk-ant-...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com
R2_BUCKET_NAME=demo-models
METABASE_URL=https://your-metabase.onrender.com
METABASE_SECRET_KEY=<64-char-hex>
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### Render - Metabase
```
MB_DB_TYPE=postgres
MB_DB_CONNECTION_URI=postgresql://...
MB_SITE_URL=https://your-metabase.onrender.com
MB_EMBEDDING_SECRET_KEY=<same-64-char-hex>
```

### GitHub Actions Secrets
```
SUPABASE_DB_URL=postgresql://...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ENDPOINT=https://xxx.r2.cloudflarestorage.com
R2_BUCKET_NAME=demo-models
```

---

## Verification Commands

Test each connection locally before deploying:

```bash
# Test Supabase connection
psql "postgresql://postgres.[ref]:[password]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres" -c "SELECT 1;"

# Test Anthropic
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-haiku-20240307","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'

# Test R2 (using AWS CLI with custom endpoint)
aws s3 ls s3://demo-models/ --endpoint-url $R2_ENDPOINT
```
