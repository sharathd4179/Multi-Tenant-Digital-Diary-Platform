"""
Simple script to create a tenant via the API.
Run this to create a working tenant for testing.
"""
import requests
import uuid

API_URL = "http://localhost:8000"

def create_tenant():
    """Create a new tenant with admin user."""
    tenant_id = str(uuid.uuid4())
    
    payload = {
        "tenant_id": tenant_id,
        "username": "admin",
        "email": "admin@example.com",
        "password": "admin123",
        "role": "admin"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register-tenant",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            user_data = response.json()
            print("\n✅ Tenant created successfully!")
            print(f"\n📋 Login Credentials:")
            print(f"   Tenant ID: {tenant_id}")
            print(f"   Username: admin")
            print(f"   Password: admin123")
            print(f"\n🌐 Login at: http://localhost:8501")
            return tenant_id
        else:
            print(f"\n❌ Failed to create tenant: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

if __name__ == "__main__":
    create_tenant()



