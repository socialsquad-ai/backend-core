# Heroku Setup Guide

This guide walks through setting up the Social Squad backend on Heroku.

## Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Heroku account with billing enabled (for Postgres addon)
- GitHub repository secrets configured

## Architecture

Each environment (staging/production) consists of:
- **1 Heroku App** with two dyno types:
  - `web` - FastAPI API server
  - `worker` - TaskIQ background worker
- **Heroku Postgres** - Shared database for both dynos

```
ssq-staging (app)
├── web dyno (API)
├── worker dyno (TaskIQ)
└── Heroku Postgres (DATABASE_URL)

ssq-production (app)
├── web dyno (API)
├── worker dyno (TaskIQ)
└── Heroku Postgres (DATABASE_URL)
```

## One-Time Setup

### 1. Login to Heroku

```bash
heroku login
```

### 2. Create Apps

```bash
# Staging
heroku create ssq-staging --stack container

# Production
heroku create ssq-production --stack container
```

### 3. Add Postgres Addon

```bash
# Staging (essential-0 is the cheapest plan)
heroku addons:create heroku-postgresql:essential-0 -a ssq-staging

# Production (choose appropriate plan)
heroku addons:create heroku-postgresql:essential-0 -a ssq-production
```

This automatically sets the `DATABASE_URL` config var.

### 4. Set Config Vars

For each app, set the required environment variables:

```bash
# Staging
heroku config:set -a ssq-staging \
  APP_ENVIRONMENT=staging \
  DEBUG=False \
  SSQ_SECRET_KEY="your-secret-key" \
  SSQ_ALGORITHM=HS256 \
  SSQ_ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  SSQ_BASE_URL="https://ssq-staging.herokuapp.com" \
  SSQ_CLIENT_URL="https://your-frontend-staging.com" \
  CORS_ORIGINS="https://your-frontend-staging.com" \
  AUTH0_DOMAIN="your-tenant.auth0.com" \
  AUTH0_AUDIENCE="your-audience" \
  AUTH0_ISSUER="https://your-tenant.auth0.com/" \
  INTERNAL_AUTH_API_KEY="your-internal-key" \
  META_CLIENT_ID="xxx" \
  META_CLIENT_SECRET="xxx" \
  GOOGLE_CLIENT_ID="xxx" \
  GOOGLE_CLIENT_SECRET="xxx"

# Production (repeat with production values)
heroku config:set -a ssq-production \
  APP_ENVIRONMENT=production \
  # ... (same vars with production values)
```

### 5. Configure GitHub Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description | Example |
|--------|-------------|---------|
| `HEROKU_API_KEY` | Your Heroku API key | Found in Heroku Account Settings |
| `HEROKU_STAGING_APP` | Staging app name | `ssq-staging` |
| `HEROKU_PRODUCTION_APP` | Production app name | `ssq-production` |

To get your Heroku API key:
1. Go to [Heroku Account Settings](https://dashboard.heroku.com/account)
2. Scroll to "API Key" section
3. Click "Reveal" and copy

## Deploying

### Via GitHub Actions (Recommended)

1. Go to **Actions** tab in GitHub
2. Select **Deploy to Staging** or **Deploy to Production**
3. Click **Run workflow**
4. Select the branch to deploy
5. Click **Run workflow**

### Manual Deployment

```bash
# Build and push
docker build --target heroku-production -t registry.heroku.com/ssq-staging/web .
docker build --target heroku-production -t registry.heroku.com/ssq-staging/worker .

# Login to registry
heroku container:login

# Push images
docker push registry.heroku.com/ssq-staging/web
docker push registry.heroku.com/ssq-staging/worker

# Release
heroku container:release web worker -a ssq-staging
```

## Scaling Dynos

After first deployment, scale your dynos:

```bash
# Staging
heroku ps:scale web=1 worker=1 -a ssq-staging

# Production (adjust based on load)
heroku ps:scale web=2 worker=1 -a ssq-production
```

## Viewing Logs

```bash
# All logs
heroku logs --tail -a ssq-staging

# Web dyno only
heroku logs --tail --dyno web -a ssq-staging

# Worker dyno only
heroku logs --tail --dyno worker -a ssq-staging
```

## Database Management

### Connect to Database

```bash
heroku pg:psql -a ssq-staging
```

### View Database Info

```bash
heroku pg:info -a ssq-staging
```

### Run Migrations

If you have SQL migration files:

```bash
# Get database credentials
heroku pg:credentials:url -a ssq-staging

# Run migration
heroku pg:psql -a ssq-staging < data_adapter/sql-postgres/1.initial_setup.sql
```

## Useful Commands

```bash
# View app info
heroku apps:info -a ssq-staging

# View config vars
heroku config -a ssq-staging

# View running dynos
heroku ps -a ssq-staging

# Restart dynos
heroku restart -a ssq-staging

# Open app in browser
heroku open -a ssq-staging
```

## Zero-Downtime Deployments (Optional)

Enable Preboot for zero-downtime deployments:

```bash
heroku features:enable preboot -a ssq-staging
heroku features:enable preboot -a ssq-production
```

With Preboot:
1. New dynos start alongside old ones
2. Once healthy, traffic shifts to new dynos
3. Old dynos are gracefully shut down

## Troubleshooting

### App Crashes on Startup

Check logs for errors:
```bash
heroku logs --tail -a ssq-staging
```

Common issues:
- Missing config vars (DATABASE_URL, AUTH0_*, etc.)
- Database connection failures
- Port binding issues (ensure using `$PORT` from Heroku)

### Worker Not Processing Tasks

1. Verify worker is running: `heroku ps -a ssq-staging`
2. Check worker logs: `heroku logs --dyno worker -a ssq-staging`
3. Verify DATABASE_URL is accessible to worker

### Database Connection Issues

```bash
# Check database status
heroku pg:info -a ssq-staging

# Test connection
heroku pg:psql -a ssq-staging -c "SELECT 1"
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Auto | Set by Heroku Postgres addon |
| `APP_ENVIRONMENT` | Yes | `staging` or `production` |
| `DEBUG` | Yes | `False` for production |
| `SSQ_SECRET_KEY` | Yes | JWT signing key |
| `SSQ_ALGORITHM` | Yes | JWT algorithm (default: HS256) |
| `SSQ_ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Token expiry |
| `SSQ_BASE_URL` | Yes | This API's URL |
| `SSQ_CLIENT_URL` | Yes | Frontend URL |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins |
| `AUTH0_DOMAIN` | Yes | Auth0 tenant domain |
| `AUTH0_AUDIENCE` | Yes | Auth0 API audience |
| `AUTH0_ISSUER` | Yes | Auth0 issuer URL |
| `INTERNAL_AUTH_API_KEY` | Yes | Internal service auth |
| `META_CLIENT_ID` | Yes | Facebook/Meta app ID |
| `META_CLIENT_SECRET` | Yes | Facebook/Meta app secret |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth client secret |
