# Auth0 Token Validation Setup

This application validates Auth0 JWT tokens for API endpoints. **No user management in backend** - Auth0 handles all signup/login, backend only validates tokens.

## What This Does

- ✅ **Frontend**: Auth0 handles signup, login, password reset, etc.
- ✅ **Backend**: Only validates tokens from frontend
- ✅ **No user storage**: All user data comes from validated tokens
- ✅ **Stateless**: No sessions or user management in backend

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Add to your `.env` file:

```env
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_AUDIENCE=your-api-identifier
AUTH0_ISSUER=https://your-tenant.auth0.com/
```

### 3. Auth0 Dashboard Setup

#### Step 1: Create an API
1. Go to Auth0 Dashboard → **APIs**
2. Click **"Create API"**
3. Set **Name**: Your API name
4. Set **Identifier**: `https://your-api.com` (this becomes your `AUTH0_AUDIENCE`)
5. Choose **RS256** signing algorithm
6. Click **"Create"**

#### Step 2: Create an Application
1. Go to Auth0 Dashboard → **Applications**
2. Click **"Create Application"**
3. Choose **Single Page Application** (for React/Vue/Angular) or **Regular Web Application** (for server-side rendering)
4. Set **Name**: Your app name
5. Set **Allowed Callback URLs**: `http://localhost:3000/callback` (adjust for your frontend)
6. Set **Allowed Logout URLs**: `http://localhost:3000` (adjust for your frontend)
7. Click **"Create"**

#### Step 3: Configure Application Settings
1. In your application settings, go to **"Settings"** tab
2. Copy the **Domain** (this becomes your `AUTH0_DOMAIN`)
3. Copy the **Client ID** (frontend will use this)
4. **Don't copy the Client Secret** (not needed for this setup)

## Usage

### Protecting Endpoints

```python
from decorators.user import require_authentication
from fastapi import Request

@router.get("/protected-endpoint")
@require_authentication
async def protected_endpoint(request: Request):
    # Access user info from token
    user_info = request.state.user
    
    return {
        "user_id": user_info.get("sub"),
        "email": user_info.get("email")
    }
```

### Accessing User Information

```python
user_info = request.state.user

# Common fields from Auth0 token
user_id = user_info.get("sub")           # Auth0 user ID
email = user_info.get("email")           # User's email
name = user_info.get("name")             # User's name
email_verified = user_info.get("email_verified")  # Email verification status
```

### Frontend Integration

```javascript
// Frontend gets token from Auth0 and sends to backend
const response = await fetch('/api/v1/auth/me', {
    headers: {
        'Authorization': `Bearer ${auth0Token}`,
        'Content-Type': 'application/json'
    }
});
```

## Example Endpoints

- `GET /api/v1/auth/me` - Get authenticated user profile
- `GET /api/v1/auth/protected` - Example protected endpoint

## The Flow

```
Frontend → Auth0 Login → Gets Token → Sends to Backend → Backend validates token
```

**What Auth0 handles:**
- User registration/signup
- Login forms
- Password reset
- Email verification
- Social login
- User profile management

**What your backend does:**
- Receives tokens from frontend
- Validates tokens are legitimate
- Extracts user info from token
- Protects your API endpoints

## Environment Variables Summary

| Variable | Description | Example |
|----------|-------------|---------|
| `AUTH0_DOMAIN` | Your Auth0 tenant domain | `myapp.auth0.com` |
| `AUTH0_AUDIENCE` | API identifier from Auth0 | `https://my-api.com` |
| `AUTH0_ISSUER` | Issuer URL | `https://myapp.auth0.com/` |

## Troubleshooting

1. **"Authentication service unavailable"**: Check internet connection and `AUTH0_DOMAIN`
2. **"Invalid token audience"**: Verify `AUTH0_AUDIENCE` matches API identifier in Auth0
3. **"Token has expired"**: Frontend should refresh tokens before expiration
4. **"Invalid token signature"**: Check `AUTH0_DOMAIN` configuration

## Security Notes

- **No backend storage**: User data comes from validated tokens only
- **Stateless**: Each request validates token independently
- **Public key verification**: Uses Auth0's JWKS for secure validation
- **Automatic key rotation**: Fetches latest keys from Auth0 