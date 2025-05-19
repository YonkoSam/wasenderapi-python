import pytest
from wasenderapi.models import Contact, RateLimitInfo
from wasenderapi.client import WasenderClient
import json
from datetime import datetime

@pytest.fixture
def mock_rate_limit_info():
    return {
        "limit": 100,
        "remaining": 99,
        "reset_timestamp": int(datetime.now().timestamp()) + 3600
    }

@pytest.fixture
def mock_contact():
    return {
        "jid": "1234567890",
        "name": "Contact Name",
        "notify": "Contact Display Name",
        "verifiedName": "Verified Business Name",
        "imgUrl": "https://profile.pic.url/image.jpg",
        "status": "Hey there! I am using WhatsApp."
    }

class TestContactTypeDefinitions:
    class TestCoreDataStructures:
        def test_contact_type_should_be_correct_all_fields(self, mock_contact):
            contact = {**mock_contact, "exists": True}
            assert contact["jid"] == "1234567890"
            assert contact["name"] == "Contact Name"
            assert contact["notify"] == "Contact Display Name"
            assert contact["verifiedName"] == "Verified Business Name"
            assert contact["imgUrl"] == "https://profile.pic.url/image.jpg"
            assert contact["status"] == "Hey there! I am using WhatsApp."
            assert contact["exists"] == True

        def test_contact_type_should_allow_optional_fields_to_be_undefined(self):
            minimal_contact = {
                "jid": "0987654321"
            }
            assert minimal_contact["jid"] == "0987654321"
            assert "name" not in minimal_contact
            assert "notify" not in minimal_contact
            assert "verifiedName" not in minimal_contact
            assert "imgUrl" not in minimal_contact
            assert "status" not in minimal_contact
            assert "exists" not in minimal_contact

    class TestAPIResponseTypes:
        def test_get_all_contacts_response_type_should_be_correct(self, mock_contact):
            response = {
                "success": True,
                "message": "Contacts retrieved successfully",
                "data": [
                    mock_contact,
                    {**mock_contact, "jid": "1122334455", "name": "Another Contact"}
                ]
            }
            assert response["success"] == True
            assert response["message"] == "Contacts retrieved successfully"
            assert len(response["data"]) == 2
            assert response["data"][0]["jid"] == "1234567890"
            assert response["data"][1]["name"] == "Another Contact"

        def test_get_contact_info_response_type_should_be_correct(self, mock_contact):
            response = {
                "success": True,
                "message": "Contact info retrieved",
                "data": {**mock_contact, "exists": True}
            }
            assert response["success"] == True
            assert response["message"] == "Contact info retrieved"
            assert response["data"]["jid"] == "1234567890"
            assert response["data"]["exists"] == True

        def test_get_contact_profile_picture_response_type_should_be_correct_with_imgurl(self):
            response = {
                "success": True,
                "message": "Profile picture URL retrieved",
                "data": {
                    "imgUrl": "https://profile.pic.url/image.jpg"
                }
            }
            assert response["success"] == True
            assert response["message"] == "Profile picture URL retrieved"
            assert response["data"]["imgUrl"] == "https://profile.pic.url/image.jpg"

        def test_get_contact_profile_picture_response_type_should_be_correct_null_imgurl(self):
            response = {
                "success": True,
                "message": "Profile picture URL retrieved, but not set",
                "data": {
                    "imgUrl": None
                }
            }
            assert response["success"] == True
            assert response["message"] == "Profile picture URL retrieved, but not set"
            assert response["data"]["imgUrl"] is None

        def test_contact_action_response_type_should_be_correct_block(self):
            response = {
                "success": True,
                "message": "Contact action successful",
                "data": {
                    "message": "Contact blocked"
                }
            }
            assert response["success"] == True
            assert response["message"] == "Contact action successful"
            assert response["data"]["message"] == "Contact blocked"

        def test_contact_action_response_type_should_be_correct_unblock(self):
            response = {
                "success": True,
                "message": "Contact action successful",
                "data": {
                    "message": "Contact unblocked"
                }
            }
            assert response["success"] == True
            assert response["data"]["message"] == "Contact unblocked"

    class TestResultTypes:
        def test_get_all_contacts_result_type_should_be_correct(self, mock_contact, mock_rate_limit_info):
            result = {
                "response": {
                    "success": True,
                    "message": "Fetched contacts",
                    "data": [mock_contact]
                },
                "rateLimit": mock_rate_limit_info
            }
            assert result["response"]["data"][0]["name"] == "Contact Name"
            assert result["rateLimit"]["limit"] == 100

        def test_get_contact_info_result_type_should_be_correct(self, mock_contact, mock_rate_limit_info):
            result = {
                "response": {
                    "success": True,
                    "message": "Fetched contact info",
                    "data": {**mock_contact, "exists": False}
                },
                "rateLimit": mock_rate_limit_info
            }
            assert result["response"]["data"]["jid"] == "1234567890"
            assert result["response"]["data"]["exists"] == False
            assert result["rateLimit"]["remaining"] == 99

        def test_get_contact_profile_picture_result_type_should_be_correct(self, mock_rate_limit_info):
            result = {
                "response": {
                    "success": True,
                    "message": "Fetched profile picture",
                    "data": {"imgUrl": "https://some.url/pic.png"}
                },
                "rateLimit": mock_rate_limit_info
            }
            assert result["response"]["data"]["imgUrl"] == "https://some.url/pic.png"
            assert result["rateLimit"]["reset_timestamp"] > 0

        def test_contact_action_result_type_should_be_correct(self, mock_rate_limit_info):
            result = {
                "response": {
                    "success": True,
                    "message": "Action performed",
                    "data": {"message": "Contact blocked successfully"}
                },
                "rateLimit": mock_rate_limit_info
            }
            assert result["response"]["data"]["message"] == "Contact blocked successfully"
            assert isinstance(datetime.fromtimestamp(result["rateLimit"]["reset_timestamp"]), datetime) 