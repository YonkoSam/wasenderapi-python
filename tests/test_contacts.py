import pytest
from wasenderapi.models import Contact, RateLimitInfo
from wasenderapi.contacts import (
    GetAllContactsResult,
    GetContactInfoResult,
    GetContactProfilePictureResult,
    ContactActionResult,
    # Individual response types if needed for more granular tests, but result types are more comprehensive
    GetAllContactsResponse, GetContactInfoResponse, GetContactProfilePictureResponse, ContactActionResponse,
    ProfilePicData, ContactActionData
)
from pydantic import ValidationError
import json
from datetime import datetime
from wasenderapi import create_async_wasender
from wasenderapi.models import RetryConfig
from unittest.mock import AsyncMock

@pytest.fixture
def mock_rate_limit_info_dict():
    return {
        "limit": 100,
        "remaining": 99,
        "reset_timestamp": int(datetime.now().timestamp()) + 3600
    }

@pytest.fixture
def specific_contact_api_data_for_model_test(): # Renamed fixture
    return {
        "jid": "1234567890@s.whatsapp.net",
        "name": "Contact Name API Model Test",
        "notify": "Contact Display API Model Test",
        "verifiedName": "Verified Business API Model Test",
        "imgUrl": "https://profile.pic.url/model_test.jpg",
        "status": "API status: Model Test Active!",
        "exists": True
    }

@pytest.fixture
def mock_multiple_contacts_api_data(specific_contact_api_data_for_model_test): # Update dependent fixture if necessary, or use original mock_contact_api_data if that's intended for this one
    # For mock_multiple_contacts_api_data, decide if it should use the highly specific one or a more general one.
    # Assuming it still uses a general form, let's define one or use the name that might be from conftest if needed by other tests.
    # For now, let it use the renamed one to see the effect. Or, create another general one if needed.
    contact2 = specific_contact_api_data_for_model_test.copy()
    contact2["jid"] = "0987654321@s.whatsapp.net"
    contact2["name"] = "Another Contact API Model Test"
    return [specific_contact_api_data_for_model_test, contact2]

@pytest.fixture
async def async_client_contacts_mocked_internals():
    retry_config_disabled = RetryConfig(enabled=False)
    # Use a dummy API key for these tests as internal methods are mocked
    client = create_async_wasender(api_key="test_contacts_key", retry_options=retry_config_disabled)
    client._get_internal = AsyncMock(name="_get_internal")
    client._post_internal = AsyncMock(name="_post_internal")
    return client

class TestContactModel: # Renamed from TestCoreDataStructures
    def test_contact_model_all_fields(self, specific_contact_api_data_for_model_test): # Use renamed fixture
        # Instantiate Contact model using ** on the fixture data (which has camelCase keys like 'verifiedName')
        # Pydantic should use the aliases to populate the snake_case fields.
        contact = Contact(**specific_contact_api_data_for_model_test)
        
        assert contact.jid == specific_contact_api_data_for_model_test["jid"]
        assert contact.name == specific_contact_api_data_for_model_test["name"]
        # Now check the model's snake_case attributes against the fixture's camelCase values
        assert contact.verified_name == specific_contact_api_data_for_model_test["verifiedName"]
        assert contact.img_url == specific_contact_api_data_for_model_test["imgUrl"]
        assert contact.status == specific_contact_api_data_for_model_test["status"]
        assert contact.exists == specific_contact_api_data_for_model_test["exists"]

        dumped_contact = contact.model_dump(by_alias=True)
        assert dumped_contact["verifiedName"] == specific_contact_api_data_for_model_test["verifiedName"]
        assert dumped_contact["imgUrl"] == specific_contact_api_data_for_model_test["imgUrl"]

    def test_contact_model_minimal_fields(self):
        minimal_data = {"jid": "0987654321@s.whatsapp.net"}
        contact = Contact(**minimal_data)
        assert contact.jid == minimal_data["jid"]
        assert contact.name is None
        dumped_contact = contact.model_dump(by_alias=True, exclude_none=True)
        assert "name" not in dumped_contact

    def test_contact_model_missing_jid_raises_error(self):
        with pytest.raises(ValidationError):
            Contact(name="Test Name")

