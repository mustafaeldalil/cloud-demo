# Cloud Architecture Demo

A minimal demo solution testing connectivity between:
- **Vercel** (Next.js frontend)
- **Render** (FastAPI backend + Metabase)
- **Supabase** (Postgres + Auth + Storage)
- **Anthropic** (Claude AI)
- **Cloudflare R2** (Object storage)
- **GitHub Actions** (Scheduled jobs)

## Quick Start

See `docs/DEPLOYMENT.md` for complete step-by-step deployment instructions.

## Project Structure

```
cloud-demo/
├── frontend/          # Next.js app (deploys to Vercel)
├── backend/           # FastAPI app (deploys to Render)
├── database/          # SQL migrations for Supabase
├── .github/workflows/ # GitHub Actions for scheduled jobs
└── docs/              # Deployment guides
```

## What This Demo Tests

1. **User Auth Flow**: Supabase Auth → JWT → Backend verification
2. **Database Connectivity**: Backend → Supabase Postgres
3. **AI Integration**: Backend → Claude API
4. **File Storage**: Backend → Cloudflare R2
5. **Scheduled Jobs**: GitHub Actions → Supabase
6. **Embedded Analytics**: Metabase iframe embedding

## Architecture Diagram

```
Browser → Vercel (Next.js) → Render (FastAPI) → Supabase (Postgres)
                                    ↓
                              Anthropic (Claude)
                                    ↓
                              Cloudflare R2
```
