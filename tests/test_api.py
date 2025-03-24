import requests
import time

# Base URL of your API
base_url = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    response = requests.get(f"{base_url}/health")
    print(f"Health check status code: {response.status_code}")
    print(f"Health check response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    
    print("✅ Health check test passed!")

def test_root():
    """Test the root endpoint"""
    response = requests.get(f"{base_url}")
    print(f"Root endpoint status code: {response.status_code}")
    print(f"Root endpoint response: {response.json()}")
    
    assert response.status_code == 200
    assert "message" in response.json()
    
    print("✅ Root endpoint test passed!")

if __name__ == "__main__":
    print("Starting API tests...")
    time.sleep(1)
    
    try:
        test_health()
        test_root()
        print("\nAll tests passed! 🎉")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}") 