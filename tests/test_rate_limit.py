import pytest
from unittest.mock import AsyncMock, patch, Mock, MagicMock, call
import time
import asyncio
from wasenderapi import create_async_wasender, create_sync_wasender
from wasenderapi.models import RetryConfig, WasenderSendResult
from wasenderapi.errors import WasenderAPIError
import requests


@pytest.fixture
def sync_client_with_retry_enabled():
    """Sync client with retries enabled for testing"""
    retry_config = RetryConfig(enabled=True, max_retries=3)
    client = create_sync_wasender("test_api_key", retry_options=retry_config)
    return client


@pytest.fixture
def sync_client_with_retry_disabled():
    """Sync client with retries disabled for testing"""
    retry_config = RetryConfig(enabled=False)
    client = create_sync_wasender("test_api_key", retry_options=retry_config)
    return client


@pytest.fixture
def async_client_with_retry_enabled():
    """Async client with retries enabled for testing"""
    retry_config = RetryConfig(enabled=True, max_retries=3)
    client = create_async_wasender("test_api_key", retry_options=retry_config)
    return client


@pytest.fixture
def async_client_with_retry_disabled():
    """Async client with retries disabled for testing"""
    retry_config = RetryConfig(enabled=False)
    client = create_async_wasender("test_api_key", retry_options=retry_config)
    return client


# Sync Client Rate Limit Tests
@patch('time.sleep')
@patch('requests.request')
def test_sync_rate_limit_uses_retry_after_from_response(mock_request, mock_sleep, sync_client_with_retry_enabled):
    """Test that sync client uses retry_after value from API response when rate limited"""
    client = sync_client_with_retry_enabled
    
    # Mock first request (rate limited) and second request (success)
    rate_limit_response = Mock()
    rate_limit_response.ok = False
    rate_limit_response.status_code = 429
    rate_limit_response.json.return_value = {
        "success": False,
        "message": "Rate limit exceeded",
        "retry_after": 5  # API says to wait 5 seconds
    }
    rate_limit_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1620000000"
    }
    
    success_response = Mock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.json.return_value = {
        "success": True,
        "message": "Message sent successfully",
        "data": {"messageId": "test-message-id"}
    }
    success_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "99",
        "X-RateLimit-Reset": "1620000000"
    }
    
    # First call returns rate limit, second call succeeds
    mock_request.side_effect = [rate_limit_response, success_response]
    
    # Make the request
    response = client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify that sleep was called with the retry_after value from the response
    mock_sleep.assert_called_once_with(5)
    
    # Verify that we got a successful response
    assert response.response.success is True
    assert response.response.data.message_id == "test-message-id"
    
    # Verify that requests.request was called twice (first rate limited, then success)
    assert mock_request.call_count == 2


@patch('time.sleep')
@patch('requests.request')
def test_sync_rate_limit_uses_default_sleep_when_no_retry_after(mock_request, mock_sleep, sync_client_with_retry_enabled):
    """Test that sync client uses default 1-second sleep when retry_after is not provided"""
    client = sync_client_with_retry_enabled
    
    # Mock first request (rate limited without retry_after) and second request (success)
    rate_limit_response = Mock()
    rate_limit_response.ok = False
    rate_limit_response.status_code = 429
    rate_limit_response.json.return_value = {
        "success": False,
        "message": "Rate limit exceeded"
        # No retry_after field
    }
    rate_limit_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1620000000"
    }
    
    success_response = Mock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.json.return_value = {
        "success": True,
        "message": "Message sent successfully",
        "data": {"messageId": "test-message-id"}
    }
    success_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "99",
        "X-RateLimit-Reset": "1620000000"
    }
    
    mock_request.side_effect = [rate_limit_response, success_response]
    
    # Make the request
    response = client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify that sleep was called with default 1 second since no retry_after was provided
    mock_sleep.assert_called_once_with(1)
    
    # Verify that we got a successful response
    assert response.response.success is True
    assert response.response.data.message_id == "test-message-id"
    
    assert mock_request.call_count == 2


@patch('time.sleep')
@patch('requests.request')
def test_sync_rate_limit_disabled_retries_raises_immediately(mock_request, mock_sleep, sync_client_with_retry_disabled):
    """Test that sync client raises immediately when retries are disabled"""
    client = sync_client_with_retry_disabled
    
    # Mock rate limit response
    rate_limit_response = Mock()
    rate_limit_response.ok = False
    rate_limit_response.status_code = 429
    rate_limit_response.json.return_value = {
        "success": False,
        "message": "Rate limit exceeded",
        "retry_after": 5
    }
    rate_limit_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1620000000"
    }
    
    mock_request.return_value = rate_limit_response
    
    # Should raise immediately without retrying since retries are disabled
    with pytest.raises(WasenderAPIError) as exc_info:
        client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify error details
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 5
    
    # Should not have slept since retries are disabled
    mock_sleep.assert_not_called()
    
    # Should only have made one request
    assert mock_request.call_count == 1


