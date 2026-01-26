from typing import Dict, Optional

import httpx
import jwt

from config import env
from logger.logging import LoggerUtil
from utils.exceptions import CustomBadRequest, CustomUnauthorized


class Auth0ManagementService:
    """Service for Auth0 Management API operations (resend verification, user management)"""

    def __init__(self):
        self.domain = env.AUTH0_DOMAIN
        self.mgmt_client_id = env.AUTH0_MGMT_CLIENT_ID
        self.mgmt_client_secret = env.AUTH0_MGMT_CLIENT_SECRET
        self.spa_client_id = env.AUTH0_SPA_CLIENT_ID
        self._mgmt_token = None
        self._mgmt_token_expires_at = 0

    async def _get_management_token(self) -> str:
        """Get a Management API access token using client credentials"""
        import time

        # Check if we have a valid cached token
        if self._mgmt_token and time.time() < self._mgmt_token_expires_at - 60:
            return self._mgmt_token

        if not self.mgmt_client_id or not self.mgmt_client_secret:
            LoggerUtil.create_error_log("Auth0 Management API credentials not configured")
            raise CustomBadRequest(detail="Email verification service not configured")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://{self.domain}/oauth/token",
                    json={
                        "client_id": self.mgmt_client_id,
                        "client_secret": self.mgmt_client_secret,
                        "audience": f"https://{self.domain}/api/v2/",
                        "grant_type": "client_credentials",
                    },
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                self._mgmt_token = data["access_token"]
                self._mgmt_token_expires_at = time.time() + data.get("expires_in", 86400)

                LoggerUtil.create_info_log("Auth0 Management API token obtained successfully")
                return self._mgmt_token

        except httpx.RequestError as e:
            LoggerUtil.create_error_log(f"Failed to get Auth0 Management token: {e}")
            raise CustomBadRequest(detail="Failed to connect to authentication service")
        except httpx.HTTPStatusError as e:
            LoggerUtil.create_error_log(f"Auth0 Management token request failed: {e.response.text}")
            raise CustomBadRequest(detail="Authentication service configuration error")

    async def send_verification_email(self, auth0_user_id: str) -> Dict:
        """
        Send verification email to a user via Auth0 Management API.

        Args:
            auth0_user_id: The Auth0 user ID (e.g., "auth0|123456")

        Returns:
            Dict with 'success' boolean and 'message' string
        """
        token = await self._get_management_token()

        try:
            async with httpx.AsyncClient() as client:
                payload = {"user_id": auth0_user_id}

                # Add client_id if configured (for redirect after verification)
                if self.spa_client_id:
                    payload["client_id"] = self.spa_client_id

                response = await client.post(
                    f"https://{self.domain}/api/v2/jobs/verification-email",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10,
                )
                response.raise_for_status()

                LoggerUtil.create_info_log(f"Verification email sent successfully for user: {auth0_user_id}")
                return {
                    "success": True,
                    "message": "Verification email sent successfully.",
                }

        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.content else {}
            LoggerUtil.create_error_log(f"Failed to send verification email: {error_detail}")

            if e.response.status_code == 429:
                return {
                    "success": False,
                    "message": "Too many requests. Please wait a few minutes before trying again.",
                }

            return {
                "success": False,
                "message": "Failed to send verification email. Please try again later.",
            }
        except httpx.RequestError as e:
            LoggerUtil.create_error_log(f"Request error sending verification email: {e}")
            return {
                "success": False,
                "message": "Service temporarily unavailable. Please try again later.",
            }


class Auth0Service:
    """Service for validating Auth0 JWT tokens"""

    def __init__(self):
        self.domain = env.AUTH0_DOMAIN
        self.audience = env.AUTH0_AUDIENCE
        self.issuer = env.AUTH0_ISSUER
        self._jwks = None
        self._jwks_url = f"https://{self.domain}/.well-known/jwks.json"

    async def _get_jwks(self) -> Dict:
        """Fetch JSON Web Key Set from Auth0"""
        if self._jwks is None:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(self._jwks_url, timeout=10)
                    response.raise_for_status()
                    self._jwks = response.json()
            except httpx.RequestError as e:
                LoggerUtil.create_error_log(f"Failed to fetch JWKS from Auth0: {e}")
                raise CustomUnauthorized(detail="Authentication service unavailable")
        return self._jwks

    async def _get_signing_key(self, token: str) -> Optional[str]:
        """Get the signing key for the token"""
        try:
            # Decode the header without verification to get the key ID
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get("kid")

            if not key_id:
                return None

            jwks = await self._get_jwks()

            # Find the key with matching key ID
            for key in jwks.get("keys", []):
                if key.get("kid") == key_id:
                    # Convert JWK to PEM format
                    if key.get("kty") == "RSA":
                        from cryptography.hazmat.backends import default_backend
                        from cryptography.hazmat.primitives import serialization
                        from cryptography.hazmat.primitives.asymmetric import rsa

                        # Extract RSA components
                        n = int.from_bytes(jwt.utils.base64url_decode(key["n"]), "big")
                        e = int.from_bytes(jwt.utils.base64url_decode(key["e"]), "big")

                        # Create RSA public key
                        public_key = rsa.RSAPublicNumbers(e, n).public_key(backend=default_backend())

                        # Export as PEM
                        pem = public_key.public_bytes(
                            encoding=serialization.Encoding.PEM,
                            format=serialization.PublicFormat.SubjectPublicKeyInfo,
                        )
                        return pem.decode("utf-8")

            return None
        except Exception as e:
            LoggerUtil.create_error_log(f"Error getting signing key: {e}")
            return None

    async def validate_token(self, token: str) -> Dict:
        """Validate Auth0 JWT token and return payload"""
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith("Bearer "):
                token = token[7:]

            # Get the signing key
            signing_key = await self._get_signing_key(token)
            if not signing_key:
                raise CustomUnauthorized(detail="Invalid token signature")

            # Decode and verify the token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iss": True,
                    "verify_exp": True,
                    "verify_iat": True,
                },
            )

            LoggerUtil.create_info_log(f"Token validated successfully for user: {payload.get('sub', 'unknown')}")
            return payload

        except CustomUnauthorized:
            # Re-raise CustomUnauthorized exceptions (e.g., from _get_signing_key)
            raise
        except jwt.ExpiredSignatureError:
            LoggerUtil.create_error_log("Token has expired")
            raise CustomUnauthorized(detail="Token has expired")
        except jwt.InvalidAudienceError:
            LoggerUtil.create_error_log("Invalid audience in token")
            raise CustomUnauthorized(detail="Invalid token audience")
        except jwt.InvalidIssuerError:
            LoggerUtil.create_error_log("Invalid issuer in token")
            raise CustomUnauthorized(detail="Invalid token issuer")
        except jwt.InvalidSignatureError:
            LoggerUtil.create_error_log("Invalid token signature")
            raise CustomUnauthorized(detail="Invalid token signature")
        except jwt.InvalidTokenError as e:
            LoggerUtil.create_error_log(f"Invalid token: {e}")
            raise CustomUnauthorized(detail="Invalid token")
        except Exception as e:
            LoggerUtil.create_error_log(f"Token validation error: {e}")
            raise CustomUnauthorized(detail="Token validation failed")
