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

## Quickstart (Local Development)

1) Configure environment
- Copy `.env.example` to `.env`
- Update any values as needed (defaults below are suggested for local dev)

Example .env:
```
MONGODB_URI=mongodb://localhost:5001
DB_NAME=healthcare
JWT_SECRET=replace_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:3000
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) Start MongoDB
- Ensure a MongoDB instance is running and accessible at `mongodb://localhost:5001`
  - See the Database container README for options (Docker, local, etc.)

4) Run the server on port 3001 (to match Flutter BASE_URL)
```
uvicorn app.main:app --reload --port 3001
```

5) Verify API is up
- Health: http://localhost:3001/ -> `{ "status": "ok", "docs": "/docs" }`
- Swagger: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc

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

Note: Registration requires a role in the payload, e.g. `{ "email": "...", "password": "...", "role": "patient", "full_name": "..." }`.

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
- The backend reads values from environment variables (not directly from `.env`). For local development, use a tool or shell to export the variables or run with uvicorn while `.env` is loaded via your environment.
- CORS is configured via `CORS_ORIGINS` (comma-separated). Ensure your Flutter web origin is listed if you are running on the web.

## E2E Validation Checklist

- Register (POST /auth/register) with role included, or create users via the database/seed and login.
- Login (POST /auth/login)
- View doctors (GET /doctors)
- Book consultation (POST /consultations)
- View appointments (consultations) (GET /consultations with patient_id or doctor_id filter)
- View records (GET /medical_records)

## Troubleshooting (Frontend/Backend Field and Endpoint Alignment)

- Registration payload: Frontend currently sends `{ name, email, password }` but backend requires `role` and uses `full_name` (optional).  
  Workaround: Register via a REST client including `role: "patient"`; or update the frontend to send a default role.

- Doctors list: Backend `DoctorPublic` exposes `{ id, user_id, specialty, years_experience, bio }`. The frontend view expects `name` and `hospital`.  
  Action: Update the frontend to derive a display name (e.g., from user full_name if you extend the backend payload) or display specialty; `hospital` is not provided by the backend.

- Appointments vs Consultations: Backend uses `/consultations`, while frontend uses `/appointments`.  
  Action: Update the frontend repositories to call `/consultations` and map fields accordingly.

- Medical records fields: Backend returns `diagnosis`, `treatments`, `created_at`, etc. The frontend expects `title`, `date`, `summary`.  
  Action: Map `title` to `diagnosis` (or a derived label), `date` to `created_at`, and `summary` to `treatments` or a suitable field.

- Database schema alignment: The provided seed script in the database container uses ObjectIds and different field shapes. The backend uses string IDs for some collections (e.g., user `_id` set to email).  
  Action: Prefer creating data via backend endpoints to keep schema consistent, or adjust the seed to match backend expectations.

## License
MIT
