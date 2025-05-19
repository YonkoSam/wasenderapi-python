import pytest
from unittest.mock import Mock, AsyncMock
from wasenderapi.client import WasenderClient, SDK_VERSION
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import WasenderSuccessResponse, RateLimitInfo, WasenderSendResult
import json

@pytest.fixture
def mock_client():
    client = WasenderClient("test_api_key")
    client._request = AsyncMock()
    return client

@pytest.fixture
def success_api_response_data():
    return {"success": True, "message": "Message sent successfully"}

@pytest.fixture
def rate_limit_headers():
    return {
        "X-RateLimit-Limit": "1000",
        "X-RateLimit-Remaining": "999",
        "X-RateLimit-Reset": "1620000000"
    }

@pytest.fixture
def mock_successful_request_return(success_api_response_data, rate_limit_headers):
    return {
        "response": success_api_response_data,
        "rate_limit": {
            "limit": int(rate_limit_headers["X-RateLimit-Limit"]),
            "remaining": int(rate_limit_headers["X-RateLimit-Remaining"]),
            "reset_timestamp": int(rate_limit_headers["X-RateLimit-Reset"])
        }
    }

@pytest.fixture
def error_api_response_data():
    return {
        "success": False, 
        "message": "Invalid phone number format", 
        "errors": {"to": ["The 'to' field is invalid."]}
    }

@pytest.fixture
def client_with_mocked_fetch():
    mock_fetch = AsyncMock()
    client = WasenderClient("test_api_key", fetch_implementation=mock_fetch)
    return client, mock_fetch

@pytest.mark.asyncio
async def test_sends_text_payload_with_correct_headers(client_with_mocked_fetch):
    client, mock_fetch = client_with_mocked_fetch

    mock_api_response = AsyncMock()
    mock_api_response.status_code = 200
    mock_api_response.ok = True
    mock_api_response.headers = {
        "X-RateLimit-Limit": "1000",
        "X-RateLimit-Remaining": "999",
        "X-RateLimit-Reset": "1620000000"
    }
    success_payload = {"success": True, "message": "ok"}
    mock_api_response.json = AsyncMock(return_value=success_payload)
    mock_api_response.text = json.dumps(success_payload)

    mock_fetch.return_value = mock_api_response

    payload_to_send = {"to": "+123", "text": "yo"}
    response: WasenderSendResult = await client.send_text(payload_to_send)

    mock_fetch.assert_called_once()
    
    called_url, called_options_dict = mock_fetch.call_args.args

    assert called_options_dict.get('method') == "POST"
    assert called_url == "https://www.wasenderapi.com/api/send-message"
    
    expected_headers = {
        "Accept": "application/json",
        "User-Agent": f"wasenderapi-python-sdk/{SDK_VERSION}",
        "Authorization": "Bearer test_api_key",
        "Content-Type": "application/json"
    }
    assert called_options_dict.get('headers') == expected_headers

    expected_body = {"to": "+123", "text": "yo", "messageType": "text"}
    assert called_options_dict.get('json') == expected_body
    
    assert response.response.success == True
    assert response.response.message == "ok"
    assert response.rate_limit.limit == 1000
    assert response.rate_limit.remaining == 999

@pytest.mark.asyncio
async def test_send_image(mock_client, mock_successful_request_return, success_api_response_data):
    mock_client._request.return_value = mock_successful_request_return
    
    payload = {"to": "1234567890", "imageUrl": "https://example.com/image.jpg", "text": "Test image"}
    response = await mock_client.send_image(payload)
        
    mock_client._request.assert_called_once_with(
        "POST", 
        "/send-message", 
        body={"to": "1234567890", "imageUrl": "https://example.com/image.jpg", "text": "Test image", "messageType": "image"}, 
        use_personal_token=False
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]
    assert response.rate_limit.limit == 1000

@pytest.mark.asyncio
async def test_send_video(mock_client, mock_successful_request_return, success_api_response_data):
    mock_client._request.return_value = mock_successful_request_return
    
    payload = {"to": "1234567890", "videoUrl": "https://example.com/video.mp4", "text": "Test video"}
    response = await mock_client.send_video(payload)
            
    mock_client._request.assert_called_once_with(
        "POST", 
        "/send-message", 
        body={"to": "1234567890", "videoUrl": "https://example.com/video.mp4", "text": "Test video", "messageType": "video"}, 
        use_personal_token=False
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]

@pytest.mark.asyncio
async def test_send_document(mock_client, mock_successful_request_return, success_api_response_data):
    mock_client._request.return_value = mock_successful_request_return
    
    payload = {"to": "1234567890", "documentUrl": "https://example.com/doc.pdf", "text": "Test document"}
    response = await mock_client.send_document(payload)
    
    mock_client._request.assert_called_once_with(
        "POST", 
        "/send-message", 
        body={"to": "1234567890", "documentUrl": "https://example.com/doc.pdf", "text": "Test document", "messageType": "document"}, 
        use_personal_token=False
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]

@pytest.mark.asyncio
async def test_send_audio(mock_client, mock_successful_request_return, success_api_response_data):
    mock_client._request.return_value = mock_successful_request_return
    
    payload = {"to": "1234567890", "audioUrl": "https://example.com/audio.mp3"}
    response = await mock_client.send_audio(payload)
    
    mock_client._request.assert_called_once_with(
        "POST", 
        "/send-message", 
        body={"to": "1234567890", "audioUrl": "https://example.com/audio.mp3", "messageType": "audio"}, 
        use_personal_token=False
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]

@pytest.mark.asyncio
async def test_send_location(mock_client, mock_successful_request_return, success_api_response_data):
    mock_client._request.return_value = mock_successful_request_return
    
    payload = {"to": "1234567890", "location": {"latitude": 37.7749, "longitude": -122.4194, "name": "San Francisco"}}
    response = await mock_client.send_location(payload)
        
    mock_client._request.assert_called_once_with(
        "POST", 
        "/send-message", 
        body={"to": "1234567890", "location": {"latitude": 37.7749, "longitude": -122.4194, "name": "San Francisco"}, "messageType": "location"}, 
        use_personal_token=False
    )
    assert response.response.success == True
    assert response.response.message == success_api_response_data["message"]

@pytest.mark.asyncio
async def test_api_error_raised(mock_client, error_api_response_data):
    mock_client._request.side_effect = WasenderAPIError(
        message=error_api_response_data["message"],
        status_code=400,
        api_message=error_api_response_data["message"],
        error_details=error_api_response_data["errors"],
        rate_limit=None,
        retry_after=None
    )
    
    with pytest.raises(WasenderAPIError) as exc_info:
        await mock_client.send_text({"to": "invalid", "text": "Test message"})
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.api_message == error_api_response_data["message"]
    assert exc_info.value.error_details == error_api_response_data["errors"] 