# Healthcare Connect - Integration & Environment Guide

## Overview

This guide walks through validating and testing the complete integration between:
- **MongoDB Database** (port 5000)
- **FastAPI Backend** (port 3001)
- **Flutter Frontend** (mobile app)

---

## Current Configuration

### MongoDB (healthcare_database)
- **Port**: 5000
- **Database**: myapp
- **Credentials**: appuser / dbuser123
- **Auth Source**: admin
- **Connection**: `mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin`

### Backend API (healthcare_backend_api)
- **Port**: 3001
- **Framework**: FastAPI + Uvicorn
- **Database**: MongoDB (myapp)
- **Environment**: See `.env` file

### Flutter Frontend (healthcare_flutter_frontend)
- **Platform**: Flutter (iOS/Android/Web)
- **Backend URL**: 
  - iOS/Web: `http://localhost:3001`
  - Android Emulator: `http://10.0.2.2:3001` (auto-remapped)

---

## Pre-Flight Checklist

### 1. Database Verification

```bash
# Check if MongoDB is running (should show port 5000)
netstat -an | grep 5000
# or
lsof -i :5000

# Test connection with mongosh
mongosh "mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin"

# Inside mongosh, verify collections
show collections
# Expected: users, patients, doctors, consultations, medical_records

# Check for data
db.users.countDocuments()
# Should return > 0 if seeded
```

**If no data exists**, seed the database:
```bash
cd healthcare-connect-5348-5358/healthcare_database
mongosh "mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin" \
  --eval "var DB_NAME='myapp'" seed_mongo.js
```

### 2. Backend Environment Validation

```bash
cd healthcare-connect-5348-5357/healthcare_backend_api

# Verify .env exists and is configured
cat .env

# Expected values:
# MONGO_URI=mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin
# MONGO_DB=myapp
# JWT_SECRET=<32+ character secret>
# BACKEND_BASE_URL=http://localhost:3001

# Run validation script
python validate_integration.py
```

### 3. Frontend Environment Validation

```bash
cd healthcare-connect-5348-5359/healthcare_flutter_frontend

# Verify .env exists
cat .env

# Expected:
# BACKEND_BASE_URL=http://localhost:3001

# Ensure dependencies are installed
flutter pub get
```

---

## Step-by-Step Integration Testing

### Step 1: Start Backend Server

```bash
cd healthcare-connect-5348-5357/healthcare_backend_api

# Install dependencies if needed
pip install -r requirements.txt

# Start the backend
./start.sh

# Or manually:
# uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

**Expected Output:**
```
Starting Healthcare Connect API
MongoDB URI: localhost:5000/myapp?authSource=admin
MongoDB Database: myapp
✓ Database connection successful
✓ Startup completed successfully
```

### Step 2: Test Backend Health

Open a new terminal:

```bash
# Basic health check
curl http://localhost:3001/

# Expected: {"message":"Healthy","status":"ok"}

# Database health check
curl http://localhost:3001/health/db

# Expected: {"message":"Database connection healthy","status":"ok","database":"myapp"}
```

### Step 3: Test Authentication Flow

```bash
# Register a new user (optional)
curl -X POST http://localhost:3001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "role": "patient",
    "full_name": "Test User"
  }'

# Login with demo user
curl -X POST http://localhost:3001/auth/login_json \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.patient@example.com",
    "password": "demo123"
  }'

# Expected: {"access_token":"eyJ...","token_type":"bearer"}

# Save the token and test /auth/me
TOKEN="<paste_token_here>"
curl http://localhost:3001/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: User profile with role
```

### Step 4: Test API Endpoints

```bash
# Get token first (from Step 3)
TOKEN="<your_token>"

# List doctors (all users can view)
curl http://localhost:3001/doctors \
  -H "Authorization: Bearer $TOKEN"

# List consultations (filtered by role)
curl http://localhost:3001/consultations \
  -H "Authorization: Bearer $TOKEN"

# List medical records (filtered by role)
curl http://localhost:3001/medical_records \
  -H "Authorization: Bearer $TOKEN"
```

### Step 5: Test Frontend Connection

```bash
cd healthcare-connect-5348-5359/healthcare_flutter_frontend

# For iOS Simulator
flutter run -d ios

# For Android Emulator
flutter run -d android

# For Web
flutter run -d chrome
```

**In the Flutter app:**
1. Navigate to Login screen
2. Enter credentials: `jane.patient@example.com` / `demo123`
3. Verify login succeeds and token is stored
4. Navigate to Dashboard
5. Verify doctors list loads
6. Navigate to Appointments/Consultations
7. Verify data loads correctly

---

## Common Issues & Solutions

### Issue 1: Backend Can't Connect to MongoDB

**Symptoms:**
```
Database connection failed
ServerSelectionTimeoutError
```

**Solutions:**
- Verify MongoDB is running: `lsof -i :5000`
- Check port in MONGO_URI matches actual MongoDB port (5000)
- Verify credentials: `appuser:dbuser123`
- Test with mongosh directly

### Issue 2: Flutter App Can't Reach Backend

**Symptoms:**
- Network errors in Flutter app
- "Connection refused"

**Solutions:**
- Verify backend is running: `curl http://localhost:3001/`
- For Android emulator, ensure `BACKEND_BASE_URL=http://localhost:3001` (env.dart auto-remaps to 10.0.2.2)
- Check CORS_ORIGINS in backend .env includes proper origins
- For real devices, use LAN IP: `http://192.168.x.x:3001`

