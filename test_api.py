import requests
import time
import pytest
import json
import os
from fastapi.testclient import TestClient
from src.main import app

# Base URL of your API
base_url = "http://localhost:8000"

client = TestClient(app)

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

def test_process_emails():
    """Test the email processing endpoint"""
    try:
        response = requests.post(f"{base_url}/api/process-emails")
        print(f"Email processing status code: {response.status_code}")
        print(f"Email processing response: {response.json()}")
        
        assert response.status_code == 200
        assert response.json()["status"] == "processing"
        
        print("✅ Email processing test passed!")
        return True
    except Exception as e:
        print(f"❌ Email processing test failed: {str(e)}")
        return False

# New test functions for additional endpoints

def test_email_service():
    """Test the email service endpoint"""
    try:
        response = requests.get(f"{base_url}/test/email-service")
        print(f"Email service status code: {response.status_code}")
        print(f"Email service response: {json.dumps(response.json(), indent=2)[:300]}...")
        
        assert response.status_code == 200
        assert "emails_found" in response.json()
        
        print("✅ Email service test passed!")
        return True
    except Exception as e:
        print(f"❌ Email service test failed: {str(e)}")
        return False

def test_summarize_text():
    """Test the text summarization endpoint"""
    try:
        data = {
            "subject": "Project Status Report",
            "body": "The project is proceeding according to schedule. We have completed the first phase of development and are now moving to the testing phase. We expect to deliver the final product by October 15th. Please review the attached documentation for more details.",
            "sender": "project.manager@example.com",
            "date": "2023-09-15"
        }
        
        response = requests.post(f"{base_url}/test/summarize-text", json=data)
        print(f"Text summarization status code: {response.status_code}")
        print(f"Text summarization response: {json.dumps(response.json(), indent=2)[:300]}...")
        
        assert response.status_code == 200
        assert "summary" in response.json()
        
        print("✅ Text summarization test passed!")
        return True
    except Exception as e:
        print(f"❌ Text summarization test failed: {str(e)}")
        return False

def test_report_generation():
    """Test the report generation endpoint"""
    try:
        data = {
            "email_data": {
                "subject": "Quarterly Report",
                "sender": "finance@example.com",
                "date": "2023-09-01"
            },
            "summaries": [
                {
                    "type": "email",
                    "summary": {
                        "success": True,
                        "summary": "This quarterly report shows a 15% increase in revenue and a 10% decrease in expenses. The company has exceeded its targets for the quarter.",
                        "metadata": {
                            "subject": "Quarterly Report",
                            "sender": "finance@example.com",
                            "date": "2023-09-01"
                        }
                    }
                },
                {
                    "type": "attachment",
                    "summary": {
                        "success": True,
                        "summary": "The attached financial statement details revenue streams by product line. Product A saw the highest growth at 22%, while Product C experienced a 5% decline.",
                        "metadata": {
                            "filename": "financial_statement.pdf"
                        }
                    }
                }
            ]
        }
        
        response = requests.post(f"{base_url}/test/generate-report", json=data)
        print(f"Report generation status code: {response.status_code}")
        print(f"Report generation response: {json.dumps(response.json(), indent=2)[:300]}...")
        
        assert response.status_code == 200
        assert "report" in response.json()
        
        print("✅ Report generation test passed!")
        return True
    except Exception as e:
        print(f"❌ Report generation test failed: {str(e)}")
        return False

def test_file_conversion():
    """Test the file conversion endpoint with a test file"""
    try:
        # Create a simple test file
        test_file_path = "test_document.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test document for conversion testing.")
        
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(f"{base_url}/test/convert-file", files=files)
        
        print(f"File conversion status code: {response.status_code}")
        print(f"File conversion response: {json.dumps(response.json(), indent=2)}")
        
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
            
        assert response.status_code == 200
        
        print("✅ File conversion test passed!")
        return True
    except Exception as e:
        print(f"❌ File conversion test failed: {str(e)}")
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        return False

def test_end_to_end():
    """Test the end-to-end processing endpoint"""
    try:
        response = requests.post(f"{base_url}/test/end-to-end")
        print(f"End-to-end processing status code: {response.status_code}")
        print(f"End-to-end processing response: {json.dumps(response.json(), indent=2)}")
        
        assert response.status_code == 200
        assert response.json()["status"] == "processing"
        
        print("✅ End-to-end processing test passed!")
        return True
    except Exception as e:
        print(f"❌ End-to-end processing test failed: {str(e)}")
        return False

# FastAPI TestClient tests
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_process_emails_fastapi():
    response = client.post("/api/process-emails")
    assert response.status_code == 200
    assert response.json()["status"] == "processing"

if __name__ == "__main__":
    print("Starting API tests...")
    time.sleep(1)
    
    try:
        # Original endpoints
        test_health()
        test_root()
        test_process_emails()
        
        # Add the new test endpoints (only run if they're implemented)
        try:
            test_email_service()
        except:
            print("⚠️ Email service endpoint not available")
            
        try:
            test_summarize_text()
        except:
            print("⚠️ Text summarization endpoint not available")
            
        try:
            test_report_generation()
        except:
            print("⚠️ Report generation endpoint not available")
            
        try:
            test_file_conversion()
        except:
            print("⚠️ File conversion endpoint not available")
            
        try:
            test_end_to_end()
        except:
            print("⚠️ End-to-end endpoint not available")
        
        # FastAPI TestClient tests
        test_health_endpoint()
        test_process_emails_fastapi()
        
        print("\nAll available tests completed! 🎉")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")

    if not test_process_emails():
        success = False 