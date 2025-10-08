"""
Configuration verification script.
Run this to verify that environment variables are loaded correctly from .env

Usage:
    python verify_config.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load .env
load_dotenv()

def verify_config():
    """Verify all required environment variables are set."""
    
    print("=" * 60)
    print("Healthcare Backend API - Configuration Verification")
    print("=" * 60)
    print()
    
    required_vars = {
        "MONGO_URI": "MongoDB connection URI",
        "MONGO_DB": "MongoDB database name",
        "JWT_SECRET": "JWT signing secret",
        "JWT_ALGORITHM": "JWT algorithm (should be HS256)",
        "ACCESS_TOKEN_EXPIRES_MINUTES": "Access token expiration in minutes",
        "CORS_ORIGINS": "Allowed CORS origins",
    }
    
    optional_vars = {
        "JWT_CLOCK_SKEW_SECONDS": "JWT clock skew tolerance (default: 30)",
        "BACKEND_BASE_URL": "Backend base URL",
    }
    
    all_valid = True
    
    print("Required Configuration:")
    print("-" * 60)
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "SECRET" in var or "PASSWORD" in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            
            status = "✓"
            
            # Check for default/placeholder values that need to be changed
            if var == "JWT_SECRET" and ("change" in value.lower() or "your-secret" in value.lower()):
                status = "⚠"
                all_valid = False
                print(f"  {status} {var}: {display_value}")
                print("      WARNING: Using placeholder secret! Generate a secure one:")
                print("      python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
            else:
                print(f"  {status} {var}: {display_value}")
            
            print(f"      ({description})")
        else:
            status = "✗"
            all_valid = False
            print(f"  {status} {var}: NOT SET")
            print(f"      ({description})")
        print()
    
    print("\nOptional Configuration:")
    print("-" * 60)
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: {value}")
        else:
            print(f"  - {var}: Using default")
        print(f"      ({description})")
        print()
    
    print("=" * 60)
    
    # Test imports
    print("\nTesting Module Imports:")
    print("-" * 60)
    try:
        from src.api import auth, db, main
        print("  ✓ All modules imported successfully")
        
        # Check loaded values
        print("\n  Loaded Configuration Values:")
        print(f"    - JWT_ALGORITHM: {auth.JWT_ALGORITHM}")
        print(f"    - ACCESS_TOKEN_EXPIRES_MINUTES: {auth.ACCESS_TOKEN_EXPIRES_MINUTES}")
        print(f"    - JWT_CLOCK_SKEW_SECONDS: {auth.JWT_CLOCK_SKEW_SECONDS}")
        print(f"    - MONGO_DB: {db.MONGO_DB}")
        print(f"    - CORS_ORIGINS: {main.CORS_ORIGINS}")
        
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        all_valid = False
    
    print()
    print("=" * 60)
    
    if all_valid:
        print("\n✓ Configuration is valid!")
        print("\nNext steps:")
        print("  1. Ensure MongoDB is running")
        print("  2. Start the API server:")
        print("     uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
        print("  3. Access docs at: http://localhost:8000/docs")
        print("  4. See docs/API_VERIFICATION.md for curl test commands")
        return 0
    else:
        print("\n✗ Configuration has issues - please review warnings above")
        print("\nIMPORTANT: Update JWT_SECRET with a secure random value:")
        print("  python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
        return 1

if __name__ == "__main__":
    sys.exit(verify_config())
