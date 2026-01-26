# Auth0 Setup Guide for SocialSquad

This guide covers the complete Auth0 integration including user registration, email verification, and webhook setup.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              AUTH0 FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   User Signs Up ──► Auth0 ──► Post User Registration Action ──► Backend API │
│        │                              │                              │       │
│        │                              │                     POST /v1/users/  │
│        │                              │                    (creates user)    │
│        │                              ▼                              │       │
│        │                    Sends verification email                 │       │
│        │                              │                              │       │
│        ▼                              ▼                              │       │
│   User Verifies Email ──► User Logs In ──► Post Login Action ──► Backend API│
│                                              │                       │       │
│                                              │              POST /v1/users/  │
│                                              │               verify-email    │
│                                              │           (marks verified)    │
│                                              ▼                       │       │
│                                    User gets JWT token               │       │
│                                              │                       │       │
│                                              ▼                       │       │
│                                    Frontend calls Backend APIs       │       │
│                                    with Bearer token                 │       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Environment Variables

Add these to your `.env` file:

```env
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=your-api-identifier
AUTH0_ISSUER=https://your-tenant.auth0.com/

# Auth0 Management API (for resending verification emails)
AUTH0_MGMT_CLIENT_ID=your-management-client-id
AUTH0_MGMT_CLIENT_SECRET=your-management-client-secret

# Internal API Key (for Auth0 Actions to call your backend)
INTERNAL_AUTH_API_KEY=your-secure-random-key
```

## Auth0 Dashboard Setup

### Step 1: Create an API

1. Go to Auth0 Dashboard → **APIs**
2. Click **"Create API"**
3. Configure:
   - **Name**: `SocialSquad API`
   - **Identifier**: `https://api.socialsquad.ai` (this becomes `AUTH0_AUDIENCE`)
   - **Signing Algorithm**: RS256
4. Click **"Create"**

### Step 2: Create a Single Page Application

1. Go to Auth0 Dashboard → **Applications** → **Create Application**
2. Choose **Single Page Application**
3. Configure in **Settings** tab:
   - **Name**: `SocialSquad Frontend`
   - **Allowed Callback URLs**:
     ```
     http://localhost:3000,
     https://app.socialsquad.ai
     ```
   - **Allowed Logout URLs**:
     ```
     http://localhost:3000,
     https://app.socialsquad.ai
     ```
   - **Allowed Web Origins**:
     ```
     http://localhost:3000,
     https://app.socialsquad.ai
     ```
4. Save the **Domain** and **Client ID** for frontend configuration

### Step 3: Create a Machine-to-Machine Application (for Management API)

1. Go to **Applications** → **Create Application**
2. Choose **Machine to Machine Applications**
3. Name it: `SocialSquad Backend`
4. Select the **Auth0 Management API**
5. Grant these permissions:
   - `read:users`
   - `update:users`
   - `create:user_tickets` (for resending verification emails)
6. Save the **Client ID** and **Client Secret** as `AUTH0_MGMT_CLIENT_ID` and `AUTH0_MGMT_CLIENT_SECRET`

### Step 4: Enable Email Verification Requirement

1. Go to **Authentication** → **Database** → **Username-Password-Authentication**
2. Enable **"Requires Username"** (optional)
3. Go to **Security** → **Attack Protection** → **Bot Detection** (recommended)

### Step 5: Create Auth0 Action - Post User Registration

This action calls your backend to create a user when someone signs up.

1. Go to **Actions** → **Library** → **Build Custom**
2. Name: `Post Registration - Create User in Backend`
3. Trigger: **Post User Registration**
4. Add **Secret**:
   - Key: `backend_api_token`
   - Value: Your `INTERNAL_AUTH_API_KEY` value
5. Add **Dependency**:
   - Name: `axios`
   - Version: `1.6.0`
6. Code:

```javascript
/**
 * Handler that will be called during the execution of a PostUserRegistration flow.
 * Creates user in SocialSquad backend after Auth0 registration.
 */
exports.onExecutePostUserRegistration = async (event, api) => {
  const axios = require("axios");

  const user = event.user || {};
  const connection = String(event.connection || "");
  const identities = Array.isArray(user.identities) ? user.identities : [];

  const provider = identities.length > 0 ? identities[0].provider : "unknown";
  const signup_method = connection !== "Username-Password-Authentication"
    ? provider
    : "email-password";

  const userInfo = {
    email: user.email,
    auth0_user_id: user.user_id,
    name: user.name,
    signup_method: signup_method,
    email_verified: user.email_verified,
    auth0_created_at: user.created_at
  };

  try {
    await axios.post("https://api.socialsquad.ai/v1/users/", userInfo, {
      headers: {
        Authorization: `Bearer ${event.secrets.backend_api_token}`,
        "Content-Type": "application/json"
      }
    });
    console.log("User creation callback success for:", user.email);
  } catch (error) {
    console.error("Failed to create user in backend:", error.message);
  }
};
```

7. Click **Deploy**
8. Go to **Actions** → **Flows** → **Post User Registration**
9. Drag your action into the flow and **Apply**

### Step 6: Create Auth0 Action - Post Login (Email Verification Sync)

