import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "SahaayAI" in response.json()["service"]

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "SahaayAI" in response.json()["service"]
    assert "supported_languages" in response.json()
    assert "supported_domains" in response.json()

def test_metrics_endpoint():
    """Test metrics endpoint"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "timestamp" in response.json()

def test_readiness_check():
    """Test readiness check"""
    response = client.get("/ready")
    assert response.status_code == 200
    assert "ready" in response.json()
    assert "checks" in response.json()

@pytest.mark.asyncio
async def test_sms_message():
    """Test SMS message handling"""
    message_data = {
        "phone_number": "+1234567890",
        "message": "I need help with healthcare",
        "channel": "sms"
    }
    
    response = client.post("/api/v1/message/sms", json=message_data)
    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_web_message():
    """Test web message handling"""
    message_data = {
        "phone_number": "+1234567890",
        "message": "Tell me about PM-KISAN scheme",
        "channel": "web",
        "language": "en"
    }
    
    response = client.post("/api/v1/message/web", json=message_data)
    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["success"] is True

def test_invalid_phone_number():
    """Test invalid phone number validation"""
    message_data = {
        "phone_number": "invalid",
        "message": "Test message",
        "channel": "sms"
    }
    
    response = client.post("/api/v1/message/sms", json=message_data)
    assert response.status_code == 422  # Validation error

def test_rate_limiting():
    """Test rate limiting (basic test)"""
    # This would need to be more sophisticated in real tests
    # For now, just verify the endpoint works
    response = client.get("/health")
    assert "X-RateLimit-Remaining-Minute" in response.headers

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
