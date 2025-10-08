# Healthcare Backend API

FastAPI-based backend REST API for the Healthcare Connect application.

## Features

- **Authentication & Authorization**: JWT-based auth with role-based access control (RBAC)
- **Patient Management**: CRUD operations for patient profiles
- **Doctor Management**: CRUD operations for doctor profiles
- **Consultations**: Schedule and manage doctor-patient consultations
- **Medical Records**: Secure medical records management
- **CORS Support**: Configured for cross-origin requests
- **OpenAPI Documentation**: Auto-generated interactive API docs

## Prerequisites

- Python 3.10+
- MongoDB instance running and accessible
- pip or poetry for dependency management

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

**CRITICAL**: Edit `.env` and update the following:

#### Required Configuration

- **JWT_SECRET**: Generate a secure random secret:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```
  Copy the output and set it as `JWT_SECRET` in your `.env` file.

- **MONGO_URI**: Update with your MongoDB connection string
  - Format: `mongodb://[username:password@]host:port/database?authSource=admin`
  - Example: `mongodb://localhost:27017/healthcare?authSource=admin`

- **MONGO_DB**: Set your database name (e.g., `healthcare`)

#### Optional Configuration

- **ACCESS_TOKEN_EXPIRES_MINUTES**: Token expiration time (default: 60)
- **JWT_CLOCK_SKEW_SECONDS**: Clock skew tolerance (default: 30)
- **CORS_ORIGINS**: Comma-separated list of allowed origins
  - Default includes localhost:3000, localhost:3001, and appetize.io

### 3. Verify Configuration

Run the configuration verification script:

```bash
python verify_config.py
```

This will check that all required environment variables are set and modules load correctly.

### 4. Start MongoDB

Ensure your MongoDB instance is running and accessible at the URI specified in `MONGO_URI`.

### 5. Start the API Server

Development mode with auto-reload:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Production mode:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6. Verify the API

Visit the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login (OAuth2 form-based)
- `POST /auth/login_json` - Login (JSON-based)
- `GET /auth/me` - Get current user info

### Patients
- `GET /patients` - List all patients (admin/doctor)
- `POST /patients` - Create patient profile
- `GET /patients/{patient_id}` - Get patient details
- `PATCH /patients/{patient_id}` - Update patient profile
- `DELETE /patients/{patient_id}` - Delete patient (admin)

### Doctors
- `GET /doctors` - List all doctors
- `POST /doctors` - Create doctor profile
- `GET /doctors/{doctor_id}` - Get doctor details
- `PATCH /doctors/{doctor_id}` - Update doctor profile
- `DELETE /doctors/{doctor_id}` - Delete doctor (admin)

### Consultations
- `GET /consultations` - List consultations
- `POST /consultations` - Create consultation
- `GET /consultations/{consultation_id}` - Get consultation details
- `PATCH /consultations/{consultation_id}` - Update consultation
- `DELETE /consultations/{consultation_id}` - Delete consultation (admin)

### Medical Records
- `GET /medical_records` - List medical records
- `POST /medical_records` - Create medical record (admin/doctor)
- `GET /medical_records/{record_id}` - Get medical record
- `PATCH /medical_records/{record_id}` - Update medical record (admin/doctor)
- `DELETE /medical_records/{record_id}` - Delete medical record (admin)

## Testing the API

### Using cURL

See `docs/API_VERIFICATION.md` for comprehensive curl command examples.

Quick test:

```bash
# Health check
curl http://localhost:8000/

# Register a user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"patient"}'

# Login
curl -X POST http://localhost:8000/auth/login_json \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### Using the Interactive Docs

1. Navigate to http://localhost:8000/docs
2. Click "Authorize" button
3. Register a user via `/auth/register`
4. Login via `/auth/login_json` to get a token
5. Copy the `access_token` from the response
6. Paste it in the "Authorize" dialog (without "Bearer " prefix)
7. Now you can test all authenticated endpoints

## Authentication

The API uses JWT Bearer tokens for authentication. After logging in, include the token in requests:

```bash
Authorization: Bearer <your_token_here>
```

Alternative methods supported:
- Custom header: `X-Auth-Token: <token>`
- Query parameter: `?token=<token>` (not recommended for production)

### User Roles

- **patient**: Can manage their own profile and medical records
- **doctor**: Can view patients, create consultations, manage medical records
- **admin**: Full access to all resources

## Project Structure

```
healthcare_backend_api/
├── src/
│   └── api/
│       ├── __init__.py
│       ├── main.py              # FastAPI app and CORS config
│       ├── auth.py              # JWT and password utilities
│       ├── db.py                # MongoDB connection and indexes
│       ├── dependencies.py      # Auth dependencies and RBAC
│       ├── models.py            # Pydantic models
│       └── routers/
│           ├── __init__.py
│           ├── auth.py          # Auth endpoints
│           ├── patients.py      # Patient endpoints
│           ├── doctors.py       # Doctor endpoints
│           ├── consultations.py # Consultation endpoints
│           └── medical_records.py # Medical records endpoints
├── tests/
│   └── test_auth_jwt.py         # JWT authentication tests
├── docs/
│   ├── API_VERIFICATION.md      # Curl command examples
│   └── FRONTEND_AUTH_NOTES.md   # Frontend integration notes
├── interfaces/
│   └── openapi.json             # Generated OpenAPI spec
├── .env                         # Environment configuration (DO NOT COMMIT)
├── .env.example                 # Example environment file
├── requirements.txt             # Python dependencies
├── verify_config.py             # Configuration verification script
└── README.md                    # This file
```

## Security Notes

- **Never commit `.env` file** - Add it to `.gitignore`
- **Use strong JWT_SECRET** - Generate a cryptographically secure random string
- **HTTPS in production** - Always use HTTPS for production deployments
- **Rotate secrets regularly** - Update JWT_SECRET periodically
- **MongoDB authentication** - Always use authentication in production
- **Rate limiting** - Consider adding rate limiting for production

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload
```

### MongoDB Connection Failed

- Verify MongoDB is running: `mongosh` or `mongo`
- Check `MONGO_URI` in `.env` is correct
- Ensure network connectivity and firewall rules

### Import Errors

Ensure you're running commands from the `healthcare_backend_api` directory and all dependencies are installed:

```bash
pip install -r requirements.txt
```

### CORS Errors

Update `CORS_ORIGINS` in `.env` to include your frontend origin:

```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Running Tests

```bash
pytest tests/ -v
```

## Generating OpenAPI Spec

To regenerate the OpenAPI specification:

```bash
python -m src.api.generate_openapi
```

Output will be written to `interfaces/openapi.json`.

## License

Proprietary - Healthcare Connect Application

## Support

For issues or questions, refer to the project documentation or contact the development team.
