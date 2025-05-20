import pytest
from unittest.mock import AsyncMock, patch
from wasenderapi import create_async_wasender, __version__ as SDK_VERSION
from wasenderapi.models import RetryConfig, WasenderSendResult
from wasenderapi.errors import WasenderAPIError
import json
import httpx

@pytest.fixture
async def async_client_with_mocked_post():
    retry_config_disabled = RetryConfig(enabled=False)
    client = create_async_wasender("test_api_key", retry_options=retry_config_disabled)
    client._post_internal = AsyncMock(name="_post_internal")
    
    mock_post_return_value = {
        "response": {"success": True, "message": "ok", "data": {"messageId": "mock_message_id"}},
        "rate_limit": {"limit": 1000, "remaining": 999, "reset_timestamp": 1620000000}
    }
    client._post_internal.return_value = mock_post_return_value
    return client

@pytest.fixture
def success_api_response_data():
    return {"success": True, "message": "Message sent successfully", "data": {"messageId": "test-message-id"}}

@pytest.fixture
def rate_limit_data():
    return {
        "limit": 1000,
        "remaining": 999,
        "reset_timestamp": 1620000000
    }

@pytest.fixture
def error_api_response_data():
    return {
        "success": False, 
        "message": "Invalid phone number format", 
        "errors": [{"field": "to", "message": "The 'to' field is invalid."}]
    }

@pytest.mark.asyncio
async def test_send_text_constructs_correct_payload_and_calls_post_internal(async_client_with_mocked_post):
    client = async_client_with_mocked_post
    
    test_to = "+1234567890"
    test_body = "Hello Wasender!"

    expected_message_id_val = "specific_test_msg_id_text"
    client._post_internal.return_value = {
        "response": {"success": True, "message": "Text sent", "data": {"messageId": expected_message_id_val}},
        "rate_limit": {"limit": 100, "remaining": 99, "reset_timestamp": 1670000000}
    }

    response: WasenderSendResult = await client.send_text(to=test_to, text_body=test_body, custom_param="test_val")

    client._post_internal.assert_called_once()
    
    args, kwargs = client._post_internal.call_args
    
    assert args[0] == "/send-message"
    
    expected_payload = {
        "to": test_to,
        "messageType": "text",
        "text": {"body": test_body},
        "custom_param": "test_val"
    }
    assert args[1] == expected_payload
    
    assert response.response.success is True
    assert response.response.message == "Text sent"
    assert response.response.data.message_id == expected_message_id_val
    assert response.rate_limit.limit == 100
    assert response.rate_limit.remaining == 99

@pytest.mark.asyncio
async def test_send_image(async_client_with_mocked_post, success_api_response_data, rate_limit_data):
    client = async_client_with_mocked_post
    client._post_internal.return_value = {
        "response": success_api_response_data,
        "rate_limit": rate_limit_data
    }
    
    test_to = "1234567890"
    test_url = "https://example.com/image.jpg"
    test_caption = "Test image"

    response = await client.send_image(to=test_to, url=test_url, caption=test_caption)
        
    client._post_internal.assert_called_once_with(
        "/send-message", 
        {
            "to": test_to, 
            "messageType": "image",
            "image": {"url": test_url, "caption": test_caption}
        }
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]
    assert response.rate_limit.limit == rate_limit_data["limit"]

@pytest.mark.asyncio
async def test_send_video(async_client_with_mocked_post, success_api_response_data, rate_limit_data):
    client = async_client_with_mocked_post
    client._post_internal.return_value = {
        "response": success_api_response_data,
        "rate_limit": rate_limit_data
    }
    
    test_to = "1234567890"
    test_url = "https://example.com/video.mp4"
    test_caption = "Test video"

    response = await client.send_video(to=test_to, url=test_url, caption=test_caption)
            
    client._post_internal.assert_called_once_with(
        "/send-message", 
        {
            "to": test_to, 
            "messageType": "video",
            "video": {"url": test_url, "caption": test_caption}
        }
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]

