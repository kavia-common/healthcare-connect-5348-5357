# Healthcare Connect Backend API

FastAPI backend service using MongoDB (Motor), with JWT authentication and REST endpoints for:
- Authentication: /auth
- Patients: /patients
- Doctors: /doctors
- Consultations: /consultations
- Medical Records: /medical_records

OpenAPI docs are available at `/docs` and `/redoc`.

## Features
- FastAPI + Motor (async MongoDB)
- JWT-based authentication
- Role-based access (patient, doctor, admin)
- Pydantic v2 models with validation
- CORS configuration via environment
- Startup index ensuring using JSON spec

## Requirements
- Python 3.11+
- MongoDB running and reachable

## Setup

1) Create and configure environment variables. For local development:
- Copy `.env.example` to `.env`
- Adjust values for your environment

Environment variables:
- MONGODB_URI
- DB_NAME
- JWT_SECRET
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- CORS_ORIGINS
- INDEXES_FILE (optional)

2) Install dependencies:
```
pip install -r requirements.txt
```

3) Run the server:
```
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for Swagger UI.

## Index Ensuring

On startup, the app will attempt to read a MongoDB indexes specification from:
- `INDEXES_FILE` environment variable, if set and valid; otherwise
- `../healthcare-connect-5348-5358/healthcare_database/indexes/indexes.json` relative to the repo root, if available.

Example of the spec (from the database container):
```json
{
  "collections": {
    "users": [
      { "keys": { "email": 1 }, "options": { "unique": true, "name": "uniq_users_email" } }
    ],
    "doctors": [
      { "keys": { "specialty": 1 }, "options": { "name": "idx_doctors_specialty" } }
    ],
    "consultations": [
      { "keys": { "patient_id": 1, "datetime": -1 }, "options": { "name": "idx_consultations_patient_datetime" } }
    ],
    "medical_records": [
      { "keys": { "patient_id": 1, "created_at": -1 }, "options": { "name": "idx_medical_records_patient_created" } }
    ]
  }
}
```

## Authentication

- Register: `POST /auth/register`
- Login: `POST /auth/login`

Both endpoints return a `TokenResponse` including `access_token` and user info.  
Use the token as a Bearer token to access protected endpoints.

## Patients

- `POST /patients` (patient role) to create profile
- `GET /patients/me` (patient role) to get own profile
- `GET /patients` list, `GET /patients/{id}`, `PUT /patients/{id}`, `DELETE /patients/{id}`

## Doctors

- `POST /doctors` (doctor role) to create profile
- `GET /doctors/me` (doctor role) to get own profile
- `GET /doctors` list, `GET /doctors/{id}`, `PUT /doctors/{id}`, `DELETE /doctors/{id}`

## Consultations

- `POST /consultations` create consultation
- `GET /consultations` list with filters
- `GET /consultations/{id}`, `PUT /consultations/{id}`, `DELETE /consultations/{id}`

## Medical Records

- `POST /medical_records` (doctor-only)
- `GET /medical_records` paginated and role-aware
- `GET /medical_records/{id}`, `PUT /medical_records/{id}` (doctor-only), `DELETE /medical_records/{id}` (doctor/admin)

## Notes
- The backend does not read `.env` directly; values are taken from environment variables.  
- CORS is configured via `CORS_ORIGINS` (comma-separated). Ensure your Flutter frontend origin is listed.

## License
MIT