# Removed TestAPIResponseTypes class as its functionality is better covered by testing Result models

class TestContactResultModels:
    def test_get_all_contacts_result(self, mock_multiple_contacts_api_data, mock_rate_limit_info_dict):
        raw_response_data = {
            "success": True,
            "message": "Fetched contacts successfully",
            "data": mock_multiple_contacts_api_data
        }
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}
        
        result_model = GetAllContactsResult(**full_result_data)
        
        assert result_model.response.success is True
        assert result_model.response.message == "Fetched contacts successfully"
        assert len(result_model.response.data) == 2
        assert isinstance(result_model.response.data[0], Contact)
        assert result_model.response.data[0].jid == mock_multiple_contacts_api_data[0]["jid"]
        assert result_model.response.data[0].name == mock_multiple_contacts_api_data[0]["name"]
        # Check aliasing for verifiedName and imgUrl from the first contact
        assert result_model.response.data[0].verified_name == mock_multiple_contacts_api_data[0]["verifiedName"]
        assert result_model.response.data[0].img_url == mock_multiple_contacts_api_data[0]["imgUrl"]
        
        assert isinstance(result_model.rate_limit, RateLimitInfo)
        assert result_model.rate_limit.limit == mock_rate_limit_info_dict["limit"]

    def test_get_contact_info_result(self, specific_contact_api_data_for_model_test, mock_rate_limit_info_dict):
        # This test might need to use the original 'mock_contact_api_data' if it expects general data
        # For now, let it use the specific one to see if it resolves the primary issue.
        # If this test relies on the conftest version of mock_contact_api_data, it will need adjustment.
        raw_response_data = {
            "success": True,
            "message": "Contact info retrieved",
            "data": specific_contact_api_data_for_model_test # Using renamed fixture here
        }
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}

        result_model = GetContactInfoResult(**full_result_data)

        assert result_model.response.success is True
        assert isinstance(result_model.response.data, Contact)
        assert result_model.response.data.jid == specific_contact_api_data_for_model_test["jid"]
        assert result_model.response.data.status == specific_contact_api_data_for_model_test["status"]
        assert result_model.rate_limit.remaining == mock_rate_limit_info_dict["remaining"]

    def test_get_contact_profile_picture_result(self, mock_rate_limit_info_dict):
        profile_pic_api_data = {"imgUrl": "https://some.url/pic.png"}
        raw_response_data = {
            "success": True,
            "message": "Fetched profile picture",
            "data": profile_pic_api_data
        }
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}
        
        result_model = GetContactProfilePictureResult(**full_result_data)

        assert result_model.response.data.img_url == profile_pic_api_data["imgUrl"]
        assert result_model.rate_limit.reset_timestamp == mock_rate_limit_info_dict["reset_timestamp"]

        # Test with null imgUrl
        profile_pic_api_data_null = {"imgUrl": None}
        raw_response_data_null = {
            "success": True, "message": "No pic", "data": profile_pic_api_data_null
        }
        full_result_data_null = {"response": raw_response_data_null, "rate_limit": mock_rate_limit_info_dict}
        result_model_null = GetContactProfilePictureResult(**full_result_data_null)
        assert result_model_null.response.data.img_url is None

    def test_contact_action_result(self, mock_rate_limit_info_dict):
        contact_action_api_data = {"message": "Contact blocked successfully"}
        raw_response_data = {
            "success": True,
            "message": "Action performed",
            "data": contact_action_api_data
        }
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}

        result_model = ContactActionResult(**full_result_data)
        
        assert result_model.response.data.message == contact_action_api_data["message"]
        assert isinstance(result_model.rate_limit.get_reset_timestamp_as_date(), datetime)