@patch('time.sleep')
@patch('requests.request')
def test_sync_rate_limit_max_retries_exhausted(mock_request, mock_sleep, sync_client_with_retry_enabled):
    """Test that sync client raises error when max retries are exhausted"""
    client = sync_client_with_retry_enabled
    
    # Mock rate limit response for all attempts
    rate_limit_response = Mock()
    rate_limit_response.ok = False
    rate_limit_response.status_code = 429
    rate_limit_response.json.return_value = {
        "success": False,
        "message": "Rate limit exceeded",
        "retry_after": 2
    }
    rate_limit_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1620000000"
    }
    
    mock_request.return_value = rate_limit_response
    
    # Should raise after exhausting retries
    with pytest.raises(WasenderAPIError) as exc_info:
        client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify error details
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 2
    
    # Should have slept 3 times (max_retries=3)
    assert mock_sleep.call_count == 3
    mock_sleep.assert_called_with(2)
    
    # Should have made 4 requests (initial + 3 retries)
    assert mock_request.call_count == 4


# Async Client Rate Limit Tests
@pytest.mark.asyncio
@patch('asyncio.sleep')
async def test_async_rate_limit_uses_retry_after_from_response(mock_sleep, async_client_with_retry_enabled):
    """Test that async client uses retry_after value from API response when rate limited"""
    client = async_client_with_retry_enabled
    
    # Mock the HTTP client to simulate rate limit then success
    mock_http_client = AsyncMock()
    
    # First request: rate limited with retry_after=3 in response body
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.is_success = False
    rate_limit_response.headers = {}
    rate_limit_response.json.return_value = {
        "message": "Rate limit exceeded",
        "retry_after": 3
    }
    
    # Second request: success
    success_response = Mock()
    success_response.status_code = 200
    success_response.is_success = True
    success_response.headers = {
        'X-RateLimit-Limit': '100',
        'X-RateLimit-Remaining': '99',
        'X-RateLimit-Reset': '1620000000'
    }
    success_response.json.return_value = {
        "success": True,
        "message": "Message sent successfully",
        "data": {"messageId": "test-message-id"}
    }
    
    # Configure the mock to return rate limit first, then success
    mock_http_client.request = AsyncMock(side_effect=[rate_limit_response, success_response])
    client._http_client = mock_http_client
    
    # Make the request
    response = await client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify that asyncio.sleep was called with the retry_after value
    mock_sleep.assert_called_once_with(3)
    
    # Verify that we got a successful response
    assert response.response.success is True
    assert response.response.data.message_id == "test-message-id"
    
    # Verify that HTTP client was called twice
    assert mock_http_client.request.call_count == 2


@pytest.mark.asyncio
@patch('asyncio.sleep')
async def test_async_rate_limit_uses_default_sleep_when_no_retry_after(mock_sleep, async_client_with_retry_enabled):
    """Test that async client uses default 1-second sleep when retry_after is not provided"""
    client = async_client_with_retry_enabled
    
    # Mock the HTTP client to simulate rate limit then success
    mock_http_client = AsyncMock()
    
    # First request: rate limited without retry_after
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.is_success = False
    rate_limit_response.headers = {}
    rate_limit_response.json.return_value = {
        "message": "Rate limit exceeded"
        # No retry_after field
    }
    
    # Second request: success
    success_response = Mock()
    success_response.status_code = 200
    success_response.is_success = True
    success_response.headers = {
        'X-RateLimit-Limit': '100',
        'X-RateLimit-Remaining': '99',
        'X-RateLimit-Reset': '1620000000'
    }
    success_response.json.return_value = {
        "success": True,
        "message": "Message sent successfully",
        "data": {"messageId": "test-message-id"}
    }
    
    # Configure the mock to return rate limit first, then success
    mock_http_client.request = AsyncMock(side_effect=[rate_limit_response, success_response])
    client._http_client = mock_http_client
    
    # Make the request
    response = await client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify that asyncio.sleep was called with default 1 second
    mock_sleep.assert_called_once_with(1)
    
    # Verify that we got a successful response
    assert response.response.success is True
    assert response.response.data.message_id == "test-message-id"
      # Verify that HTTP client was called twice
    assert mock_http_client.request.call_count == 2


