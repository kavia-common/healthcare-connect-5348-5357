from datetime import timedelta
import pytest
from starlette.requests import Request

from src.api.auth import create_access_token, decode_access_token
from src.api.dependencies import get_current_user, get_current_user_strict
from jose import ExpiredSignatureError


def make_request_with_headers(headers: dict) -> Request:
    """
    Build a minimal Starlette Request for dependency testing.
    """
    # Convert headers to lowercase bytes as expected by ASGI scope
    scope_headers = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "path": "/",
        "headers": scope_headers,
    }
    return Request(scope)


def test_create_and_decode_token_includes_exp_and_iat(monkeypatch):
    # Ensure deterministic env
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("JWT_CLOCK_SKEW_SECONDS", "0")

    token = create_access_token({"sub": "user123", "role": "admin"}, expires_delta=timedelta(minutes=5))
    claims = decode_access_token(token)
    assert claims["sub"] == "user123"
    assert claims["role"] == "admin"
    assert "exp" in claims
    assert "iat" in claims


def test_decode_token_with_leeway_allows_small_skew(monkeypatch):
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("JWT_CLOCK_SKEW_SECONDS", "60")

    # Create a token that is already "expired" by a few seconds, but within leeway
    token = create_access_token({"sub": "user123"}, expires_delta=timedelta(seconds=-5))
    # With 60s leeway, this should still decode
    claims = decode_access_token(token)
    assert claims["sub"] == "user123"


def test_expired_token_raises(monkeypatch):
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("JWT_CLOCK_SKEW_SECONDS", "0")

    token = create_access_token({"sub": "user123"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(ExpiredSignatureError):
        # Direct decoder raises ExpiredSignatureError
        decode_access_token(token)


def test_get_current_user_header_and_query_fallback(monkeypatch):
    # Validate non-strict variant accepts Authorization and query fallback
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "test-secret")
    monkeypatch.setenv("JWT_CLOCK_SKEW_SECONDS", "0")

    token = create_access_token({"sub": "abc", "role": "patient"}, expires_delta=timedelta(minutes=1))

    # Authorization header
    req = make_request_with_headers({"authorization": f"Bearer {token}"})
    user = get_current_user(req, token=None)  # type: ignore
    assert user["sub"] == "abc"

    # Query fallback (only in non-strict)
    req2 = make_request_with_headers({})
    # Starlette Request stores query params in the scope when built by ASGI server; for unit test,
    # we can inject by modifying the underlying _query_params property after creation.
    req2._query_params = {"token": token}  # type: ignore[attr-defined]
    user2 = get_current_user(req2, token=None)  # type: ignore
    assert user2["sub"] == "abc"


def test_get_current_user_strict_rejects_query_token(monkeypatch):
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    token = create_access_token({"sub": "abc"}, expires_delta=timedelta(minutes=1))
    req = make_request_with_headers({})
    req._query_params = {"token": token}  # type: ignore[attr-defined]

    with pytest.raises(Exception) as excinfo:
        get_current_user_strict(req, token=None)  # type: ignore
    # Ensure 401 is raised
    assert "401" in str(excinfo.value)


def test_get_current_user_strict_accepts_x_auth_token(monkeypatch):
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_SECRET", "test-secret")

    token = create_access_token({"sub": "xyz"}, expires_delta=timedelta(minutes=1))
    req = make_request_with_headers({"x-auth-token": token})
    user = get_current_user_strict(req, token=None)  # type: ignore
    assert user["sub"] == "xyz"
