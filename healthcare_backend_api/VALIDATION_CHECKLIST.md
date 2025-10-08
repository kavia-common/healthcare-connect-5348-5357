# Backend API Validation Checklist

Use this checklist to verify all backend endpoints and features are working correctly.

## Pre-Flight Checks

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file exists and JWT_SECRET is set to a secure value (not placeholder)
- [ ] MongoDB is running and accessible
- [ ] Configuration verified: `python verify_config.py` returns success
- [ ] Server starts without errors: `uvicorn src.api.main:app --reload`

## Core Functionality Tests

### Health & Documentation

- [ ] Health check: `GET /` returns `{"message": "Healthy"}`
- [ ] Swagger UI accessible: http://localhost:8000/docs
- [ ] ReDoc accessible: http://localhost:8000/redoc
- [ ] OpenAPI JSON available: http://localhost:8000/openapi.json

### Authentication Endpoints (Public)

**Register Users:**
- [ ] Register patient: `POST /auth/register` with role="patient"
- [ ] Register doctor: `POST /auth/register` with role="doctor"
- [ ] Register admin: `POST /auth/register` with role="admin"
- [ ] Duplicate email rejected: Returns 400

**Login:**
- [ ] Form-based login: `POST /auth/login` (OAuth2 form)
- [ ] JSON login: `POST /auth/login_json` (JSON body)
- [ ] Invalid credentials rejected: Returns 401
- [ ] Token contains: access_token and token_type="bearer"

**Current User:**
- [ ] Get current user: `GET /auth/me` with valid token
- [ ] Returns user profile with id, email, full_name, role
- [ ] Missing token rejected: Returns 401
- [ ] Invalid token rejected: Returns 401
- [ ] Expired token rejected: Returns 401 with detail="Token expired"

### Patient Endpoints (Authenticated)

**As Patient:**
- [ ] Create own profile: `POST /patients` (user_id inferred from token)
- [ ] List patients rejected: `GET /patients` returns 403
- [ ] Get own profile: `GET /patients/{id}` returns own patient data
- [ ] Get other profile rejected: `GET /patients/{other_id}` returns 403
- [ ] Update own profile: `PATCH /patients/{id}` succeeds
- [ ] Update other profile rejected: `PATCH /patients/{other_id}` returns 403
- [ ] Delete rejected: `DELETE /patients/{id}` returns 403

**As Doctor:**
- [ ] List all patients: `GET /patients` returns array
- [ ] Get any patient: `GET /patients/{id}` returns patient data
- [ ] Create patient rejected: `POST /patients` returns 403
- [ ] Update patient rejected: `PATCH /patients/{id}` returns 403
- [ ] Delete rejected: `DELETE /patients/{id}` returns 403

**As Admin:**
- [ ] List all patients: `GET /patients` returns array
- [ ] Create patient for user: `POST /patients` with user_id
- [ ] Get any patient: `GET /patients/{id}` returns patient data
- [ ] Update any patient: `PATCH /patients/{id}` succeeds
- [ ] Delete any patient: `DELETE /patients/{id}` returns 204

### Doctor Endpoints (Authenticated)

**As Doctor:**
- [ ] Create own profile: `POST /doctors` (user_id inferred)
- [ ] List all doctors: `GET /doctors` returns array
- [ ] Get any doctor: `GET /doctors/{id}` returns doctor data
- [ ] Update own profile: `PATCH /doctors/{id}` succeeds
- [ ] Update other profile rejected: `PATCH /doctors/{other_id}` returns 403
- [ ] Delete rejected: `DELETE /doctors/{id}` returns 403

**As Patient:**
- [ ] List all doctors: `GET /doctors` returns array
- [ ] Get any doctor: `GET /doctors/{id}` returns doctor data
- [ ] Create doctor rejected: `POST /doctors` returns 403
- [ ] Update rejected: `PATCH /doctors/{id}` returns 403
- [ ] Delete rejected: `DELETE /doctors/{id}` returns 403

**As Admin:**
- [ ] Create doctor for user: `POST /doctors` with user_id
- [ ] List all doctors: `GET /doctors` returns array
- [ ] Get any doctor: `GET /doctors/{id}` returns doctor data
- [ ] Update any doctor: `PATCH /doctors/{id}` succeeds
- [ ] Delete any doctor: `DELETE /doctors/{id}` returns 204

### Consultation Endpoints (Authenticated)

**As Doctor:**
- [ ] Create consultation: `POST /consultations` (doctor_id inferred from token)
- [ ] List own consultations: `GET /consultations` returns only doctor's consultations
- [ ] Get own consultation: `GET /consultations/{id}` returns consultation
- [ ] Get other consultation rejected: `GET /consultations/{other_id}` returns 403
- [ ] Update own consultation: `PATCH /consultations/{id}` succeeds
- [ ] Update other consultation rejected: Returns 403
- [ ] Delete rejected: `DELETE /consultations/{id}` returns 403

**As Patient:**
- [ ] Create rejected: `POST /consultations` returns 403
- [ ] List own consultations: `GET /consultations` returns only patient's consultations
- [ ] Get own consultation: `GET /consultations/{id}` returns consultation
- [ ] Get other consultation rejected: Returns 403
- [ ] Update rejected: `PATCH /consultations/{id}` returns 403
- [ ] Delete rejected: `DELETE /consultations/{id}` returns 403

**As Admin:**
- [ ] Create consultation: `POST /consultations` with any doctor_id
- [ ] List all consultations: `GET /consultations` returns all
- [ ] Get any consultation: `GET /consultations/{id}` returns consultation
- [ ] Update any consultation: `PATCH /consultations/{id}` succeeds
- [ ] Delete any consultation: `DELETE /consultations/{id}` returns 204