class TestContactsClientMethods:
    @pytest.mark.asyncio
    async def test_get_contacts(self, async_client_contacts_mocked_internals, mock_multiple_contacts_api_data, mock_rate_limit_info_dict):
        client = async_client_contacts_mocked_internals
        
        # Setup mock return value for _get_internal
        mock_response_payload = {
            "success": True, 
            "message": "Contacts fetched", 
            "data": mock_multiple_contacts_api_data
        }
        client._get_internal.return_value = {
            "response": mock_response_payload,
            "rate_limit": mock_rate_limit_info_dict
        }

        result: GetAllContactsResult = await client.get_contacts()

        client._get_internal.assert_called_once_with("/contacts")
        assert isinstance(result, GetAllContactsResult)
        assert result.response.success is True
        assert len(result.response.data) == len(mock_multiple_contacts_api_data)
        assert result.response.data[0].name == mock_multiple_contacts_api_data[0]["name"]
        assert result.rate_limit.limit == mock_rate_limit_info_dict["limit"]

    @pytest.mark.asyncio
    async def test_get_contact_info(self, async_client_contacts_mocked_internals, specific_contact_api_data_for_model_test, mock_rate_limit_info_dict):
        # Same consideration for this client method test
        client = async_client_contacts_mocked_internals
        contact_phone = "1234567890" 
        
        mock_response_payload = {"success": True, "message": "Info fetched", "data": specific_contact_api_data_for_model_test}
        client._get_internal.return_value = {
            "response": mock_response_payload,
            "rate_limit": mock_rate_limit_info_dict
        }

        result: GetContactInfoResult = await client.get_contact_info(contact_phone_number=contact_phone)

        client._get_internal.assert_called_once_with(f"/contacts/{contact_phone}")
        assert isinstance(result, GetContactInfoResult)
        assert result.response.data.jid == specific_contact_api_data_for_model_test["jid"]

    @pytest.mark.asyncio
    async def test_get_contact_profile_picture(self, async_client_contacts_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_contacts_mocked_internals
        contact_phone = "1234567890"
        expected_img_url = "https://example.com/pic.jpg"

        mock_response_payload = {"success": True, "message": "Pic fetched", "data": {"imgUrl": expected_img_url}}
        client._get_internal.return_value = {
            "response": mock_response_payload,
            "rate_limit": mock_rate_limit_info_dict
        }

        result: GetContactProfilePictureResult = await client.get_contact_profile_picture(contact_phone_number=contact_phone)

        client._get_internal.assert_called_once_with(f"/contacts/{contact_phone}/profile-picture")
        assert isinstance(result, GetContactProfilePictureResult)
        assert result.response.data.img_url == expected_img_url

    @pytest.mark.asyncio
    async def test_block_contact(self, async_client_contacts_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_contacts_mocked_internals
        contact_phone = "1234567890"
        action_message = "Contact blocked/unblocked successfully."

        mock_response_payload = {"success": True, "message": "Contact blocked/unblocked successfully.", "data": {"message": action_message}}
        client._post_internal.return_value = {
            "response": mock_response_payload,
            "rate_limit": mock_rate_limit_info_dict
        }

        result: ContactActionResult = await client.block_contact(contact_phone_number=contact_phone)

        client._post_internal.assert_called_once_with(f"/contacts/{contact_phone}/block", None)
        assert isinstance(result, ContactActionResult)
        assert result.response.data.message == action_message

    @pytest.mark.asyncio
    async def test_unblock_contact(self, async_client_contacts_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_contacts_mocked_internals
        contact_phone = "1234567890"
        action_message = "Contact blocked/unblocked successfully."

        mock_response_payload = {"success": True, "message": "Contact blocked/unblocked successfully.", "data": {"message": action_message}}
        client._post_internal.return_value = {
            "response": mock_response_payload,
            "rate_limit": mock_rate_limit_info_dict
        }
    
        result: ContactActionResult = await client.unblock_contact(contact_phone_number=contact_phone)

        client._post_internal.assert_called_once_with(f"/contacts/{contact_phone}/unblock", None)
        assert isinstance(result, ContactActionResult)
        assert result.response.data.message == action_message 