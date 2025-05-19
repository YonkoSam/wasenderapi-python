import pytest
from unittest.mock import Mock, patch
from wasenderapi.client import WasenderClient
import json
import requests

@pytest.fixture
def api_key():
    return "test_api_key"

@pytest.fixture
def mock_response():
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({
        "success": True,
        "message": "Operation successful",
        "data": {"messageId": "test-message-id"},
        "rateLimit": {
            "limit": 1000,
            "remaining": 999,
            "reset": 1234567890
        }
    }).encode()
    response.encoding = "utf-8"
    return response

@pytest.fixture
def mock_error_response():
    response = requests.Response()
    response.status_code = 400
    response._content = json.dumps({
        "success": False,
        "message": "Bad request",
        "error": {
            "code": "INVALID_PARAMETER",
            "details": "Invalid phone number format"
        }
    }).encode()
    response.encoding = "utf-8"
    return response

@pytest.fixture
def mock_contacts_response():
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({
        "success": True,
        "message": "Contacts retrieved successfully",
        "data": {
            "contacts": [
                {
                    "jid": "1234567890@s.whatsapp.net",
                    "name": "Test Contact",
                    "notify": "Test",
                    "verifiedName": None,
                    "imgUrl": None,
                    "status": "Hey there!",
                    "exists": True
                }
            ]
        },
        "rateLimit": {
            "limit": 1000,
            "remaining": 999,
            "reset": 1234567890
        }
    }).encode()
    response.encoding = "utf-8"
    return response

@pytest.fixture
def mock_client(api_key):
    client = WasenderClient(api_key)
    client.fetch_impl = Mock()
    return client

@pytest.fixture
def client(api_key):
    return WasenderClient(api_key) 