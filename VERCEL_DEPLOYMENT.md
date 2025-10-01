# Vercel Deployment

## Important: Vercel Limitations

⚠️ **Vercel is NOT ideal for this application** because:

1. **Serverless Architecture**: Vercel uses serverless functions with cold starts and execution time limits (10-60 seconds)
2. **Database**: SQLite doesn't work on Vercel (filesystem is read-only). You MUST use PostgreSQL or another external database
3. **APScheduler**: Background scheduler won't work reliably in serverless environment
4. **Redis**: Requires external Redis service (e.g., Redis Labs, Upstash)

## Recommended Alternatives

**Better hosting options for this Flask app:**
- **Railway** (railway.app) - Easy Flask deployment with persistent storage
- **Render** (render.com) - Good for Python apps, free tier available
- **Heroku** - Traditional PaaS, works well with Flask
- **DigitalOcean App Platform** - Reliable and affordable
- **Fly.io** - Modern deployment platform

## If You Still Want to Use Vercel

### Prerequisites

1. **External PostgreSQL Database** (required)
   - Vercel Postgres (recommended)
   - Supabase
   - ElephantSQL
   - AWS RDS

2. **External Redis** (for caching)
   - Upstash Redis (recommended for Vercel)
   - Redis Labs

3. **Remove/Disable APScheduler**
   - Use Vercel Cron Jobs instead
   - Or external cron service (e.g., cron-job.org)

### Environment Variables to Set in Vercel Dashboard

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-strong-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# Database (REQUIRED - use PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Redis (optional but recommended)
REDIS_URL=redis://user:password@host:6379

# API Keys
FINNHUB_API_KEY=your-finnhub-key
TWELVE_DATA_API_KEY=your-twelve-data-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
GOOGLE_API_KEY=your-google-ai-key
OPENAI_API_KEY=your-openai-key

# Email (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email
MAIL_PASSWORD=your-app-password
```

### Deployment Steps

1. **Set up external database** (PostgreSQL)
2. **Push code to GitHub**
3. **Connect Vercel to GitHub repo**
4. **Add all environment variables** in Vercel dashboard
5. **Deploy**

### Troubleshooting 404 Errors

**Common causes:**

1. **Missing `wsgi.py`** - ✅ Now created
2. **Wrong build configuration** - ✅ `vercel.json` configured
3. **Database connection fails** - Check `DATABASE_URL`
4. **Missing environment variables** - Verify in Vercel dashboard
5. **Cold start timeout** - Vercel functions timeout after 10s (hobby) or 60s (pro)

**Check Vercel logs:**
```bash
# Install Vercel CLI
npm i -g vercel

# View logs
vercel logs [your-deployment-url]
```

### Database Migration

If using PostgreSQL, run migrations:
```bash
# Locally with remote database
export DATABASE_URL="your-vercel-postgres-url"
flask db upgrade
```

Or create a Vercel serverless function to run migrations (advanced).

## Current 404 Error - Likely Causes

1. ❌ **No `vercel.json` file** (fixed now)
2. ❌ **No `wsgi.py` file** (fixed now)
3. ⚠️ **SQLite database won't work on Vercel** - MUST use PostgreSQL
4. ⚠️ **Environment variables not set correctly**
5. ⚠️ **App crashes on startup due to missing dependencies**

## Next Steps

1. **Check Vercel deployment logs** in dashboard
2. **Set up PostgreSQL database** (Vercel Postgres recommended)
3. **Update `DATABASE_URL` in Vercel environment variables**
4. **Redeploy after adding these files**

If you continue having issues, **Railway or Render are much better choices** for this type of application.
