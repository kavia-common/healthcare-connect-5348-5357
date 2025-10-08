# API Endpoint Verification Guide

This document provides sample curl commands to verify all FastAPI endpoints.

## Prerequisites

1. Ensure MongoDB is running and accessible
2. Start the FastAPI server: `uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload`
3. Server should be running at http://localhost:8000

## Health Check

```bash
curl -X GET http://localhost:8000/
```

Expected: `{"message":"Healthy"}`

## Authentication Endpoints

### 1. Register a New User (Patient)

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "SecurePass123!",
    "full_name": "John Patient",
    "role": "patient"
  }'
```

Expected: 201 Created with user object containing id, email, full_name, role

### 2. Register a Doctor

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "SecurePass123!",
    "full_name": "Dr. Sarah Smith",
    "role": "doctor"
  }'
```

### 3. Register an Admin

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "full_name": "Admin User",
    "role": "admin"
  }'
```

### 4. Login (Form-based OAuth2)

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=patient@example.com&password=SecurePass123!"
```

Expected: `{"access_token":"<JWT_TOKEN>","token_type":"bearer"}`

### 5. Login (JSON-based)

```bash
curl -X POST http://localhost:8000/auth/login_json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "SecurePass123!"
  }'
```

Expected: `{"access_token":"<JWT_TOKEN>","token_type":"bearer"}`

**Save the token from login response for subsequent requests:**

```bash
export TOKEN="<paste_your_token_here>"
```

### 6. Get Current User Info (/auth/me)

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

Expected: User profile with id, email, full_name, role

## Patient Endpoints

### 1. Create Patient Profile

```bash
curl -X POST http://localhost:8000/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 35,
    "gender": "Male",
    "address": "123 Main St, City, State 12345"
  }'
```

Expected: 201 Created with patient object

### 2. List All Patients (Admin/Doctor only)

```bash
curl -X GET http://localhost:8000/patients \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Specific Patient

```bash
curl -X GET http://localhost:8000/patients/<patient_id> \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update Patient Profile

```bash
curl -X PATCH http://localhost:8000/patients/<patient_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 36,
    "address": "456 New St, City, State 12345"
  }'
```

### 5. Delete Patient (Admin only)

```bash
curl -X DELETE http://localhost:8000/patients/<patient_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Doctor Endpoints

### 1. Create Doctor Profile

```bash
curl -X POST http://localhost:8000/doctors \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "specialty": "Cardiology",
    "bio": "Board-certified cardiologist with 10 years experience"
  }'
```

### 2. List All Doctors

```bash
curl -X GET http://localhost:8000/doctors \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Specific Doctor

```bash
curl -X GET http://localhost:8000/doctors/<doctor_id> \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update Doctor Profile

```bash
curl -X PATCH http://localhost:8000/doctors/<doctor_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "specialty": "Interventional Cardiology",
    "bio": "Updated bio with new specialization"
  }'
```

### 5. Delete Doctor (Admin only)

```bash
curl -X DELETE http://localhost:8000/doctors/<doctor_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Consultation Endpoints

### 1. Create Consultation

```bash
curl -X POST http://localhost:8000/consultations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "<patient_id>",
    "doctor_id": "<doctor_id>",
    "scheduled_at": "2024-12-31T14:00:00Z",
    "notes": "Follow-up consultation for heart condition"
  }'
```

### 2. List Consultations

```bash
curl -X GET http://localhost:8000/consultations \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Specific Consultation

```bash
curl -X GET http://localhost:8000/consultations/<consultation_id> \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update Consultation

```bash
curl -X PATCH http://localhost:8000/consultations/<consultation_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "scheduled_at": "2024-12-31T15:00:00Z",
    "notes": "Rescheduled to 3 PM"
  }'
```

### 5. Delete Consultation (Admin only)

```bash
curl -X DELETE http://localhost:8000/consultations/<consultation_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Medical Records Endpoints

### 1. Create Medical Record

```bash
curl -X POST http://localhost:8000/medical_records \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "<patient_id>",
    "entries": ["Blood pressure: 120/80", "Temperature: 98.6F"]
  }'
```

### 2. List Medical Records

```bash
# Admin: all records
curl -X GET http://localhost:8000/medical_records \
  -H "Authorization: Bearer $TOKEN"

# Doctor: requires patient_id filter
curl -X GET "http://localhost:8000/medical_records?patient_id=<patient_id>" \
  -H "Authorization: Bearer $TOKEN"

# Patient: only their own
curl -X GET http://localhost:8000/medical_records \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Specific Medical Record

```bash
curl -X GET http://localhost:8000/medical_records/<record_id> \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Update Medical Record

```bash
curl -X PATCH http://localhost:8000/medical_records/<record_id> \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entries": ["Blood pressure: 120/80", "Temperature: 98.6F", "Heart rate: 72 bpm"]
  }'
```

### 5. Delete Medical Record (Admin only)

```bash
curl -X DELETE http://localhost:8000/medical_records/<record_id> \
  -H "Authorization: Bearer $TOKEN"
```

## Testing CORS

To verify CORS configuration is working:

```bash
curl -X OPTIONS http://localhost:8000/auth/me \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Authorization" \
  -v
```

Expected: Response headers should include:
- `Access-Control-Allow-Origin: http://localhost:3000`
- `Access-Control-Allow-Methods: *`
- `Access-Control-Allow-Headers: *`

## Alternative Token Passing Methods

The API supports multiple ways to pass authentication tokens:

1. **Standard Authorization Header (Recommended):**
   ```bash
   -H "Authorization: Bearer $TOKEN"
   ```

2. **Custom X-Auth-Token Header (Fallback):**
   ```bash
   -H "X-Auth-Token: $TOKEN"
   ```

3. **Query Parameter (Not recommended for sensitive routes):**
   ```bash
   curl "http://localhost:8000/auth/me?token=$TOKEN"
   ```

## OpenAPI Documentation

Once the server is running, access interactive API documentation at:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Notes

- Replace `<patient_id>`, `<doctor_id>`, `<consultation_id>`, `<record_id>` with actual IDs from your database
- Ensure MongoDB is running before starting the API
- All timestamps should be in ISO 8601 format (e.g., "2024-12-31T14:00:00Z")
- Role-based access control (RBAC) is enforced on all endpoints
- Tokens expire based on `ACCESS_TOKEN_EXPIRES_MINUTES` setting (default: 60 minutes)