This action syncs the email verification status to your backend when a user logs in.

1. Go to **Actions** → **Library** → **Build Custom**
2. Name: `Post Login - Sync Email Verification`
3. Trigger: **Login / Post Login**
4. Add **Secret**:
   - Key: `backend_api_token`
   - Value: Your `INTERNAL_AUTH_API_KEY` value
5. Add **Dependency**:
   - Name: `axios`
   - Version: `1.6.0`
6. Code:

```javascript
/**
 * Handler that will be called during the execution of a PostLogin flow.
 * Syncs email verification status to backend (retries up to 3 times).
 */
exports.onExecutePostLogin = async (event, api) => {
  const axios = require("axios");

  // Only process if email is verified
  if (!event.user.email_verified) {
    return;
  }

  // Check notification count from app_metadata (retry up to 3 times)
  const notificationCount = event.user.app_metadata?.email_verification_notify_count || 0;

  if (notificationCount >= 3) {
    return;
  }

  try {
    await axios.post(
      "https://api.socialsquad.ai/v1/users/verify-email",
      {
        auth0_user_id: event.user.user_id
      },
      {
        headers: {
          Authorization: `Bearer ${event.secrets.backend_api_token}`,
          "Content-Type": "application/json"
        }
      }
    );

    // Increment count on success
    api.user.setAppMetadata("email_verification_notify_count", notificationCount + 1);
    console.log(`Email verification synced (attempt ${notificationCount + 1}/3) for:`, event.user.email);
  } catch (error) {
    console.error("Failed to sync email verification:", error.message);
    // Don't increment on failure - will retry next login
  }
};
```

7. Click **Deploy**
8. Go to **Actions** → **Flows** → **Login**
9. Drag your action into the flow and **Apply**

### Step 7: Create Auth0 Action - Block Unverified Email Logins (Optional but Recommended)

This action blocks login attempts from users who haven't verified their email.

1. Go to **Actions** → **Library** → **Build Custom**
2. Name: `Login - Require Email Verification`
3. Trigger: **Login / Post Login**
4. Code:

```javascript
/**
 * Blocks login if email is not verified (for email/password signups only).
 */
exports.onExecutePostLogin = async (event, api) => {
  // Skip for social logins (they're pre-verified)
  if (event.connection !== "Username-Password-Authentication") {
    return;
  }

  // Block if email not verified
  if (!event.user.email_verified) {
    api.access.deny("Please verify your email before logging in.");
  }
};
```

5. Click **Deploy**
6. Go to **Actions** → **Flows** → **Login**
7. Drag this action **BEFORE** the email verification sync action
8. **Apply**

## Backend API Endpoints

### Internal Endpoints (Auth0 Actions call these)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/users/` | POST | Internal API Key | Create user after registration |
| `/v1/users/verify-email` | POST | Internal API Key | Mark email as verified |

### Public Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/auth/resend-verification` | POST | None | Resend verification email |

### Authenticated Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/v1/users/profile` | GET | Auth0 JWT | Get current user profile |
| `/v1/users/{uuid}` | GET | Auth0 JWT | Get user by UUID |
| `/v1/users/` | GET | Auth0 JWT | List all users |

## User Status Flow

```
email-password signup:  verification_pending → (verify email) → onboarding → active
social signup (Google): onboarding → active
```

## Frontend Configuration

Create a `config.js` file:

```javascript
const AUTH0_CONFIG = {
    domain: 'your-tenant.auth0.com',
    clientId: 'your-spa-client-id',
    audience: 'https://api.socialsquad.ai',
    apiBaseUrl: 'https://api.socialsquad.ai'  // or http://localhost:8000 for local
};
```

## Testing Locally

### 1. Start Backend

```bash
docker compose up
```

### 2. Start Test Frontend

```bash
cd auth0-test-frontend
python server.py 3000
```

### 3. Test Flow

1. Open http://localhost:3000
2. Enter email and click "Continue with Email"
3. Sign up in Auth0
4. Check your email for verification link
5. Verify email
6. Log in again
7. You should see the dashboard

## Troubleshooting

### "Authentication service unavailable"
- Check `AUTH0_DOMAIN` is correct
- Verify internet connectivity

### "Invalid token audience"
- Ensure `AUTH0_AUDIENCE` matches the API identifier in Auth0

### User not created in backend
- Check Auth0 Action logs: **Monitoring** → **Logs**
- Verify `backend_api_token` secret is set correctly
- Check backend logs for errors

### Email verification not syncing
- Check Post Login action logs
- Verify the action is deployed and in the Login flow
- Check `email_verification_notify_count` in user's `app_metadata`

### Resend verification email not working
- Verify `AUTH0_MGMT_CLIENT_ID` and `AUTH0_MGMT_CLIENT_SECRET` are set
- Check the Machine-to-Machine app has correct permissions

## Security Notes

- **Internal API Key**: Keep `INTERNAL_AUTH_API_KEY` secret, only share with Auth0 Actions
- **Management API**: Only grant minimum required permissions
- **Token Validation**: All user endpoints validate Auth0 JWT tokens
- **Email Enumeration**: Resend verification endpoint returns generic responses to prevent enumeration
