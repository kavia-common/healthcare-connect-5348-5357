# Healthcare Connect Backend API

FastAPI backend service for the Healthcare Connect application.

## Overview

This is a RESTful API backend built with FastAPI that provides authentication, patient management, doctor management, consultation scheduling, and medical records management.

## Features

- **Authentication:** JWT-based authentication with role-based access control (RBAC)
- **User Management:** Support for patients, doctors, and admin roles
- **Patient Profiles:** Create and manage patient information
- **Doctor Profiles:** Create and manage doctor information
- **Consultations:** Schedule and manage doctor-patient consultations
- **Medical Records:** Store and retrieve patient medical records
- **OpenAPI Documentation:** Auto-generated API documentation (Swagger UI)

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI:** http://localhost:3001/docs
- **ReDoc:** http://localhost:3001/redoc
- **OpenAPI JSON:** http://localhost:3001/openapi.json

See also:
- `docs/API_VERIFICATION.md` - API endpoint verification and examples
- `docs/QUICKSTART.md` - Quick start guide with demo auth flow

## Tech Stack

- **Framework:** FastAPI 0.109.0
- **Database:** MongoDB with Motor (async driver)
- **Authentication:** JWT tokens with python-jose
- **Password Hashing:** bcrypt via passlib
- **Validation:** Pydantic v2
- **ASGI Server:** Uvicorn

## Prerequisites

- Python 3.12+
- MongoDB running on port 5001 (or configured port)
- pip or poetry for dependency management

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# MongoDB Configuration
MONGO_URI=mongodb://appuser:dbuser123@localhost:5001/myapp?authSource=admin
MONGO_DB=myapp

# JWT Configuration
JWT_SECRET=your-secret-key-change-in-production-use-secure-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=60
JWT_CLOCK_SKEW_SECONDS=30

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Backend Configuration
BACKEND_BASE_URL=http://localhost:3001
```

See `.env.example` for a template with all available options.

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGO_URI` | MongoDB connection string | Required |
| `MONGO_DB` | Database name | `myapp` |
| `JWT_SECRET` | Secret key for JWT signing | Required |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRES_MINUTES` | Token expiration time | `60` |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | `*` |

## Installation

### 1. Clone or navigate to the project

```bash
cd healthcare-connect-5348-5357/healthcare_backend_api
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Ensure MongoDB is running

Verify database connection:
```bash
mongosh mongodb://appuser:dbuser123@localhost:5001/myapp?authSource=admin
```

## Running the Application

### Development Mode

```bash
# From the project root directory
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

The API will be available at http://localhost:3001

### Production Mode

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --workers 4
```

### Using Docker

```bash
docker-compose up healthcare_backend_api
```

## Demo Credentials

Use these credentials to test the API:

### Admin Account
- **Email:** admin@healthcare.com
- **Password:** admin123
- **Role:** admin

### Doctor Accounts
1. **Dr. Sarah Johnson**
   - **Email:** doctor1@healthcare.com
   - **Password:** doctor123
   - **Specialty:** Cardiology

2. **Dr. Michael Chen**
   - **Email:** doctor2@healthcare.com
   - **Password:** doctor123
   - **Specialty:** Pediatrics

### Patient Accounts
1. **John Smith**
   - **Email:** patient1@healthcare.com
   - **Password:** patient123

2. **Emma Davis**
   - **Email:** patient2@healthcare.com
   - **Password:** patient123

## Demo Authentication Flow

### 1. Login and Get Token

```bash
curl -X POST "http://localhost:3001/auth/login_json" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient1@healthcare.com",
    "password": "patient123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Use Token for Authenticated Requests

```bash
curl -X GET "http://localhost:3001/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Access Protected Resources

