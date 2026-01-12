# Heroku Setup Guide

This guide walks through setting up the Social Squad backend on Heroku.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Architecture](#architecture)
- [One-Time Setup](#one-time-setup)
- [App URLs](#app-urls)
- [Custom Domains](#custom-domains)
- [Deploying](#deploying)
- [Scaling](#scaling)
- [Heroku Dashboard](#heroku-dashboard)
- [Viewing Logs](#viewing-logs)
- [Database Management](#database-management)
- [Zero-Downtime Deployments](#zero-downtime-deployments-optional)
- [Useful Commands](#useful-commands)
- [Troubleshooting](#troubleshooting)
- [Environment Variables Reference](#environment-variables-reference)

---

## Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Heroku account with billing enabled (for Postgres addon)
- GitHub repository secrets configured
- (Optional) Custom domain registered (e.g., GoDaddy, Namecheap, Cloudflare)

---

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

---

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

# Get the addon name and attach to Worker app
heroku addons:attach $(heroku addons -a ssq-api-staging --json | jq -r '.[0].name') -a ssq-worker-staging

# Production - Add Postgres to API app
heroku addons:create heroku-postgresql:essential-0 -a ssq-api-production

# Get the addon name and attach to Worker app
heroku addons:attach $(heroku addons -a ssq-api-production --json | jq -r '.[0].name') -a ssq-worker-production
```

**Alternative (if jq is not installed):**
```bash
# List addons to see the name
heroku addons -a ssq-api-staging
# Output shows something like: postgresql-cubed-12345

# Then attach using that name
heroku addons:attach postgresql-cubed-12345 -a ssq-worker-staging
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
  DEBUG=False \
  SSQ_SECRET_KEY="your-production-secret-key" \
  SSQ_ALGORITHM=HS256 \
  SSQ_ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  SSQ_BASE_URL="https://ssq-api-production.herokuapp.com" \
  SSQ_CLIENT_URL="https://your-frontend.com" \
  CORS_ORIGINS="https://your-frontend.com" \
  AUTH0_DOMAIN="your-tenant.auth0.com" \
  AUTH0_AUDIENCE="your-audience" \
  AUTH0_ISSUER="https://your-tenant.auth0.com/" \
  INTERNAL_AUTH_API_KEY="your-production-internal-key" \
  META_CLIENT_ID="xxx" \
  META_CLIENT_SECRET="xxx" \
  GOOGLE_CLIENT_ID="xxx" \
  GOOGLE_CLIENT_SECRET="xxx"

# Production Worker app (same as production API)
heroku config:set -a ssq-worker-production \
  APP_ENVIRONMENT=production \
  DEBUG=False \
  SSQ_SECRET_KEY="your-production-secret-key" \
  SSQ_ALGORITHM=HS256 \
  SSQ_ACCESS_TOKEN_EXPIRE_MINUTES=30 \
  SSQ_BASE_URL="https://ssq-api-production.herokuapp.com" \
  SSQ_CLIENT_URL="https://your-frontend.com" \
  AUTH0_DOMAIN="your-tenant.auth0.com" \
  AUTH0_AUDIENCE="your-audience" \
  AUTH0_ISSUER="https://your-tenant.auth0.com/" \
  INTERNAL_AUTH_API_KEY="your-production-internal-key" \
  META_CLIENT_ID="xxx" \
  META_CLIENT_SECRET="xxx" \
  GOOGLE_CLIENT_ID="xxx" \
  GOOGLE_CLIENT_SECRET="xxx"
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

**To get your Heroku API key:**
1. Go to [Heroku Account Settings](https://dashboard.heroku.com/account)
2. Scroll to "API Key" section
3. Click "Reveal" and copy

---

## App URLs

### Default Heroku URLs

When you create a Heroku app, it automatically gets a URL:

```
https://<app-name>.herokuapp.com
```

**Your app URLs:**

| App | Default URL | Purpose |
|-----|-------------|---------|
| `ssq-api-staging` | `https://ssq-api-staging.herokuapp.com` | Staging API for frontend |
| `ssq-api-production` | `https://ssq-api-production.herokuapp.com` | Production API for frontend |
| `ssq-worker-staging` | `https://ssq-worker-staging.herokuapp.com` | Not used (workers don't serve HTTP) |
| `ssq-worker-production` | `https://ssq-worker-production.herokuapp.com` | Not used (workers don't serve HTTP) |

**Example API calls from your frontend:**
```javascript
// Staging
const API_URL = 'https://ssq-api-staging.herokuapp.com';
fetch(`${API_URL}/v1/status/`);

// Production
const API_URL = 'https://ssq-api-production.herokuapp.com';
fetch(`${API_URL}/v1/users/me`);
```

### View Your App URL

```bash
# View app info including URL
heroku apps:info -a ssq-api-production

# Open app in browser
heroku open -a ssq-api-production
```

### Via Heroku Dashboard

1. Go to [Heroku Dashboard](https://dashboard.heroku.com/apps)
2. Click on your app (e.g., `ssq-api-production`)
3. The URL is shown at the top: **Open app** button or in **Settings → Domains**

---

## Custom Domains

If you want to use your own domain (e.g., `api.yourdomain.com`) instead of `.herokuapp.com`:

### Step 1: Add Domain to Heroku

```bash
# Add custom domain
heroku domains:add api.yourdomain.com -a ssq-api-production

# View the DNS target Heroku provides
heroku domains -a ssq-api-production
```

**Example output:**
```
=== ssq-api-production Heroku Domain
ssq-api-production-abc123def456.herokuapp.com

=== ssq-api-production Custom Domains
Domain Name           DNS Record Type  DNS Target
────────────────────  ───────────────  ──────────────────────────────────────────
api.yourdomain.com    CNAME            api.yourdomain.com.herokudns.com
```

**Important:** Copy the **DNS Target** (e.g., `api.yourdomain.com.herokudns.com`) - you'll need this for DNS setup.

### Step 2: Configure DNS at Your Domain Registrar

#### GoDaddy

1. Log in to [GoDaddy](https://www.godaddy.com/)
2. Go to **My Products** → Find your domain → Click **DNS**
3. Click **Add** under DNS Records
4. Add a CNAME record:

| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | `api` (for api.yourdomain.com) |
| Value | `api.yourdomain.com.herokudns.com` (the DNS Target from Heroku) |
| TTL | 600 seconds (or default) |

5. Click **Save**

#### Namecheap

1. Log in to [Namecheap](https://www.namecheap.com/)
2. Go to **Domain List** → Click **Manage** next to your domain
3. Go to **Advanced DNS** tab
4. Click **Add New Record**
5. Add a CNAME record:

| Field | Value |
|-------|-------|
| Type | CNAME Record |
| Host | `api` |
| Value | `api.yourdomain.com.herokudns.com` |
| TTL | Automatic |

6. Click the checkmark to save

#### Cloudflare

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Select your domain
3. Go to **DNS** → **Records**
4. Click **Add record**
5. Add a CNAME record:

| Field | Value |
|-------|-------|
| Type | CNAME |
| Name | `api` |
| Target | `api.yourdomain.com.herokudns.com` |
| Proxy status | **DNS only** (grey cloud) - Important! |
| TTL | Auto |

6. Click **Save**

**Note:** For Cloudflare, set proxy to "DNS only" (grey cloud) to avoid SSL conflicts with Heroku.

### Step 3: Verify DNS Propagation

DNS changes can take 5 minutes to 48 hours to propagate. Check status:

```bash
# Check if DNS is resolving
dig api.yourdomain.com CNAME

# Or use online tool
# https://dnschecker.org/#CNAME/api.yourdomain.com
```

### Step 4: Enable SSL (Automatic)

Heroku automatically provisions SSL certificates for custom domains using Let's Encrypt:

```bash
# Check SSL status
heroku certs:auto -a ssq-api-production

# If needed, enable auto SSL
heroku certs:auto:enable -a ssq-api-production
```

### Step 5: Update Config Vars

After setting up custom domain, update your config vars:

```bash
heroku config:set -a ssq-api-production \
  SSQ_BASE_URL="https://api.yourdomain.com" \
  CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

heroku config:set -a ssq-worker-production \
  SSQ_BASE_URL="https://api.yourdomain.com"
```

### Multiple Custom Domains

You can add multiple domains to one app:

```bash
# Add www subdomain
heroku domains:add www.api.yourdomain.com -a ssq-api-production

# Add staging subdomain
heroku domains:add api-staging.yourdomain.com -a ssq-api-staging

# List all domains
heroku domains -a ssq-api-production
```

### Remove a Custom Domain

```bash
heroku domains:remove api.yourdomain.com -a ssq-api-production
```

---

## Deploying

### Via GitHub Actions (Recommended)

1. Go to **Actions** tab in GitHub
2. Select **Deploy to Staging** or **Deploy to Production**
3. Click **Run workflow**
4. Select the branch to deploy
5. Click **Run workflow**

The workflow will:
- Build the Docker images
- Push to Heroku Container Registry
- Release both API and Worker apps
- Show deployment summary

### Manual Deployment

```bash
# Login to Heroku Container Registry
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

**Note:** API uses `--target production`, Worker uses `--target worker-production`.

---

## Scaling

### Understanding Dynos

- **Dyno** = A container that runs your app
- **Web dyno** = Handles HTTP requests (API) or runs background processes (Worker)
- **Dyno types** = Basic, Standard-1X, Standard-2X, Performance-M, Performance-L (more resources)

### Manual Scaling

#### Scale Number of Dynos

```bash
# Scale to 1 dyno (default)
heroku ps:scale web=1 -a ssq-api-production

# Scale up for more traffic
heroku ps:scale web=3 -a ssq-api-production

# Scale down
heroku ps:scale web=1 -a ssq-api-production

# Turn off (0 dynos)
heroku ps:scale web=0 -a ssq-api-production
```

#### Change Dyno Type (Size)

```bash
# View current dyno type
heroku ps -a ssq-api-production

# Upgrade to Standard-1X (512MB RAM)
heroku ps:type web=standard-1x -a ssq-api-production

# Upgrade to Standard-2X (1GB RAM)
heroku ps:type web=standard-2x -a ssq-api-production

# Upgrade to Performance-M (2.5GB RAM) - for high traffic
heroku ps:type web=performance-m -a ssq-api-production

# Downgrade back to Basic
heroku ps:type web=basic -a ssq-api-production
```

#### Recommended Scaling Strategy

| Environment | API Dynos | API Type | Worker Dynos | Worker Type |
|-------------|-----------|----------|--------------|-------------|
| Staging | 1 | basic | 1 | basic |
| Production (low) | 1-2 | standard-1x | 1 | standard-1x |
| Production (medium) | 2-4 | standard-2x | 1-2 | standard-1x |
| Production (high) | 4+ | performance-m | 2+ | standard-2x |

### Autoscaling

Heroku offers autoscaling for Performance and Private dynos.

#### Enable Autoscaling (Performance dynos only)

```bash
# First, upgrade to Performance dynos
heroku ps:type web=performance-m -a ssq-api-production

# Enable autoscaling (min 2, max 10 dynos)
heroku autoscale:enable web -a ssq-api-production --min 2 --max 10

# View autoscaling status
heroku autoscale -a ssq-api-production

# Disable autoscaling
heroku autoscale:disable web -a ssq-api-production
```

#### Autoscaling via Heroku Dashboard

1. Go to [Heroku Dashboard](https://dashboard.heroku.com/apps)
2. Click on your app (e.g., `ssq-api-production`)
3. Go to **Resources** tab
4. Click the **pencil icon** next to your dyno
5. Enable **Autoscaling** (if available for your dyno type)
6. Set **Min** and **Max** dynos
7. Set **Target Response Time** (e.g., 200ms)
8. Click **Confirm**

**Note:** Autoscaling is based on response time. Heroku adds dynos when response time exceeds your target.

#### Third-Party Autoscaling (For Standard Dynos)

For Standard dynos, use addons like:

```bash
# Rails Autoscale (works with any language)
heroku addons:create railsautoscale -a ssq-api-production

# Adept Scale
heroku addons:create adept-scale -a ssq-api-production
```

### View Current Scale

```bash
# View all dynos and their status
heroku ps -a ssq-api-production

# Example output:
# === web (Standard-2X): uvicorn server.app:app --host 0.0.0.0 --port $PORT (2)
# web.1: up 2024/01/15 10:30:00 +0000 (~ 2h ago)
# web.2: up 2024/01/15 10:30:05 +0000 (~ 2h ago)
```

---

## Heroku Dashboard

### Accessing the Dashboard

1. Go to [https://dashboard.heroku.com/apps](https://dashboard.heroku.com/apps)
2. Log in with your Heroku credentials

### Dashboard Overview

| Tab | What It Shows |
|-----|---------------|
| **Overview** | App status, dyno hours used, recent activity |
| **Resources** | Dynos (scale here), Add-ons (Postgres, Redis, etc.) |
| **Deploy** | Deployment method, activity log |
| **Metrics** | Response time, throughput, memory, CPU (paid plans) |
| **Activity** | Release history, who deployed what |
| **Access** | Team members and permissions |
| **Settings** | Config vars, domains, SSL, maintenance mode |

### Key Dashboard Actions

#### View/Edit Config Vars
1. Click on your app
2. Go to **Settings** tab
3. Click **Reveal Config Vars**
4. Add/Edit/Delete variables

#### Scale Dynos
1. Click on your app
2. Go to **Resources** tab
3. Click the **pencil icon** next to the dyno
4. Adjust slider or enable autoscaling
5. Click **Confirm**

#### View Logs
1. Click on your app
2. Click **More** (top right) → **View logs**
3. Or go to **Activity** tab for release logs

#### Check Metrics (Paid plans)
1. Click on your app
2. Go to **Metrics** tab
3. View:
   - Response time (p50, p95, p99)
   - Throughput (requests/minute)
   - Memory usage
   - Dyno load

#### Manage Domains
1. Click on your app
2. Go to **Settings** tab
3. Scroll to **Domains** section
4. Click **Add domain**

#### Enable Maintenance Mode
1. Click on your app
2. Go to **Settings** tab
3. Scroll to **Maintenance Mode**
4. Toggle ON (shows maintenance page to users)

---

## Viewing Logs

### CLI Commands

```bash
# Stream logs in real-time (Ctrl+C to stop)
heroku logs --tail -a ssq-api-staging

# View last 100 lines
heroku logs -n 100 -a ssq-api-staging

# Filter by source
heroku logs --source app -a ssq-api-staging      # Application logs only
heroku logs --source heroku -a ssq-api-staging   # Heroku system logs only

# Filter by dyno
heroku logs --dyno web.1 -a ssq-api-staging

# Combine filters
heroku logs --tail --source app --dyno web -a ssq-api-production
```

### Log Drains (For Production)

Send logs to external services for better analysis:

```bash
# Papertrail
heroku drains:add syslog+tls://logs.papertrailapp.com:12345 -a ssq-api-production

# Datadog
heroku drains:add "https://http-intake.logs.datadoghq.com/v1/input/<API_KEY>?ddsource=heroku&service=ssq-api" -a ssq-api-production

# List drains
heroku drains -a ssq-api-production

# Remove drain
heroku drains:remove <drain-url> -a ssq-api-production
```

---

## Database Management

The database is attached to both API and Worker apps. Use the API app for database management.

### Connect to Database

```bash
# Interactive psql session
heroku pg:psql -a ssq-api-staging

# Run a query directly
heroku pg:psql -a ssq-api-staging -c "SELECT COUNT(*) FROM users"
```

### View Database Info

```bash
# Database plan, size, connections
heroku pg:info -a ssq-api-staging

# Example output:
# === DATABASE_URL
# Plan:                  Essential-0
# Status:                Available
# Connections:           3/20
# PG Version:            15.4
# Data Size:             8.2 MB
# Tables:                12
# Rows:                  1523
```

### Get Database Credentials

```bash
# Full connection URL
heroku config:get DATABASE_URL -a ssq-api-staging

# Connection details
heroku pg:credentials:url -a ssq-api-staging
```

### Run Migrations

```bash
# Run SQL file
heroku pg:psql -a ssq-api-staging < data_adapter/sql-postgres/1.initial_setup.sql

# Or connect and run manually
heroku pg:psql -a ssq-api-staging
# Then paste SQL commands
```

### Database Backups

```bash
# Create manual backup
heroku pg:backups:capture -a ssq-api-production

# List backups
heroku pg:backups -a ssq-api-production

# Download latest backup
heroku pg:backups:download -a ssq-api-production

# Restore from backup
heroku pg:backups:restore b001 DATABASE_URL -a ssq-api-production
```

### Upgrade Database Plan

```bash
# View available plans
heroku addons:plans heroku-postgresql

# Upgrade (creates new DB and migrates data)
heroku addons:upgrade heroku-postgresql:essential-1 -a ssq-api-production
```

---

## Zero-Downtime Deployments (Optional)

Enable Preboot for zero-downtime deployments:

```bash
# Enable for API apps
heroku features:enable preboot -a ssq-api-staging
heroku features:enable preboot -a ssq-api-production

# Check status
heroku features -a ssq-api-production
```

**How Preboot works:**
1. New dynos start alongside old ones
2. Heroku waits for new dynos to pass health checks
3. Traffic shifts to new dynos
4. Old dynos are gracefully shut down

**Note:** Preboot doubles your dyno usage during deployments (brief period).

---

## Useful Commands

### App Management

```bash
# View all your apps
heroku apps

# View app info
heroku apps:info -a ssq-api-production

# Rename app
heroku apps:rename new-name -a old-name

# Delete app (careful!)
heroku apps:destroy -a ssq-api-staging --confirm ssq-api-staging
```

### Config Vars

```bash
# View all config vars
heroku config -a ssq-api-production

# Get single var
heroku config:get SSQ_SECRET_KEY -a ssq-api-production

# Set vars
heroku config:set KEY=value -a ssq-api-production

# Unset var
heroku config:unset KEY -a ssq-api-production
```

### Dyno Management

```bash
# View running dynos
heroku ps -a ssq-api-production

# Restart all dynos
heroku restart -a ssq-api-production

# Restart specific dyno
heroku restart web.1 -a ssq-api-production

# Run one-off dyno (for debugging)
heroku run bash -a ssq-api-production
```

### Releases

```bash
# View release history
heroku releases -a ssq-api-production

# Rollback to previous release
heroku rollback -a ssq-api-production

# Rollback to specific release
heroku rollback v42 -a ssq-api-production
```

---

## Troubleshooting

### App Crashes on Startup

```bash
# Check logs for errors
heroku logs --tail -a ssq-api-staging
```

**Common issues:**
- Missing config vars (`DATABASE_URL`, `AUTH0_*`, etc.)
- Database connection failures
- Port binding issues (ensure using `$PORT` from Heroku)
- Missing dependencies in requirements.txt

### Worker Not Processing Tasks

1. Verify worker is running:
   ```bash
   heroku ps -a ssq-worker-staging
   ```

2. Check worker logs:
   ```bash
   heroku logs --tail -a ssq-worker-staging
   ```

3. Verify DATABASE_URL is set:
   ```bash
   heroku config:get DATABASE_URL -a ssq-worker-staging
   ```

### Database Connection Issues

```bash
# Check database status
heroku pg:info -a ssq-api-staging

# Test connection
heroku pg:psql -a ssq-api-staging -c "SELECT 1"

# Check connection count (may be maxed out)
heroku pg:info -a ssq-api-staging | grep Connections
```

### Custom Domain Not Working

1. Verify DNS propagation:
   ```bash
   dig api.yourdomain.com CNAME
   ```

2. Check domain is added to Heroku:
   ```bash
   heroku domains -a ssq-api-production
   ```

3. Check SSL certificate:
   ```bash
   heroku certs:auto -a ssq-api-production
   ```

### Memory Issues (R14/R15 Errors)

```bash
# Check memory usage
heroku logs --tail -a ssq-api-production | grep "Memory"

# Upgrade dyno type
heroku ps:type web=standard-2x -a ssq-api-production
```

### Request Timeout (H12 Error)

- Requests must complete within 30 seconds
- Move long operations to Worker using TaskIQ
- Check for slow database queries

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Auto | Set automatically by Heroku Postgres addon |
| `APP_ENVIRONMENT` | Yes | `staging` or `production` |
| `DEBUG` | Yes | `False` for production |
| `SSQ_SECRET_KEY` | Yes | JWT signing key (use strong random string) |
| `SSQ_ALGORITHM` | Yes | JWT algorithm (default: `HS256`) |
| `SSQ_ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | Token expiry in minutes |
| `SSQ_BASE_URL` | Yes | This API's public URL |
| `SSQ_CLIENT_URL` | Yes | Frontend URL (for redirects) |
| `CORS_ORIGINS` | Yes | Comma-separated allowed origins |
| `AUTH0_DOMAIN` | Yes | Auth0 tenant domain |
| `AUTH0_AUDIENCE` | Yes | Auth0 API audience |
| `AUTH0_ISSUER` | Yes | Auth0 issuer URL |
| `INTERNAL_AUTH_API_KEY` | Yes | Internal service authentication key |
| `META_CLIENT_ID` | Yes | Facebook/Meta app ID |
| `META_CLIENT_SECRET` | Yes | Facebook/Meta app secret |
| `GOOGLE_CLIENT_ID` | Yes | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Yes | Google OAuth client secret |

---

## Cost Estimation

| Resource | Staging | Production |
|----------|---------|------------|
| API Dyno (basic) | ~$7/mo | - |
| API Dyno (standard-1x) | - | ~$25/mo |
| Worker Dyno (basic) | ~$7/mo | - |
| Worker Dyno (standard-1x) | - | ~$25/mo |
| Postgres (essential-0) | ~$5/mo | ~$5/mo |
| **Total (minimum)** | **~$19/mo** | **~$55/mo** |

**Note:** Prices are approximate. Check [Heroku Pricing](https://www.heroku.com/pricing) for current rates.
