import pytest
from unittest.mock import Mock, patch, AsyncMock
from wasenderapi.client import WasenderClient
import json
from wasenderapi.models import RateLimitInfo, WasenderSuccessResponse
from wasenderapi.sessions import (
    WhatsAppSessionStatus,
    CreateWhatsAppSessionPayload,
    UpdateWhatsAppSessionPayload
)
from datetime import datetime

@pytest.fixture
def mock_client_with_async_fetch():
    client = WasenderClient("test_api_key")
    client.fetch_impl = AsyncMock()
    return client

@pytest.fixture
def mock_success_response_content():
    return {
        "success": True,
        "message": "Operation successful"
    }

@pytest.fixture
def mock_rate_limit_headers():
    return {
        "x-ratelimit-limit": "1000",
        "x-ratelimit-remaining": "999",
        "x-ratelimit-reset": str(int(datetime.now().timestamp()) + 3600)
    }

@pytest.fixture
def mock_api_response(mock_success_response_content, mock_rate_limit_headers):
    response_mock = AsyncMock()
    response_mock.status_code = 200
    response_mock.ok = True
    response_mock.headers = mock_rate_limit_headers
    
    async def json_func(): 
        return mock_success_response_content
    response_mock.json = json_func
    return response_mock

@pytest.fixture
def mock_session_status_response_data():
    return {
        "status": "CONNECTED"
    }

@pytest.fixture
def mock_qr_code_response_data():
    return {
        "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    }

@pytest.fixture
def mock_whatsapp_session_data():
    return {
        "id": 1,
        "name": "Business WhatsApp",
        "phoneNumber": "+1234567890",
        "status": "CONNECTED",
        "accountProtection": True,
        "logMessages": True,
        "webhookUrl": "https://example.com/webhook",
        "webhookEnabled": True,
        "webhookEvents": ["message", "group_update"],
        "createdAt": "2025-04-01T12:00:00Z",
        "updatedAt": "2025-05-08T15:30:00Z"
    }

@pytest.fixture
def mock_rate_limit_info_fixture():
    return {
        "limit": 100,
        "remaining": 99,
        "reset_timestamp": int(datetime.now().timestamp()) + 3600
    }

class TestSessionsClientMethods:

    @pytest.mark.asyncio
    async def test_get_session_status(self, mock_client_with_async_fetch, mock_api_response, mock_session_status_response_data):
        mock_api_response.json = AsyncMock(return_value=mock_session_status_response_data)
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response
        
        session_id = "session_123"
        result = await mock_client_with_async_fetch.get_session_status(session_id)
        
        mock_client_with_async_fetch.fetch_impl.assert_called_once_with(
            f'{mock_client_with_async_fetch.base_url}/sessions/{session_id}/status',
            {'method': 'GET', 'headers': {'Accept': 'application/json', 'User-Agent': 'wasenderapi-python-sdk/0.1.0', 'Authorization': 'Bearer test_api_key'}, 'url': f'{mock_client_with_async_fetch.base_url}/sessions/{session_id}/status'}
        )
        assert result.response.status == WhatsAppSessionStatus.CONNECTED
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_get_qr_code(self, mock_client_with_async_fetch, mock_api_response, mock_qr_code_response_data):
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "QR Code retrieved", "data": mock_qr_code_response_data})
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response
        
        session_id = 123
        result = await mock_client_with_async_fetch.get_whatsapp_session_qr_code(session_id)
        
        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success == True
        assert result.response.data.qr_code == mock_qr_code_response_data["qrCode"]
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_logout_session(self, mock_client_with_async_fetch, mock_api_response):
        logout_response_data_inner = {"status": WhatsAppSessionStatus.DISCONNECTED.value, "message": "Session logged out successfully from inner"}
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "Session logged out", "data": logout_response_data_inner})
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response
        
        session_id = 123
        result = await mock_client_with_async_fetch.disconnect_whatsapp_session(session_id)
        
        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success == True
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_connect_whatsapp_session(self, mock_client_with_async_fetch, mock_api_response):
        session_id = 123
        connect_response_data = {"status": WhatsAppSessionStatus.CONNECTED.value, "message": "Session connected"}
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "Connection status", "data": connect_response_data})
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response

        result = await mock_client_with_async_fetch.connect_whatsapp_session(session_id)

        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success is True
        assert result.response.data.status == WhatsAppSessionStatus.CONNECTED
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_get_all_whatsapp_sessions(self, mock_client_with_async_fetch, mock_api_response, mock_whatsapp_session_data):
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "Sessions listed", "data": [mock_whatsapp_session_data]})
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response

        result = await mock_client_with_async_fetch.get_all_whatsapp_sessions()

        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success is True
        assert len(result.response.data) == 1
        assert result.response.data[0].name == "Business WhatsApp"
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_create_whatsapp_session(self, mock_client_with_async_fetch, mock_api_response, mock_whatsapp_session_data):
        payload_data = {
            "name": "New Session", 
            "phoneNumber": "+123", 
            "accountProtection": True,
            "logMessages": True
        }
        payload_model = CreateWhatsAppSessionPayload(**payload_data)
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "Session created", "data": mock_whatsapp_session_data})
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response

        result = await mock_client_with_async_fetch.create_whatsapp_session(payload_model)
        
        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success is True
        assert result.response.data.name == "Business WhatsApp"
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_get_whatsapp_session_details(self, mock_client_with_async_fetch, mock_api_response, mock_whatsapp_session_data):
        session_id = mock_whatsapp_session_data["id"]
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "Details retrieved", "data": mock_whatsapp_session_data})
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response

        result = await mock_client_with_async_fetch.get_whatsapp_session_details(session_id)

        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success is True
        assert result.response.data.id == session_id
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_update_whatsapp_session(self, mock_client_with_async_fetch, mock_api_response, mock_whatsapp_session_data):
        session_id = mock_whatsapp_session_data["id"]
        update_payload_data = {"name": "Updated Session Name"}
        update_payload_model = UpdateWhatsAppSessionPayload(**update_payload_data)
        updated_session_data = {**mock_whatsapp_session_data, "name": "Updated Session Name"}
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "Session updated", "data": updated_session_data})
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response

        result = await mock_client_with_async_fetch.update_whatsapp_session(session_id, update_payload_model)

        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success is True
        assert result.response.data.name == "Updated Session Name"
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_delete_whatsapp_session(self, mock_client_with_async_fetch, mock_api_response):
        session_id = 123
        mock_api_response.json = AsyncMock(return_value={"success": True, "message": "Session deleted", "data": None})
        mock_api_response.status_code = 200
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response

        result = await mock_client_with_async_fetch.delete_whatsapp_session(session_id)

        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success is True
        assert result.rate_limit is None

    @pytest.mark.asyncio
    async def test_regenerate_api_key_for_session(self, mock_client_with_async_fetch, mock_api_response):
        session_id = 123
        api_key_data = {"apiKey": "new_regenerated_key"}
        mock_api_response.json = AsyncMock(return_value=api_key_data)
        mock_client_with_async_fetch.fetch_impl.return_value = mock_api_response

        result = await mock_client_with_async_fetch.regenerate_api_key(session_id)

        mock_client_with_async_fetch.fetch_impl.assert_called_once()
        assert result.response.success is True
        assert result.response.api_key == "new_regenerated_key"
        assert result.rate_limit is None

