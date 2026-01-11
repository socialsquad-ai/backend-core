# Heroku Setup Guide

This guide walks through setting up the Social Squad backend on Heroku.

## Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Heroku account with billing enabled (for Postgres addon)
- GitHub repository secrets configured

## Architecture

Each environment (staging/production) uses **separate Heroku apps** for each service:
- **API App** - FastAPI API server (web dyno)
- **Worker App** - TaskIQ background worker (web dyno)
- **Heroku Postgres** - Database attached to both apps

```
Staging Environment:
├── ssq-api-staging (API app)
│   ├── web dyno (FastAPI)
│   └── DATABASE_URL → Heroku Postgres
├── ssq-worker-staging (Worker app)
│   ├── web dyno (TaskIQ)
│   └── DATABASE_URL → Same Heroku Postgres (attached)
└── Heroku Postgres (primary on API app)

Production Environment:
├── ssq-api-production (API app)
│   ├── web dyno (FastAPI)
│   └── DATABASE_URL → Heroku Postgres
├── ssq-worker-production (Worker app)
│   ├── web dyno (TaskIQ)
│   └── DATABASE_URL → Same Heroku Postgres (attached)
└── Heroku Postgres (primary on API app)
```

**Why separate apps?** Heroku apps are single-service units. This architecture allows:
- Independent scaling of API and Worker
- Clearer resource monitoring per service
- Simpler deployment and rollback per service

## One-Time Setup

### 1. Login to Heroku

```bash
heroku login
```

### 2. Create Apps

Create 4 apps total (2 per environment):

```bash
# Staging apps
heroku create ssq-api-staging --stack container
heroku create ssq-worker-staging --stack container

# Production apps
heroku create ssq-api-production --stack container
heroku create ssq-worker-production --stack container
```

### 3. Add Postgres Addon

Add Postgres to the API apps, then attach to Worker apps:

```bash
# Staging - Add Postgres to API app
heroku addons:create heroku-postgresql:essential-0 -a ssq-api-staging

# Attach the same database to Worker app
heroku addons:attach $(heroku addons:info heroku-postgresql -a ssq-api-staging --json | jq -r '.name') -a ssq-worker-staging

# Production - Add Postgres to API app
heroku addons:create heroku-postgresql:essential-0 -a ssq-api-production

# Attach the same database to Worker app
heroku addons:attach $(heroku addons:info heroku-postgresql -a ssq-api-production --json | jq -r '.name') -a ssq-worker-production
```

This sets `DATABASE_URL` on both API and Worker apps, pointing to the same database.

### 4. Set Config Vars

Set environment variables on all 4 apps. API and Worker apps in the same environment share the same config values:

```bash
# Staging API app
heroku config:set -a ssq-api-staging \
  APP_ENVIRONMENT=staging \
  DEBUG=False \
  SSQ_SECRET_KEY="your-secret-key" \
  SSQ_ALGORITHM=HS256 \
  SSQ_ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  SSQ_BASE_URL="https://ssq-api-staging.herokuapp.com" \
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

# Staging Worker app (same values, DATABASE_URL already set via attach)
heroku config:set -a ssq-worker-staging \
  APP_ENVIRONMENT=staging \
  DEBUG=False \
  SSQ_SECRET_KEY="your-secret-key" \
  SSQ_ALGORITHM=HS256 \
  SSQ_ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  SSQ_BASE_URL="https://ssq-api-staging.herokuapp.com" \
  SSQ_CLIENT_URL="https://your-frontend-staging.com" \
  AUTH0_DOMAIN="your-tenant.auth0.com" \
  AUTH0_AUDIENCE="your-audience" \
  AUTH0_ISSUER="https://your-tenant.auth0.com/" \
  INTERNAL_AUTH_API_KEY="your-internal-key" \
  META_CLIENT_ID="xxx" \
  META_CLIENT_SECRET="xxx" \
  GOOGLE_CLIENT_ID="xxx" \
  GOOGLE_CLIENT_SECRET="xxx"

# Production API app (repeat with production values)
heroku config:set -a ssq-api-production \
  APP_ENVIRONMENT=production \
  # ... (same vars with production values)

# Production Worker app (repeat with production values)
heroku config:set -a ssq-worker-production \
  APP_ENVIRONMENT=production \
  # ... (same vars with production values)
```