```bash
# Get all doctors (requires authentication)
curl -X GET "http://localhost:3001/doctors" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Project Structure

```
healthcare_backend_api/
├── src/
│   └── api/
│       ├── main.py              # FastAPI app initialization
│       ├── db.py                # Database connection and utilities
│       ├── auth.py              # Authentication utilities
│       ├── models/              # Pydantic models
│       │   ├── user.py
│       │   ├── patient.py
│       │   ├── doctor.py
│       │   ├── consultation.py
│       │   └── medical_record.py
│       └── routers/             # API route handlers
│           ├── auth.py
│           ├── patients.py
│           ├── doctors.py
│           ├── consultations.py
│           └── medical_records.py
├── docs/
│   ├── API_VERIFICATION.md      # API testing guide
│   └── QUICKSTART.md            # Quick start guide
├── tests/                       # Test files
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## API Endpoints

### Authentication
- `POST /auth/login` - Login with form data (OAuth2 compatible)
- `POST /auth/login_json` - Login with JSON body
- `POST /auth/register` - Register new user
- `GET /auth/me` - Get current user info

### Patients
- `GET /patients` - List all patients (admin/doctor only)
- `POST /patients` - Create patient profile
- `GET /patients/{patient_id}` - Get patient by ID
- `PATCH /patients/{patient_id}` - Update patient
- `DELETE /patients/{patient_id}` - Delete patient (admin only)

### Doctors
- `GET /doctors` - List all doctors
- `POST /doctors` - Create doctor profile
- `GET /doctors/{doctor_id}` - Get doctor by ID
- `PATCH /doctors/{doctor_id}` - Update doctor
- `DELETE /doctors/{doctor_id}` - Delete doctor (admin only)

### Consultations
- `GET /consultations` - List consultations (filtered by role)
- `POST /consultations` - Create consultation
- `GET /consultations/{consultation_id}` - Get consultation by ID
- `PATCH /consultations/{consultation_id}` - Update consultation
- `DELETE /consultations/{consultation_id}` - Delete consultation (admin only)

### Medical Records
- `GET /medical_records` - List medical records (filtered by role)
- `POST /medical_records` - Create medical record (admin/doctor only)
- `GET /medical_records/{record_id}` - Get medical record by ID
- `PATCH /medical_records/{record_id}` - Update medical record
- `DELETE /medical_records/{record_id}` - Delete medical record (admin only)

## Role-Based Access Control

### Patient Role
- Can create and update their own patient profile
- Can view their own consultations and medical records
- Can view all doctors

### Doctor Role
- Can create and update their own doctor profile
- Can view and manage consultations where they are assigned
- Can view all patients
- Can create and manage medical records

### Admin Role
- Full access to all resources
- Can create/update/delete any user, patient, doctor, consultation, or medical record

## CORS Configuration

CORS is configured via the `CORS_ORIGINS` environment variable. The application automatically includes common development origins:

- http://localhost:3000
- http://localhost:3001
- http://127.0.0.1:3000
- http://127.0.0.1:5173
- https://appetize.io (for Flutter web preview)

To add more origins, update the `.env` file:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://your-domain.com
```

## Testing

### Run Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Manual API Testing

Use the Swagger UI at http://localhost:3001/docs for interactive testing.

Or use curl/Postman with the demo credentials above.

## Troubleshooting

### Common Issues

#### 1. 401 Unauthorized - Missing or Invalid Token

**Symptoms:**
- API returns 401 status
- Error: "Could not validate credentials"

**Solutions:**
- Ensure you're including the `Authorization: Bearer <token>` header
- Check that the token hasn't expired (default: 60 minutes)
- Verify JWT_SECRET matches between token generation and validation
- Login again to get a fresh token

**Example:**
```bash
# Correct way to include token
curl -H "Authorization: Bearer eyJhbGci..." http://localhost:3001/auth/me
```

#### 2. CORS Errors (Browser)

**Symptoms:**
- Browser console shows CORS policy error
- "Access-Control-Allow-Origin" header missing

**Solutions:**
- Add your frontend URL to `CORS_ORIGINS` in `.env`
- Restart the backend after changing CORS settings
- For Flutter emulator, use http://10.0.2.2:3001 instead of localhost

**Example:**
```bash
# In .env
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://10.0.2.2:3001
```

#### 3. Cannot Connect to MongoDB

**Symptoms:**
- Connection timeout
- "ServerSelectionTimeoutError"

**Solutions:**
- Verify MongoDB is running: `docker ps | grep mongodb`
- Check connection string in `.env`
- Ensure port 5001 is not blocked by firewall
- Test connection: `mongosh mongodb://appuser:dbuser123@localhost:5001/myapp?authSource=admin`

