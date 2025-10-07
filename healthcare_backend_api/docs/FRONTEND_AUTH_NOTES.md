Frontend JWT usage notes

- Login:
  - Use POST /auth/login_json with JSON body: {"email": "...", "password": "..."}.
  - Store response.access_token securely (Flutter: consider flutter_secure_storage for mobile).
  - token_type is "bearer"; always send as an HTTP header:
    Authorization: Bearer <access_token>

- Per-request auth:
  - Attach Authorization: Bearer <token> to every API request.
  - X-Auth-Token header is supported as a fallback if an environment prevents setting Authorization.
  - Query parameter tokens (?token=...) are NOT accepted on sensitive routes and should be avoided.

- Token lifecycle:
  - Access tokens include exp (expiry) and iat (issued at).
  - The backend allows small clock skew (JWT_CLOCK_SKEW_SECONDS) to tolerate device time drift.
  - On 401 with detail "Token expired", clear the stored token and route to the login screen.
  - No refresh token flow is implemented; re-login when expired.

- CORS:
  - Ensure your mobile/dev environment origin appears in the backend CORS_ORIGINS (see .env.example).

- Logout:
  - Remove the stored token and ensure subsequent requests omit the Authorization header.
