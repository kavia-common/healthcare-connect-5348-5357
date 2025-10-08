#!/usr/bin/env python3
"""
Integration Validation Script
Validates MongoDB connectivity, backend health, and configuration.
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def main():
    print("=" * 70)
    print("Healthcare Connect - Integration Validation")
    print("=" * 70)
    print()
    
    # 1. Check environment variables
    print("1. Environment Configuration:")
    print("-" * 70)
    
    mongo_uri = os.getenv("MONGO_URI", "")
    mongo_db = os.getenv("MONGO_DB", "")
    jwt_secret = os.getenv("JWT_SECRET", "")
    cors_origins = os.getenv("CORS_ORIGINS", "")
    backend_url = os.getenv("BACKEND_BASE_URL", "")
    
    print(f"   MONGO_URI: {mongo_uri[:50]}..." if len(mongo_uri) > 50 else f"   MONGO_URI: {mongo_uri}")
    print(f"   MONGO_DB: {mongo_db}")
    print(f"   JWT_SECRET: {'✓ Set' if jwt_secret and len(jwt_secret) >= 32 else '✗ Missing or too short (need 32+ chars)'}")
    print(f"   CORS_ORIGINS: {cors_origins}")
    print(f"   BACKEND_BASE_URL: {backend_url}")
    print()
    
    # Check for common issues
    issues = []
    if not mongo_uri:
        issues.append("MONGO_URI not set")
    if not mongo_db:
        issues.append("MONGO_DB not set")
    if not jwt_secret or len(jwt_secret) < 32:
        issues.append("JWT_SECRET missing or too short (need 32+ characters)")
    if "mongodb://localhost:27017" in mongo_uri or "mongodb://127.0.0.1:27017" in mongo_uri:
        issues.append("MongoDB URI uses port 27017, but database is on port 5000")
    if jwt_secret and jwt_secret.startswith("mongodb://"):
        issues.append("JWT_SECRET appears to be a MongoDB URI (should be a random secret)")
    
    if issues:
        print("   ⚠ Configuration Issues Found:")
        for issue in issues:
            print(f"      - {issue}")
        print()
    else:
        print("   ✓ Basic configuration looks good")
        print()
    
    # 2. Test MongoDB Connection
    print("2. MongoDB Connection Test:")
    print("-" * 70)
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Ping the database
        await client.admin.command('ping')
        print("   ✓ MongoDB connection successful")
        
        # Check database and collections
        db = client[mongo_db]
        collections = await db.list_collection_names()
        print(f"   ✓ Database '{mongo_db}' accessible")
        print(f"   ✓ Collections found: {len(collections)}")
        
        expected_collections = ['users', 'patients', 'doctors', 'consultations', 'medical_records']
        missing_collections = [c for c in expected_collections if c not in collections]
        
        if collections:
            print(f"      Available: {', '.join(collections)}")
        
        if missing_collections:
            print(f"   ⚠ Missing expected collections: {', '.join(missing_collections)}")
            print(f"      Run seed script to create demo data")
        else:
            print(f"   ✓ All expected collections present")
        
        # Check for sample data
        users_count = await db.users.count_documents({})
        print(f"   ✓ Users collection: {users_count} documents")
        
        client.close()
        print()
        
    except Exception as e:
        print(f"   ✗ MongoDB connection failed: {e}")
        print(f"      Make sure MongoDB is running on the configured port")
        print()
        return False
    
    # 3. Database Seed Status
    print("3. Database Seed Data:")
    print("-" * 70)
    
    try:
        client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[mongo_db]
        
        users_count = await db.users.count_documents({})
        patients_count = await db.patients.count_documents({})
        doctors_count = await db.doctors.count_documents({})
        consultations_count = await db.consultations.count_documents({})
        records_count = await db.medical_records.count_documents({})
        
        print(f"   Users: {users_count}")
        print(f"   Patients: {patients_count}")
        print(f"   Doctors: {doctors_count}")
        print(f"   Consultations: {consultations_count}")
        print(f"   Medical Records: {records_count}")
        
        if users_count == 0:
            print()
            print("   ⚠ No seed data found. To seed the database, run:")
            print("      cd healthcare-connect-5348-5358/healthcare_database")
            print("      mongosh \"mongodb://appuser:dbuser123@localhost:5000/myapp?authSource=admin\" --eval \"var DB_NAME='myapp'\" seed_mongo.js")
        else:
            print("   ✓ Database contains data")
        
        client.close()
        print()
        
    except Exception as e:
        print(f"   ✗ Could not check seed data: {e}")
        print()
    
    # 4. Summary
    print("=" * 70)
    print("Validation Summary:")
    print("-" * 70)
    
    if not issues:
        print("✓ Configuration is correct")
        print("✓ MongoDB is reachable")
        print()
        print("Next Steps:")
        print("1. Start backend: cd healthcare-connect-5348-5357/healthcare_backend_api && ./start.sh")
        print("2. Test health endpoint: curl http://localhost:3001/")
        print("3. Test DB health: curl http://localhost:3001/health/db")
        print("4. View API docs: http://localhost:3001/docs")
        print()
        return True
    else:
        print("✗ Configuration issues found (see above)")
        print()
        print("Please fix the issues and run this script again.")
        print()
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nValidation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nValidation failed with error: {e}")
        sys.exit(1)
