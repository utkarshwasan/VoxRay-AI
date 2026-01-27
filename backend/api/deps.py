import jwt
from jwt import PyJWKClient
from fastapi import Request, HTTPException, Depends
import os
from dotenv import load_dotenv
from pathlib import Path

# Load env from backend/.env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Stack Auth Project ID from env
STACK_PROJECT_ID = os.getenv("STACK_PROJECT_ID")

# Construct JWKS URL (Public Keys)
if STACK_PROJECT_ID:
    JWKS_URL = f"https://api.stack-auth.com/api/v1/projects/{STACK_PROJECT_ID}/.well-known/jwks.json"
else:
    # Fallback or warning - for now we proceed but get_current_user will fail if not set
    JWKS_URL = ""
    print("WARNING: STACK_PROJECT_ID not set. Auth will fail.")

# Cache the public keys
jwks_client = PyJWKClient(JWKS_URL) if JWKS_URL else None

def get_current_user(request: Request):
    """
    Validates the 'x-stack-access-token' header against Stack Auth's JWKS.
    Returns the decoded token payload if valid.
    """
    # 1. Get token from header (using x-stack-access-token as consistent convention)
    token = request.headers.get("x-stack-access-token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    if not jwks_client:
        raise HTTPException(status_code=500, detail="Server auth configuration error (Missing Project ID)")

    try:
        # 2. Get the Signing Key
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        # 3. Decode & Verify (ES256/RS256)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience=STACK_PROJECT_ID,
            # Add leeway to handle clock skew between client and server
            leeway=60,  # Allow 60 seconds tolerance
            options={"verify_aud": True} 
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        # Catch-all for other crypto/network errors
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def require_role(role: str):
    """
    Placeholder for Role-Based Access Control (RBAC).
    Usage: @app.post("/admin", dependencies=[Depends(require_role("admin"))])
    """
    def role_checker(user: dict = Depends(get_current_user)):
        # In the future, check user.get('roles') or similar from Stack Auth metadata
        # if role not in user.get('roles', []):
        #     raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