### Medical Records Endpoints (Authenticated)

**As Patient:**
- [ ] Create rejected: `POST /medical_records` returns 403
- [ ] List own records: `GET /medical_records` returns only own records
- [ ] Get own record: `GET /medical_records/{id}` returns record
- [ ] Get other record rejected: Returns 403
- [ ] Update rejected: `PATCH /medical_records/{id}` returns 403
- [ ] Delete rejected: `DELETE /medical_records/{id}` returns 403

**As Doctor:**
- [ ] Create medical record: `POST /medical_records` succeeds
- [ ] List with patient_id filter: `GET /medical_records?patient_id={id}` returns records
- [ ] List without filter rejected: `GET /medical_records` returns 400
- [ ] Get any record: `GET /medical_records/{id}` returns record
- [ ] Update any record: `PATCH /medical_records/{id}` succeeds
- [ ] Delete rejected: `DELETE /medical_records/{id}` returns 403

**As Admin:**
- [ ] Create medical record: `POST /medical_records` succeeds
- [ ] List all records: `GET /medical_records` returns all
- [ ] List with filter: `GET /medical_records?patient_id={id}` returns filtered
- [ ] Get any record: `GET /medical_records/{id}` returns record
- [ ] Update any record: `PATCH /medical_records/{id}` succeeds
- [ ] Delete any record: `DELETE /medical_records/{id}` returns 204

## Security & CORS Tests

### JWT Token Handling

- [ ] Token in Authorization header accepted: `Authorization: Bearer {token}`
- [ ] Token in X-Auth-Token header accepted: `X-Auth-Token: {token}`
- [ ] Token in query param accepted (non-strict): `?token={token}`
- [ ] Query param rejected on strict endpoints: `/auth/me?token={token}` returns 401
- [ ] Expired token returns 401 with detail="Token expired"
- [ ] Invalid token returns 401
- [ ] Missing token returns 401

### CORS

- [ ] Preflight OPTIONS requests succeed
- [ ] Access-Control-Allow-Origin header present
- [ ] Access-Control-Allow-Methods includes GET, POST, PATCH, DELETE
- [ ] Access-Control-Allow-Headers includes Authorization, Content-Type
- [ ] Requests from configured origins accepted

### Role-Based Access Control (RBAC)

- [ ] Patient can only access own resources
- [ ] Doctor can view patients, create consultations/records
- [ ] Admin has full access to all resources
- [ ] Role enforcement on all protected endpoints
- [ ] Proper 403 responses for insufficient permissions

## Data Validation Tests

### User Registration

- [ ] Email format validated
- [ ] Password required
- [ ] Valid roles: patient, doctor, admin
- [ ] Invalid role rejected
- [ ] Duplicate email rejected

### Patient Profile

- [ ] Age is integer or null
- [ ] Gender is string or null
- [ ] Address is string or null
- [ ] user_id is required

### Doctor Profile

- [ ] Specialty is string or null
- [ ] Bio is string or null
- [ ] user_id is required

### Consultation

- [ ] patient_id is required and valid ObjectId
- [ ] doctor_id is required and valid ObjectId
- [ ] scheduled_at is valid ISO datetime
- [ ] notes is string or null
- [ ] Invalid patient_id returns 404
- [ ] Invalid doctor_id returns 404

### Medical Record

- [ ] patient_id is required and valid ObjectId
- [ ] entries is array of strings
- [ ] Invalid patient_id returns 404

## Database Integration Tests

- [ ] Users collection: unique email index enforced
- [ ] Patients collection: unique user_id index enforced
- [ ] Doctors collection: unique user_id index enforced
- [ ] Consultations indexed by patient_id and scheduled_at
- [ ] Medical records indexed by patient_id
- [ ] Duplicate email registration fails with unique constraint error

## Performance & Reliability

- [ ] Server starts in <5 seconds
- [ ] Health check responds in <100ms
- [ ] Login responds in <500ms
- [ ] List endpoints respond in <1s with <100 records
- [ ] No memory leaks after 100 requests
- [ ] Graceful shutdown on Ctrl+C

## Documentation Quality

- [ ] OpenAPI spec generated correctly
- [ ] All endpoints documented in Swagger UI
- [ ] Request/response schemas visible
- [ ] Example values provided
- [ ] Tags organize endpoints logically
- [ ] Security schemes documented
- [ ] Error responses documented

## Environment Variables

- [ ] MONGO_URI loads correctly
- [ ] MONGO_DB loads correctly
- [ ] JWT_SECRET not using placeholder
- [ ] JWT_ALGORITHM is HS256
- [ ] ACCESS_TOKEN_EXPIRES_MINUTES is 60
- [ ] JWT_CLOCK_SKEW_SECONDS is 30
- [ ] CORS_ORIGINS loads and parses correctly

## Final Verification

- [ ] All 29 endpoints responding
- [ ] All 5 tag groups present (Auth, Patients, Doctors, Consultations, Medical Records)
- [ ] No startup errors or warnings (except MongoDB connection if not running)
- [ ] Indexes created successfully on startup
- [ ] Clean shutdown without errors

---

## Quick Test Script

Run this to test core functionality:

```bash
# Health check
curl http://localhost:8000/

# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","role":"patient"}'

# Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login_json \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# Get current user
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

---

**Total Checks**: 130+

Once all checks pass, your backend API is fully validated and production-ready! ✅