#### 4. Import Errors or Module Not Found

**Symptoms:**
- "ModuleNotFoundError: No module named 'fastapi'"
- Import errors when starting server

**Solutions:**
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
- Verify Python version: `python --version` (should be 3.12+)

#### 5. Port Already in Use

**Symptoms:**
- "Address already in use" error
- Cannot bind to port 3001

**Solutions:**
- Find process using port: `lsof -i :3001` (Unix) or `netstat -ano | findstr :3001` (Windows)
- Kill the process or use a different port: `uvicorn src.api.main:app --port 3002`

#### 6. Environment Variables Not Loading

**Symptoms:**
- Default values used instead of .env values
- "Required environment variable not set"

**Solutions:**
- Ensure `.env` file exists in project root
- Check file permissions: `chmod 644 .env`
- Verify no syntax errors in `.env` (no quotes, spaces around =)
- Restart the application after editing `.env`

### Network Configuration for Flutter Emulators

When testing with mobile emulators, use the appropriate network address:

**Android Emulator:**
- Use `http://10.0.2.2:3001` instead of `localhost:3001`
- The Android emulator maps 10.0.2.2 to the host's localhost

**iOS Simulator:**
- Use `http://localhost:3001` (works directly)

**Flutter Web:**
- Use `http://localhost:3001` (same network)

Update Flutter `.env`:
```bash
# For Android emulator
BACKEND_BASE_URL=http://10.0.2.2:3001

# For iOS simulator or web
BACKEND_BASE_URL=http://localhost:3001
```

### Debugging Tips

1. **Enable Debug Logging:**
   ```bash
   LOG_LEVEL=DEBUG uvicorn src.api.main:app --reload
   ```

2. **Check Database Connections:**
   ```bash
   mongosh mongodb://appuser:dbuser123@localhost:5001/myapp?authSource=admin --eval "db.serverStatus()"
   ```

3. **Verify Token Contents:**
   Decode JWT at https://jwt.io to inspect claims

4. **Test Endpoints:**
   Use Swagger UI at http://localhost:3001/docs for interactive testing

## Performance Optimization

### Database Indexes

Indexes are automatically created on startup for:
- User email (unique)
- Patient user_id
- Doctor user_id
- Consultation patient_id, doctor_id, scheduled_at
- Medical record patient_id

### Caching Strategies

For production, consider:
- Redis for session/token caching
- Database query result caching
- CDN for static assets

### Scaling

For high-traffic scenarios:
- Run multiple uvicorn workers: `--workers 4`
- Use a reverse proxy (nginx)
- Implement database connection pooling
- Consider MongoDB replica sets for read scaling

## Security Best Practices

### For Production

1. **Secure JWT Secret:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use HTTPS:** Deploy behind SSL/TLS reverse proxy

3. **Limit CORS Origins:** Don't use `*` in production

4. **Rate Limiting:** Implement rate limiting middleware

5. **Input Validation:** All inputs validated via Pydantic models

6. **Password Policy:** Enforce strong passwords (implement in registration)

7. **Logging:** Monitor authentication failures and suspicious activity

8. **Environment Variables:** Never commit `.env` to version control

## Contributing

1. Follow PEP 8 style guide
2. Add docstrings to all public functions
3. Include unit tests for new features
4. Update API documentation when adding endpoints
5. Run tests before committing: `pytest`

## License

[Your License Here]

## Support

For issues or questions:
- Check the troubleshooting section above
- Review API documentation at http://localhost:3001/docs
- Consult `docs/API_VERIFICATION.md` for testing examples