@pytest.mark.asyncio
async def test_send_document(async_client_with_mocked_post, success_api_response_data, rate_limit_data):
    client = async_client_with_mocked_post
    client._post_internal.return_value = {
        "response": success_api_response_data,
        "rate_limit": rate_limit_data
    }
    
    test_to = "1234567890"
    test_url = "https://example.com/doc.pdf"
    test_filename = "Test Document.pdf"
    test_caption = "Test document"

    response = await client.send_document(to=test_to, url=test_url, filename=test_filename, caption=test_caption)
    
    client._post_internal.assert_called_once_with(
        "/send-message", 
        {
            "to": test_to, 
            "messageType": "document",
            "document": {"url": test_url, "filename": test_filename, "caption": test_caption}
        }
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]

@pytest.mark.asyncio
async def test_send_audio(async_client_with_mocked_post, success_api_response_data, rate_limit_data):
    client = async_client_with_mocked_post
    test_to = "1234567890"
    test_url = "https://example.com/audio.mp3"

    # Test Case 1: ptt = False
    client._post_internal.reset_mock() # Reset mock for a clean assertion
    client._post_internal.return_value = {
        "response": success_api_response_data,
        "rate_limit": rate_limit_data
    }
    response_no_ptt = await client.send_audio(to=test_to, url=test_url, ptt=False)
    client._post_internal.assert_called_once_with(
        "/send-message",
        {
            "to": test_to,
            "messageType": "audio",
            "audio": {"url": test_url, "ptt": False}
        }
    )
    assert response_no_ptt.response.success is True

    # Test Case 2: ptt = True
    client._post_internal.reset_mock() # Reset mock for a clean assertion
    # Update message_id for distinct response if necessary, though not asserted here
    updated_success_data = {**success_api_response_data, "data": {**success_api_response_data["data"], "message_id": "mock_audio_ptt_true"}}
    client._post_internal.return_value = {
        "response": updated_success_data, # Use potentially updated data
        "rate_limit": rate_limit_data
    }
    response_ptt = await client.send_audio(to=test_to, url=test_url, ptt=True)
    client._post_internal.assert_called_once_with(
        "/send-message",
        {
            "to": test_to,
            "messageType": "audio",
            "audio": {"url": test_url, "ptt": True}
        }
    )
    assert response_ptt.response.success is True

@pytest.mark.asyncio
async def test_send_location(async_client_with_mocked_post, success_api_response_data, rate_limit_data):
    client = async_client_with_mocked_post
    client._post_internal.return_value = {
        "response": success_api_response_data,
        "rate_limit": rate_limit_data
    }
    
    test_to = "1234567890"
    lat, lon = 37.7749, -122.4194
    loc_name, loc_addr = "San Francisco HQ", "123 Main St"

    response = await client.send_location(to=test_to, latitude=lat, longitude=lon, name=loc_name, address=loc_addr)
        
    client._post_internal.assert_called_once_with(
        "/send-message", 
        {
            "to": test_to, 
            "messageType": "location",
            "location": {"latitude": lat, "longitude": lon, "name": loc_name, "address": loc_addr}
        }
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]

@pytest.mark.asyncio
async def test_api_error_raised_from_post_internal(async_client_with_mocked_post, error_api_response_data):
    client = async_client_with_mocked_post
    
    original_api_message = error_api_response_data["message"]
    original_error_details = error_api_response_data["errors"]

    client._post_internal.side_effect = WasenderAPIError(
        message=original_api_message,
        status_code=400,
        api_message=original_api_message,
        error_details=original_error_details
    )
    
    with pytest.raises(WasenderAPIError) as exc_info:
        await client.send_text(to="invalid_phone", text_body="Test error message")
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.api_message == original_api_message
    assert exc_info.value.error_details == original_error_details 