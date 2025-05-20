import pytest
from unittest.mock import Mock, patch
from wasenderapi.models import RetryConfig
from wasenderapi import create_sync_wasender
import json
import requests

@pytest.fixture
def api_key():
    return "test_api_key"

@pytest.fixture
def personal_access_token():
    return "test_personal_access_token"

@pytest.fixture
def webhook_secret():
    return "test_webhook_secret"

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
        "errors": [{
            "code": "INVALID_PARAMETER",
            "message": "Invalid phone number format"
        }]
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
        "data": [
            {
                "jid": "1234567890@s.whatsapp.net",
                "name": "Test Contact",
                "notify": "Test",
                "verifiedName": None,
                "imgUrl": None,
                "status": "Hey there!",
                "isWhatsAppUser": True
            }
        ]
    }).encode()
    response.encoding = "utf-8"
    return response

@pytest.fixture
def sync_client(api_key, personal_access_token, webhook_secret):
    retry_config_disabled = RetryConfig(enabled=False)
    return create_sync_wasender(
        api_key=api_key,
        personal_access_token=personal_access_token,
        webhook_secret=webhook_secret,
        retry_options=retry_config_disabled
    )

@pytest.fixture
def mocked_sync_client(sync_client):
    return sync_client

@pytest.fixture
def client_with_mocked_requests(api_key):
    with patch('requests.request') as mock_req:
        retry_config_disabled = RetryConfig(enabled=False)
        client = create_sync_wasender(api_key=api_key, retry_options=retry_config_disabled)
        yield client, mock_req 