### 5. Configure GitHub Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description | Example |
|--------|-------------|---------|
| `HEROKU_API_KEY` | Your Heroku API key | Found in Heroku Account Settings |
| `HEROKU_STAGING_API_APP` | Staging API app name | `ssq-api-staging` |
| `HEROKU_STAGING_WORKER_APP` | Staging Worker app name | `ssq-worker-staging` |
| `HEROKU_PRODUCTION_API_APP` | Production API app name | `ssq-api-production` |
| `HEROKU_PRODUCTION_WORKER_APP` | Production Worker app name | `ssq-worker-production` |

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
# Login to registry
heroku container:login

# Build and push API (staging example)
docker build --target production -t registry.heroku.com/ssq-api-staging/web .
docker push registry.heroku.com/ssq-api-staging/web
heroku container:release web -a ssq-api-staging

# Build and push Worker (staging example)
docker build --target worker-production -t registry.heroku.com/ssq-worker-staging/web .
docker push registry.heroku.com/ssq-worker-staging/web
heroku container:release web -a ssq-worker-staging
```

Note: API uses `--target production`, Worker uses `--target worker-production`.

## Scaling Dynos

After first deployment, scale your dynos (each app has only `web` dyno type):

```bash
# Staging
heroku ps:scale web=1 -a ssq-api-staging
heroku ps:scale web=1 -a ssq-worker-staging

# Production (adjust based on load)
heroku ps:scale web=2 -a ssq-api-production
heroku ps:scale web=1 -a ssq-worker-production
```

## Viewing Logs

```bash
# API logs
heroku logs --tail -a ssq-api-staging

# Worker logs
heroku logs --tail -a ssq-worker-staging
```

## Database Management

The database is attached to both API and Worker apps. Use the API app for database management:

### Connect to Database

```bash
heroku pg:psql -a ssq-api-staging
```

### View Database Info

```bash
heroku pg:info -a ssq-api-staging
```

### Run Migrations

If you have SQL migration files:

```bash
# Get database credentials
heroku pg:credentials:url -a ssq-api-staging

# Run migration
heroku pg:psql -a ssq-api-staging < data_adapter/sql-postgres/1.initial_setup.sql
```

## Useful Commands

```bash
# View app info
heroku apps:info -a ssq-api-staging
heroku apps:info -a ssq-worker-staging

# View config vars
heroku config -a ssq-api-staging

# View running dynos
heroku ps -a ssq-api-staging
heroku ps -a ssq-worker-staging

# Restart dynos
heroku restart -a ssq-api-staging
heroku restart -a ssq-worker-staging

# Open API app in browser
heroku open -a ssq-api-staging
```

## Zero-Downtime Deployments (Optional)

Enable Preboot for zero-downtime deployments (primarily useful for API apps):

```bash
# Staging
heroku features:enable preboot -a ssq-api-staging

# Production
heroku features:enable preboot -a ssq-api-production
```

With Preboot:
1. New dynos start alongside old ones
2. Once healthy, traffic shifts to new dynos
3. Old dynos are gracefully shut down

## Troubleshooting

### App Crashes on Startup

Check logs for errors:
```bash
heroku logs --tail -a ssq-api-staging
heroku logs --tail -a ssq-worker-staging
```

Common issues:
- Missing config vars (DATABASE_URL, AUTH0_*, etc.)
- Database connection failures
- Port binding issues (ensure using `$PORT` from Heroku)

### Worker Not Processing Tasks

1. Verify worker is running: `heroku ps -a ssq-worker-staging`
2. Check worker logs: `heroku logs --tail -a ssq-worker-staging`
3. Verify DATABASE_URL is set: `heroku config:get DATABASE_URL -a ssq-worker-staging`

### Database Connection Issues

```bash
# Check database status
heroku pg:info -a ssq-api-staging

# Test connection
heroku pg:psql -a ssq-api-staging -c "SELECT 1"
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
