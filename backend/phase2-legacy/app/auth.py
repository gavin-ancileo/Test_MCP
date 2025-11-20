# auth.py
# Minimal Cognito JWT verifier. Swap this provider in Phase-3 with AgentCore easily.
import os
from typing import List, Dict, Any, Optional
from jose import jwt
import requests

COGNITO_JWKS_URL = os.getenv("COGNITO_JWKS_URL", "")

class UserContext:
    """Normalized caller context."""
    def __init__(self, sub: str, email: str, roles: List[str], claims: Dict[str, Any]):
        self.sub = sub
        self.email = email
        self.roles = roles
        self.claims = claims

class AuthError(Exception): ...

class AuthProvider:
    """Interface for swappable auth providers."""
    def verify(self, token: str) -> UserContext:  # pragma: no cover
        raise NotImplementedError

class CognitoAuthProvider(AuthProvider):
    def __init__(self, jwks_url: str):
        self.jwks_url = jwks_url
        self._jwks = None

    def _get_jwks(self):
        if self._jwks is None:
            resp = requests.get(self.jwks_url, timeout=10)
            resp.raise_for_status()
            self._jwks = resp.json()
        return self._jwks

    def verify(self, token: str) -> UserContext:
        if not token:
            raise AuthError("Missing bearer token")
        jwks = self._get_jwks()
        unverified = jwt.get_unverified_header(token)
        kid = unverified.get("kid")
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise AuthError("JWKS key not found")
        claims = jwt.decode(token, key, options={"verify_aud": False})
        # Normalize fields
        sub = claims.get("sub", "")
        email = claims.get("email") or claims.get("username") or ""
        roles = claims.get("cognito:groups") or []
        return UserContext(sub=sub, email=email, roles=roles, claims=claims)

def current_auth_provider() -> AuthProvider:
    if not COGNITO_JWKS_URL:
        # Dev mode: allow unauthenticated but tag as 'dev'
        return DevAuthProvider()
    return CognitoAuthProvider(COGNITO_JWKS_URL)

class DevAuthProvider(AuthProvider):
    """Dev-only: DO NOT USE in production."""
    def verify(self, token: str) -> UserContext:
        return UserContext(sub="dev", email="dev@example.com", roles=["admin","hr"], claims={"dev":True})