@pytest.mark.asyncio
@patch('asyncio.sleep')
async def test_async_rate_limit_disabled_retries_raises_immediately(mock_sleep, async_client_with_retry_disabled):
    """Test that async client raises immediately when retries are disabled"""
    client = async_client_with_retry_disabled
    
    # Mock the HTTP client to always return rate limit error
    mock_http_client = AsyncMock()
    
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.is_success = False
    rate_limit_response.headers = {}
    rate_limit_response.json.return_value = {
        "message": "Rate limit exceeded",
        "retry_after": 5
    }
    
    mock_http_client.request = AsyncMock(return_value=rate_limit_response)
    client._http_client = mock_http_client
    
    # Should raise immediately without retrying since retries are disabled
    with pytest.raises(WasenderAPIError) as exc_info:
        await client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify error details
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 5
    
    # Should not have slept since retries are disabled
    mock_sleep.assert_not_called()


@pytest.mark.asyncio
@patch('asyncio.sleep')
async def test_async_rate_limit_max_retries_exhausted(mock_sleep, async_client_with_retry_enabled):
    """Test that async client raises error when max retries are exhausted"""
    client = async_client_with_retry_enabled
    
    # Mock the HTTP client to always return rate limit error
    mock_http_client = AsyncMock()
    
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.is_success = False
    rate_limit_response.headers = {}
    rate_limit_response.json.return_value = {
        "message": "Rate limit exceeded",
        "retry_after": 1
    }
    
    mock_http_client.request = AsyncMock(return_value=rate_limit_response)
    client._http_client = mock_http_client
    
    # Should raise after exhausting retries
    with pytest.raises(WasenderAPIError) as exc_info:
        await client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify error details
    assert exc_info.value.status_code == 429
    assert exc_info.value.retry_after == 1
    
    # Should have slept 3 times (max_retries=3)
    assert mock_sleep.call_count == 3
    mock_sleep.assert_has_calls([call(1), call(1), call(1)])


@pytest.mark.asyncio
@patch('asyncio.sleep')
async def test_async_rate_limit_retry_after_zero_uses_default(mock_sleep, async_client_with_retry_enabled):
    """Test that async client uses default sleep when retry_after is 0"""
    client = async_client_with_retry_enabled
    
    # Mock the HTTP client to simulate rate limit then success
    mock_http_client = AsyncMock()
    
    # First request: rate limited with retry_after=0
    rate_limit_response = Mock()
    rate_limit_response.status_code = 429
    rate_limit_response.is_success = False
    rate_limit_response.headers = {}
    rate_limit_response.json.return_value = {
        "message": "Rate limit exceeded",
        "retry_after": 0  # API says retry_after is 0
    }
    
    # Second request: success
    success_response = Mock()
    success_response.status_code = 200
    success_response.is_success = True
    success_response.headers = {
        'X-RateLimit-Limit': '100',
        'X-RateLimit-Remaining': '99',
        'X-RateLimit-Reset': '1620000000'
    }
    success_response.json.return_value = {
        "success": True,
        "message": "Message sent successfully",
        "data": {"messageId": "test-message-id"}
    }
    
    # Configure the mock to return rate limit first, then success
    mock_http_client.request = AsyncMock(side_effect=[rate_limit_response, success_response])
    client._http_client = mock_http_client
    
    # Make the request
    response = await client.send_text(to="+1234567890", text_body="Test message")
    
    # Verify that asyncio.sleep was called with default 1 second since retry_after was 0
    mock_sleep.assert_called_once_with(1)
    
    # Verify that we got a successful response
    assert response.response.success is True
    assert response.response.data.message_id == "test-message-id"
      # Verify that HTTP client was called twice
    assert mock_http_client.request.call_count == 2


@patch('time.sleep')
@patch('requests.request')
def test_sync_rate_limit_retry_after_zero_uses_default(mock_request, mock_sleep, sync_client_with_retry_enabled):
    """Test that sync client uses default sleep when retry_after is 0"""
    client = sync_client_with_retry_enabled
    
    # Mock first request (rate limited with retry_after=0) and second request (success)
    rate_limit_response = Mock()
    rate_limit_response.ok = False
    rate_limit_response.status_code = 429
    rate_limit_response.json.return_value = {
        "success": False,
        "message": "Rate limit exceeded",
        "retry_after": 0  # API says retry_after is 0
    }
    rate_limit_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": "1620000000"
    }
    
    success_response = Mock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.json.return_value = {
        "success": True,
        "message": "Message sent successfully",
        "data": {"messageId": "test-message-id"}
    }
    success_response.headers = {
        "X-RateLimit-Limit": "100",
        "X-RateLimit-Remaining": "99",
        "X-RateLimit-Reset": "1620000000"
    }
    
    mock_request.side_effect = [rate_limit_response, success_response]
    
    # Make the request
    response = client.send_text(to="+1234567890", text_body="Test message")
      # Verify that sleep was called with default 1 second since retry_after=0
    mock_sleep.assert_called_once_with(1)
    
    # Verify that we got a successful response
    assert response.response.success is True
    assert response.response.data.message_id == "test-message-id"
    
    assert mock_request.call_count == 2
