# Healthcare Backend API - Quick Start Guide

Get the backend API running in 5 minutes.

## Prerequisites

- Python 3.10+
- MongoDB running locally or accessible remotely
- Terminal/Command prompt

## Step 1: Generate JWT Secret

Run this command and copy the output:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 2: Update .env File

Open `.env` and replace the JWT_SECRET value with the one you just generated:

```bash
# Before:
JWT_SECRET=your-secret-key-change-in-production-use-secure-random-string

# After (example):
JWT_SECRET=xK8j_9nF2mP5qR7tV4wY6zA1bC3dE8fG0hI2jK4lM6n
```

If your MongoDB is not at `localhost:27017`, also update `MONGO_URI`:

```bash
MONGO_URI=mongodb://your-mongo-host:port/healthcare?authSource=admin
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Verify Configuration

```bash
python verify_config.py
```

You should see "✓ Configuration is valid!"

## Step 5: Start the Server

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## Step 6: Test It

Open your browser and go to:

**http://localhost:8000/docs**

You should see the interactive API documentation (Swagger UI).

### Quick API Test

#### 1. Register a User

In the Swagger UI:
1. Expand `POST /auth/register`
2. Click "Try it out"
3. Use this JSON:
   ```json
   {
     "email": "patient@test.com",
     "password": "Test123!",
     "full_name": "Test Patient",
     "role": "patient"
   }
   ```
4. Click "Execute"
5. You should get a 201 response with the user details

#### 2. Login

1. Expand `POST /auth/login_json`
2. Click "Try it out"
3. Use this JSON:
   ```json
   {
     "email": "patient@test.com",
     "password": "Test123!"
   }
   ```
4. Click "Execute"
5. Copy the `access_token` from the response

#### 3. Authorize

1. Click the "Authorize" button at the top of the page
2. Paste your token (without "Bearer ")
3. Click "Authorize"
4. Click "Close"

#### 4. Test Authenticated Endpoint

1. Expand `GET /auth/me`
2. Click "Try it out"
3. Click "Execute"
4. You should see your user profile

## Alternative: Test with cURL

### Health Check
```bash
curl http://localhost:8000/
```

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"patient","full_name":"Test User"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login_json \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### Get Current User (replace TOKEN)
```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## URLs

- **API Base**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Common Issues

### Port Already in Use

Use a different port:
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

### MongoDB Connection Failed

Check:
1. Is MongoDB running? `mongosh` or `mongo`
2. Is MONGO_URI correct in `.env`?
3. Can you connect from terminal? `mongosh "mongodb://localhost:27017/healthcare"`

### Module Not Found

Install dependencies:
```bash
pip install -r requirements.txt
```

## What's Next?

- Review **README.md** for detailed documentation
- Check **docs/API_VERIFICATION.md** for curl command examples
- See **docs/FRONTEND_AUTH_NOTES.md** for frontend integration
- Read **CONFIGURATION_SUMMARY.md** for configuration details

## Need Help?

Run the configuration verification:
```bash
python verify_config.py
```

This will check your setup and show any issues.

---

**That's it!** Your backend API is now running and ready to use. 🚀