### Issue 3: CORS Errors in Browser/Flutter Web

**Symptoms:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
Update backend `.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://10.0.2.2:3001,https://appetize.io
```
Restart backend after changing.

### Issue 4: JWT Token Invalid/Expired

**Symptoms:**
```
401 Unauthorized
Could not validate credentials
```

**Solutions:**
- Check JWT_SECRET is set correctly (not a MongoDB URI!)
- Token expires after ACCESS_TOKEN_EXPIRES_MINUTES (default 60)
- Login again to get fresh token
- Verify JWT_CLOCK_SKEW_SECONDS for time sync issues

### Issue 5: No Seed Data / Empty Collections

**Solution:**
```bash
cd healthcare-connect-5348-5358/healthcare_database
mongosh "mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin" \
  --eval "var DB_NAME='myapp'" seed_mongo.js
```

---

## Demo Credentials

### Patients
- **Email**: jane.patient@example.com
- **Password**: demo123
- **Role**: patient

- **Email**: john.patient@example.com
- **Password**: demo123
- **Role**: patient

### Doctors
- **Email**: dr.smith@example.com
- **Password**: demo123
- **Role**: doctor
- **Specialty**: Cardiology

- **Email**: dr.lee@example.com
- **Password**: demo123
- **Role**: doctor
- **Specialty**: Dermatology

---

## API Documentation

Once backend is running:
- **Swagger UI**: http://localhost:3001/docs
- **ReDoc**: http://localhost:3001/redoc
- **OpenAPI JSON**: http://localhost:3001/openapi.json

---

## E2E Flow Testing

### Patient Flow
1. **Login**: jane.patient@example.com / demo123
2. **View Profile**: GET /auth/me (verify role=patient)
3. **List Doctors**: GET /doctors
4. **View Consultations**: GET /consultations (only patient's own)
5. **View Medical Records**: GET /medical_records (only patient's own)

### Doctor Flow
1. **Login**: dr.smith@example.com / demo123
2. **View Profile**: GET /auth/me (verify role=doctor)
3. **List Patients**: GET /patients (doctors can see all)
4. **View Consultations**: GET /consultations (assigned to this doctor)
5. **Create Medical Record**: POST /medical_records (doctor can create)

### Admin Operations
*Note: Seed script creates demo users but may not create admin by default.*

To create admin user:
```bash
mongosh "mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin"

use myapp
db.users.insertOne({
  email: "admin@healthcare.com",
  password_hash: "$2b$12$abcdefghijklmnopqrstuv12345678901234567890123456789012",
  role: "admin",
  created_at: new Date()
})
```

---

## Monitoring & Logs

### Backend Logs
When running with `./start.sh`, logs appear in terminal:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failures requiring attention

### Database Logs
Check MongoDB logs if container:
```bash
docker logs <mongodb_container_name>
```

### Flutter Logs
```bash
flutter logs
```

---

## Network Configuration Reference

| Platform | Backend URL | Notes |
|----------|-------------|-------|
| iOS Simulator | http://localhost:3001 | Direct localhost works |
| Android Emulator | http://localhost:3001 | Auto-remapped to 10.0.2.2 by env.dart |
| Flutter Web | http://localhost:3001 | Same network |
| Real Device | http://192.168.x.x:3001 | Use machine's LAN IP |

---

## Quick Commands Reference

```bash
# Test backend health
curl http://localhost:3001/

# Test DB health
curl http://localhost:3001/health/db

# Login
curl -X POST http://localhost:3001/auth/login_json \
  -H "Content-Type: application/json" \
  -d '{"email":"jane.patient@example.com","password":"demo123"}'

# Test with token
curl http://localhost:3001/doctors \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check MongoDB
mongosh "mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin" --eval "db.users.countDocuments()"

# Seed database
cd healthcare-connect-5348-5358/healthcare_database
mongosh "mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin" --eval "var DB_NAME='myapp'" seed_mongo.js

# Run validation
cd healthcare-connect-5348-5357/healthcare_backend_api
python validate_integration.py
```

---

## Success Criteria

✅ **Database**: MongoDB accessible, collections seeded, users exist  
✅ **Backend**: Health endpoints respond, DB connection OK, /docs accessible  
✅ **Authentication**: Login works, /auth/me returns user with role, token persists  
✅ **CORS**: No CORS errors in browser/Flutter  
✅ **Doctors**: List loads for all authenticated users  
✅ **Consultations**: List filtered by role (patient sees own, doctor sees assigned)  
✅ **Medical Records**: List filtered by role, doctors can create  
✅ **Frontend**: Login flow works, dashboard loads, navigation functional  

---

## Next Steps

After validation passes:
1. Deploy to staging/production environments
2. Update connection strings for production MongoDB
3. Use strong JWT_SECRET (generate with `openssl rand -hex 32`)
4. Enable HTTPS/TLS
5. Configure proper CORS origins
6. Set up monitoring and logging
7. Implement rate limiting
8. Regular backups

---

**For questions or issues, refer to:**
- Backend README: `healthcare-connect-5348-5357/healthcare_backend_api/README.md`
- Database README: `healthcare-connect-5348-5358/healthcare_database/README.md`
- API Docs: http://localhost:3001/docs (when running)