class TestSessionTypeDefinitions:
    class TestCoreDataStructures:
        def test_whatsapp_session_type_should_be_correct(self, mock_whatsapp_session_data):
            session = {**mock_whatsapp_session_data}
            assert session["id"] == 1
            assert session["name"] == "Business WhatsApp"
            assert session["status"] == WhatsAppSessionStatus.CONNECTED.value
            assert session["webhookEvents"] == ["message", "group_update"]

        def test_whatsapp_session_status_type_should_allow_valid_statuses(self):
            status1 = WhatsAppSessionStatus.CONNECTED
            status2 = WhatsAppSessionStatus.NEED_SCAN
            assert status1.value == "CONNECTED"
            assert status2.value == "NEED_SCAN"

    class TestAPIRequestPayloads:
        def test_create_whatsapp_session_payload_type_should_be_correct_all_fields(self):
            payload = {
                "name": "Test Session",
                "phone_number": "+19998887777",
                "account_protection": False,
                "log_messages": False,
                "webhook_url": "https://test.com/hook",
                "webhook_enabled": True,
                "webhook_events": ["messages.upsert"]
            }
            assert payload["name"] == "Test Session"
            assert payload["webhook_events"] == ["messages.upsert"]

        def test_create_whatsapp_session_payload_type_should_be_correct_required_fields_only(self):
            payload = {
                "name": "Minimal Session",
                "phone_number": "+12223334444",
                "account_protection": True,
                "log_messages": True
            }
            assert payload["name"] == "Minimal Session"
            assert "webhook_url" not in payload

        def test_update_whatsapp_session_payload_type_should_allow_partial_updates(self):
            payload1 = {"name": "Updated Name"}
            payload2 = {"webhook_enabled": False, "webhook_events": []}
            payload3 = {}
            assert payload1["name"] == "Updated Name"
            assert payload2["webhook_events"] == []
            assert "name" not in payload3

        def test_connect_session_payload_type_should_be_correct(self):
            payload1 = {"qr_as_image": True}
            payload2 = {"qr_as_image": False}
            payload3 = {}
            assert payload1["qr_as_image"] == True
            assert payload2["qr_as_image"] == False
            assert "qr_as_image" not in payload3

    class TestAPIResponseDataStructures:
        def test_connect_session_response_data_type_should_be_correct_need_scan(self):
            data = {
                "status": WhatsAppSessionStatus.NEED_SCAN.value,
                "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACA..."
            }
            assert data["status"] == WhatsAppSessionStatus.NEED_SCAN.value
            assert data["qrCode"] == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACA..."

        def test_connect_session_response_data_type_should_be_correct_connected(self):
            data = {
                "status": WhatsAppSessionStatus.CONNECTED.value,
                "message": "Session already connected"
            }
            assert data["status"] == WhatsAppSessionStatus.CONNECTED.value
            assert data["message"] == "Session already connected"
            assert "qrCode" not in data

        def test_qr_code_response_data_type_should_be_correct(self, mock_qr_code_response_data):
            data = {**mock_qr_code_response_data}
            assert data["qrCode"] == "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."

        def test_disconnect_session_response_data_type_should_be_correct(self):
            data = {
                "status": WhatsAppSessionStatus.DISCONNECTED.value,
                "message": "WhatsApp session disconnected successfully",
            }
            assert data["status"] == WhatsAppSessionStatus.DISCONNECTED.value
            assert data["message"] == "WhatsApp session disconnected successfully"
        
        def test_regenerate_api_key_response_type_should_be_correct(self):
            data = {
                "api_key": "new_whatsapp_api_key_abc456"
            }
            assert data["api_key"] == "new_whatsapp_api_key_abc456"

        def test_session_status_data_type_should_be_correct(self, mock_session_status_response_data):
            data = {**mock_session_status_response_data}
            assert data["status"] == WhatsAppSessionStatus.CONNECTED.value

    class TestAPISuccessResponseTypes:
        def test_get_all_whatsapp_sessions_response_type_should_be_correct(self, mock_whatsapp_session_data):
            response = {
                "success": True,
                "message": "Sessions retrieved successfully",
                "data": [mock_whatsapp_session_data, {**mock_whatsapp_session_data, "id": 2, "name": "Support WhatsApp", "status": WhatsAppSessionStatus.DISCONNECTED.value}]
            }
            assert response["success"] is True
            assert response["message"] == "Sessions retrieved successfully"
            assert len(response["data"]) == 2
            assert response["data"][0]["id"] == 1
            assert response["data"][1]["status"] == WhatsAppSessionStatus.DISCONNECTED.value

        def test_get_whatsapp_session_details_response_type_should_be_correct(self, mock_whatsapp_session_data):
            response = {
                "success": True,
                "message": "Session details retrieved",
                "data": mock_whatsapp_session_data
            }
            assert response["success"] is True
            assert response["message"] == "Session details retrieved"
            assert response["data"]["name"] == "Business WhatsApp"

        def test_create_whatsapp_session_response_type_should_be_correct(self, mock_whatsapp_session_data):
            response = {
                "success": True,
                "message": "Session created successfully",
                "data": mock_whatsapp_session_data
            }
            assert response["success"] is True
            assert response["data"]["status"] == WhatsAppSessionStatus.CONNECTED.value

        def test_get_session_status_response_type_should_be_correct(self, mock_session_status_response_data):
            response = {
                "success": True,
                "message": "Status retrieved",
                "data": mock_session_status_response_data
            }
            assert response["success"] is True
            assert response["data"]["status"] == WhatsAppSessionStatus.CONNECTED.value

    class TestResultTypes:
        def test_get_session_status_result_type_should_be_correct(self, mock_session_status_response_data, mock_rate_limit_info_fixture):
            result = {
                "response": {"success": True, "data": mock_session_status_response_data, "message": "Status ok"},
                "rate_limit": mock_rate_limit_info_fixture
            }
            assert result["response"]["data"]["status"] == WhatsAppSessionStatus.CONNECTED.value
            assert result["rate_limit"]["limit"] == 100

        def test_get_all_whatsapp_sessions_result_type_should_be_correct(self, mock_whatsapp_session_data, mock_rate_limit_info_fixture):
            result = {
                "response": {"success": True, "data": [mock_whatsapp_session_data], "message": "Sessions list"},
                "rate_limit": mock_rate_limit_info_fixture
            }
            assert len(result["response"]["data"]) == 1
            assert result["rate_limit"]["remaining"] == 99
            
        def test_create_whatsapp_session_result_type_should_be_correct(self, mock_whatsapp_session_data, mock_rate_limit_info_fixture):
            result = {
                "response": {"success": True, "data": mock_whatsapp_session_data, "message": "Created"},
                "rate_limit": mock_rate_limit_info_fixture
            }
            assert result["response"]["data"]["name"] == "Business WhatsApp"
            assert isinstance(datetime.fromtimestamp(result["rate_limit"]["reset_timestamp"]), datetime) 