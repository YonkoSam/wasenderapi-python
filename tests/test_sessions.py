import pytest
from unittest.mock import Mock, patch, AsyncMock
from wasenderapi import WasenderAsyncClient,create_async_wasender
import json
from wasenderapi.models import RateLimitInfo, WasenderSuccessResponse
from wasenderapi.sessions import (
    WhatsAppSessionStatus,
    CreateWhatsAppSessionPayload,
    UpdateWhatsAppSessionPayload,
    ConnectSessionResult,
    GetQRCodeResult,
    DisconnectSessionResult,
    RegenerateApiKeyResult,
    GetSessionStatusResult,
    GetAllWhatsAppSessionsResult,
    GetWhatsAppSessionDetailsResult,
    CreateWhatsAppSessionResult,
    UpdateWhatsAppSessionResult,
    DeleteWhatsAppSessionResult,
    ConnectSessionPayload,
    WhatsAppSession
)
from datetime import datetime, timezone
from wasenderapi.models import RetryConfig
from pydantic import ValidationError

@pytest.fixture
def mock_client_with_async_fetch():
    client = WasenderAsyncClient("test_api_key")
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
        "x-ratelimit-reset": str(int(datetime.now(timezone.utc).timestamp()) + 3600)
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
        "status": "connected"
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
        "phone_number": "+1234567890",
        "status": "connected",
        "account_protection": True,
        "log_messages": True,
        "webhook_url": "https://example.com/webhook",
        "webhook_enabled": True,
        "webhook_events": ["messages.upsert", "status.update"],
        "created_at": "2025-04-01T12:00:00Z",
        "updated_at": "2025-05-08T15:30:00Z"
    }

@pytest.fixture
def mock_rate_limit_info_dict():
    return {
        "limit": 1000,
        "remaining": 999,
        "reset_timestamp": int(datetime.now(timezone.utc).timestamp()) + 3600
    }

@pytest.fixture
def mock_whatsapp_session_api_data():
    return {
            "id": 123,
            "user_id": 456,
            "name": "Test Session",
            "phone_number": "+1234567890",
            "status": "connected",
            "api_key": "test_api_key_123",
            "session_data": {
                "status_updated_at": "2025-01-01T12:00:00+00:00",
                "status_info": {
                    "status": "connected"
                }
            },
            "last_active_at": "2025-01-01T12:00:00Z",
            "created_at": "2025-01-01T12:00:00Z",
            "updated_at": "2025-01-01T12:00:00Z",
            "account_protection": True,
            "log_messages": True,
            "webhook_url": None,
            "webhook_events": [],
            "webhook_enabled": False,
            "webhook_secret": "test_webhook_secret_123"
    }

@pytest.fixture
async def async_client_sessions_mocked_internals():
    retry_config_disabled = RetryConfig(enabled=False)
    client = create_async_wasender(api_key="dummy_api_key_for_pat_tests", personal_access_token="test_pat_123", retry_options=retry_config_disabled)
    client._get_internal = AsyncMock(name="_get_internal")
    client._post_internal = AsyncMock(name="_post_internal")
    client._put_internal = AsyncMock(name="_put_internal")
    client._delete_internal = AsyncMock(name="_delete_internal")
    return client

class TestSessionsClientMethods:
    @pytest.mark.asyncio
    async def test_get_session_status(self, async_client_sessions_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        session_id_str = "session_123"
        mock_api_response_data = {"status": "connected"}
        
        client._get_internal.return_value = {
            "response": mock_api_response_data,
            "rate_limit": mock_rate_limit_info_dict
        }

        result: GetSessionStatusResult = await client.get_session_status(session_id=session_id_str)

        client._get_internal.assert_called_once_with(f"/sessions/{session_id_str}/status", use_personal_token=True)
        assert isinstance(result, GetSessionStatusResult)
        assert result.response.status == WhatsAppSessionStatus.CONNECTED
        assert result.rate_limit is not None

    @pytest.mark.asyncio
    async def test_get_qr_code(self, async_client_sessions_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        session_id_int = 123
        qr_data = {"qr_code": "base64qrdata"}
        mock_api_response_data = {"success": True, "message": "QR Code", "data": qr_data}
        client._get_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: GetQRCodeResult = await client.get_whatsapp_session_qr_code(session_id=session_id_int)

        client._get_internal.assert_called_once_with(f"/whatsapp-sessions/{session_id_int}/qr-code", use_personal_token=True)
        assert isinstance(result, GetQRCodeResult)
        assert result.response.data.qr_code == "base64qrdata"

    @pytest.mark.asyncio
    async def test_disconnect_whatsapp_session(self, async_client_sessions_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        session_id_int = 123
        disconnect_data = {"status": "disconnected", "message": "Session logged out"}
        mock_api_response_data = {"success": True, "message": "Logged out op", "data": disconnect_data}
        client._post_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: DisconnectSessionResult = await client.disconnect_whatsapp_session(session_id=session_id_int)

        client._post_internal.assert_called_once_with(f"/whatsapp-sessions/{session_id_int}/disconnect", None, use_personal_token=True)
        assert isinstance(result, DisconnectSessionResult)
        assert result.response.data.status == WhatsAppSessionStatus.DISCONNECTED

    @pytest.mark.asyncio
    @pytest.mark.parametrize("qr_as_image_param, path_has_query_param", [
        (True, True),
        (False, False),
        (None, False)
    ])
    async def test_connect_whatsapp_session(self, async_client_sessions_mocked_internals, mock_rate_limit_info_dict, qr_as_image_param, path_has_query_param):
        client = async_client_sessions_mocked_internals
        session_id_int = 123
        connect_response_data = {"status": "connected", "message": "Session connected"}
        mock_api_response_data = {"success": True, "message": "Connection status", "data": connect_response_data}
        client._post_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: ConnectSessionResult = await client.connect_whatsapp_session(session_id=session_id_int, qr_as_image=qr_as_image_param)
        
        expected_path_base = f"/whatsapp-sessions/{session_id_int}/connect"
        if path_has_query_param:
            expected_path = f"{expected_path_base}?qrAsImage=true"
        else:
            expected_path = expected_path_base
            
        client._post_internal.assert_called_once_with(expected_path, None, use_personal_token=True)
        assert isinstance(result, ConnectSessionResult)
        assert result.response.data.status == WhatsAppSessionStatus.CONNECTED

    @pytest.mark.asyncio
    async def test_get_all_whatsapp_sessions(self, async_client_sessions_mocked_internals, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        mock_api_response_data = {"success": True, "message": "Sessions list", "data": [mock_whatsapp_session_api_data]}
        client._get_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: GetAllWhatsAppSessionsResult = await client.get_all_whatsapp_sessions()

        client._get_internal.assert_called_once_with("/whatsapp-sessions", use_personal_token=True)
        assert isinstance(result, GetAllWhatsAppSessionsResult)
        assert len(result.response.data) == 1
        assert result.response.data[0].name == mock_whatsapp_session_api_data["name"]

    @pytest.mark.asyncio
    async def test_create_whatsapp_session(self, async_client_sessions_mocked_internals, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        payload_data = {"name": "New Session", "phone_number": "+123", "account_protection": True, "log_messages": True}
        payload_model = CreateWhatsAppSessionPayload(**payload_data)
        mock_api_response_data = {"success": True, "message": "Session created", "data": mock_whatsapp_session_api_data}
        client._post_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: CreateWhatsAppSessionResult = await client.create_whatsapp_session(payload=payload_model)

        client._post_internal.assert_called_once_with("/whatsapp-sessions", payload_model.model_dump(by_alias=True), use_personal_token=True)
        assert isinstance(result, CreateWhatsAppSessionResult)
        assert result.response.data.id == mock_whatsapp_session_api_data["id"]

    @pytest.mark.asyncio
    async def test_get_whatsapp_session_details(self, async_client_sessions_mocked_internals, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        session_id_int = mock_whatsapp_session_api_data["id"]
        mock_api_response_data = {"success": True, "message": "Details", "data": mock_whatsapp_session_api_data}
        client._get_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: GetWhatsAppSessionDetailsResult = await client.get_whatsapp_session_details(session_id=session_id_int)

        client._get_internal.assert_called_once_with(f"/whatsapp-sessions/{session_id_int}", use_personal_token=True)
        assert isinstance(result, GetWhatsAppSessionDetailsResult)
        assert result.response.data.phone_number == mock_whatsapp_session_api_data["phone_number"]

    @pytest.mark.asyncio
    async def test_update_whatsapp_session(self, async_client_sessions_mocked_internals, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        session_id_int = mock_whatsapp_session_api_data["id"]
        update_payload_data = {"name": "Updated Session Name"}
        update_payload_model = UpdateWhatsAppSessionPayload(**update_payload_data)
        updated_session_response_data = {**mock_whatsapp_session_api_data, "name": "Updated Session Name"}
        mock_api_response_data = {"success": True, "message": "Updated", "data": updated_session_response_data}
        client._put_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: UpdateWhatsAppSessionResult = await client.update_whatsapp_session(session_id=session_id_int, payload=update_payload_model)

        client._put_internal.assert_called_once_with(
            f"/whatsapp-sessions/{session_id_int}", 
            update_payload_model.model_dump(by_alias=True, exclude_none=True), 
            use_personal_token=True
        )
        assert isinstance(result, UpdateWhatsAppSessionResult)
        assert result.response.data.name == "Updated Session Name"

    @pytest.mark.asyncio
    async def test_delete_whatsapp_session(self, async_client_sessions_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        session_id_int = 123
        mock_api_response_data = {"success": True, "message": "Session deleted", "data": None}
        client._delete_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: DeleteWhatsAppSessionResult = await client.delete_whatsapp_session(session_id=session_id_int)

        client._delete_internal.assert_called_once_with(f"/whatsapp-sessions/{session_id_int}", use_personal_token=True)
        assert isinstance(result, DeleteWhatsAppSessionResult)
        assert result.response.success is True

    @pytest.mark.asyncio
    async def test_regenerate_api_key(self, async_client_sessions_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_sessions_mocked_internals
        session_id_int = 123
        api_key_data = {"api_key": "new_key_value"}
        client._post_internal.return_value = {"response": api_key_data, "rate_limit": mock_rate_limit_info_dict}

        result: RegenerateApiKeyResult = await client.regenerate_api_key(session_id=session_id_int)

        client._post_internal.assert_called_once_with(f"/whatsapp-sessions/{session_id_int}/regenerate-api-key", None, use_personal_token=True)
        assert isinstance(result, RegenerateApiKeyResult)
        assert result.response.api_key == "new_key_value"

class TestSessionCoreModels:
    def test_whatsapp_session_model(self, mock_whatsapp_session_api_data):
        model = WhatsAppSession(**mock_whatsapp_session_api_data)
        assert model.id == mock_whatsapp_session_api_data["id"]
        assert model.name == mock_whatsapp_session_api_data["name"]
        assert model.phone_number == mock_whatsapp_session_api_data["phone_number"]
        assert model.status == WhatsAppSessionStatus.CONNECTED
        assert model.account_protection is True
        assert model.log_messages is True
        assert model.webhook_url == mock_whatsapp_session_api_data["webhook_url"]
        assert model.webhook_enabled == mock_whatsapp_session_api_data["webhook_enabled"]
        assert model.webhook_events == mock_whatsapp_session_api_data["webhook_events"]
        
        expected_created_at_dt = datetime.fromisoformat(mock_whatsapp_session_api_data["created_at"].replace("Z", "+00:00"))
        expected_updated_at_dt = datetime.fromisoformat(mock_whatsapp_session_api_data["updated_at"].replace("Z", "+00:00"))
        assert model.created_at == expected_created_at_dt
        assert model.updated_at == expected_updated_at_dt

        dumped_model = model.model_dump(by_alias=True, mode='json')
        assert dumped_model["phone_number"] == mock_whatsapp_session_api_data["phone_number"]
        
        assert dumped_model["created_at"] == mock_whatsapp_session_api_data["created_at"]
        assert dumped_model["updated_at"] == mock_whatsapp_session_api_data["updated_at"]

        model_fields = WhatsAppSession.model_fields.keys()

        required_model_fields_for_validation_test = [
            "id", "user_id", "name", "phone_number", "status", "api_key", "session_data",
            "last_active_at", "account_protection", "log_messages", 
            "webhook_enabled", "webhook_secret", "created_at", "updated_at"
        ]

        for field_name_snake_case in required_model_fields_for_validation_test:
            field_info = WhatsAppSession.model_fields[field_name_snake_case]
            api_key_to_omit = field_info.alias or field_name_snake_case

            bad_data = mock_whatsapp_session_api_data.copy()
            if api_key_to_omit in bad_data:
                del bad_data[api_key_to_omit]
            else:
                pass

            with pytest.raises(ValidationError, match=rf"(^|\W){field_name_snake_case}(\W|$)|(^|\W){api_key_to_omit}(\W|$)"):
                 WhatsAppSession(**bad_data)

    def test_whatsapp_session_status_enum(self):
        assert WhatsAppSessionStatus.CONNECTED.value == "connected"
        assert WhatsAppSessionStatus.NEED_SCAN.value == "need_scan"
        with pytest.raises(ValueError):
            WhatsAppSessionStatus("INVALID_STATUS")

class TestSessionRequestPayloadModels:
    def test_create_whatsapp_session_payload(self):
        valid_data_all_fields = {
            "name": "Test Session", "phone_number": "+19998887777",
            "account_protection": False, "log_messages": False,
            "webhook_url": "https://test.com/hook", "webhook_enabled": True,
            "webhook_events": ["messages.upsert", "session.status"]
        }
        model = CreateWhatsAppSessionPayload(**valid_data_all_fields)
        assert model.name == valid_data_all_fields["name"]
        assert model.phone_number == valid_data_all_fields["phone_number"]
        assert model.webhook_events == valid_data_all_fields["webhook_events"]
        dumped = model.model_dump(by_alias=True, exclude_none=True)
        assert dumped["phone_number"] == valid_data_all_fields["phone_number"]
        assert dumped["webhook_url"] == valid_data_all_fields["webhook_url"]

        valid_data_required_only = {
            "name": "Minimal Session", "phone_number": "+12223334444",
            "account_protection": True, "log_messages": True
        }
        model_req = CreateWhatsAppSessionPayload(**valid_data_required_only)
        assert model_req.name == valid_data_required_only["name"]
        assert model_req.webhook_url is None
        dumped_req = model_req.model_dump(by_alias=True, exclude_none=True)
        assert "webhook_url" not in dumped_req
        assert "webhook_events" not in dumped_req

        with pytest.raises(ValidationError):
            CreateWhatsAppSessionPayload(phone_number="+1", account_protection=True, log_messages=True)

    def test_update_whatsapp_session_payload(self):
        payload_all = {
            "name": "Updated Name", "phone_number": "+1newphone",
            "account_protection": True, "log_messages": False,
            "webhook_url": "https://new.hook", "webhook_enabled": False,
            "webhook_events": ["messages.upsert"]
        }
        model_all = UpdateWhatsAppSessionPayload(**payload_all)
        assert model_all.name == payload_all["name"]
        dumped_all = model_all.model_dump(by_alias=True, exclude_none=True)
        assert dumped_all["phone_number"] == payload_all["phone_number"]
        assert dumped_all["webhook_events"] == payload_all["webhook_events"]

        payload_partial = {"name": "Partial Update"}
        model_partial = UpdateWhatsAppSessionPayload(**payload_partial)
        assert model_partial.name == "Partial Update"
        assert model_partial.phone_number is None
        assert model_partial.model_dump(exclude_none=True) == payload_partial

        model_empty = UpdateWhatsAppSessionPayload()
        assert model_empty.model_dump(exclude_none=True) == {}

    def test_connect_session_payload(self):
        model_true = ConnectSessionPayload(qrAsImage=True)
        assert model_true.qr_as_image is True
        assert model_true.model_dump(by_alias=True) == {"qrAsImage": True}

        model_false = ConnectSessionPayload(qrAsImage=False)
        assert model_false.qr_as_image is False
        assert model_false.model_dump(by_alias=True) == {"qrAsImage": False}
        
        model_none = ConnectSessionPayload()
        assert model_none.qr_as_image is None
        assert model_none.model_dump(by_alias=True, exclude_none=True) == {}

class TestSessionResultModels:
    def test_connect_session_result_model(self, mock_rate_limit_info_dict):
        # Case: Need Scan
        need_scan_data = {"status": "need_scan", "qrCode": "base64string", "message": "Scan QR"}
        response_need_scan = {"success": True, "message": "Connect attempt", "data": need_scan_data}
        result_data_need_scan = {"response": response_need_scan, "rate_limit": mock_rate_limit_info_dict}
        model_need_scan = ConnectSessionResult(**result_data_need_scan)
        assert model_need_scan.response.data.status == WhatsAppSessionStatus.NEED_SCAN
        assert model_need_scan.response.data.qr_code == "base64string"
        assert model_need_scan.rate_limit is not None

        # Case: Already Connected
        connected_data = {"status": "connected", "message": "Already connected"}
        response_connected = {"success": True, "message": "Connect attempt", "data": connected_data}
        result_data_connected = {"response": response_connected}
        model_connected = ConnectSessionResult(**result_data_connected)
        assert model_connected.response.data.status == WhatsAppSessionStatus.CONNECTED
        assert model_connected.response.data.qr_code is None
        assert model_connected.rate_limit is None

    def test_qr_code_result_model(self, mock_rate_limit_info_dict):
        qr_data = {"qr_code": "base64qr"}
        response = {"success": True, "message": "QR data", "data": qr_data}
        result_data = {"response": response, "rate_limit": mock_rate_limit_info_dict}
        model = GetQRCodeResult(**result_data)
        assert model.response.data.qr_code == "base64qr"

    def test_disconnect_session_result_model(self, mock_rate_limit_info_dict):
        disconnect_data = {"status": "disconnected", "message": "Logged out"}
        response = {"success": True, "message": "Disconnect op", "data": disconnect_data}
        result_data = {"response": response, "rate_limit": mock_rate_limit_info_dict}
        model = DisconnectSessionResult(**result_data)
        assert model.response.data.status == WhatsAppSessionStatus.DISCONNECTED
        assert model.response.data.message == "Logged out"

    def test_regenerate_api_key_result_model(self, mock_rate_limit_info_dict):
        api_key_data = {"api_key": "newkey123"} # This is the structure of RegenerateApiKeyResponse
        # Note: RegenerateApiKeyResponse itself has success=True and api_key fields.
        # It is not nested under a generic success/message/data structure like others.
        result_data = {"response": api_key_data, "rate_limit": mock_rate_limit_info_dict}
        model = RegenerateApiKeyResult(**result_data)
        assert model.response.success is True
        assert model.response.api_key == "newkey123"

    def test_get_session_status_result_model(self, mock_rate_limit_info_dict):
        status_data = {"status": "connected"} # This is GetSessionStatusResponse structure
        # GetSessionStatusResult directly wraps GetSessionStatusResponse
        result_data = {"response": status_data, "rate_limit": mock_rate_limit_info_dict}
        model = GetSessionStatusResult(**result_data)
        assert model.response.status == WhatsAppSessionStatus.CONNECTED

    def test_get_all_whatsapp_sessions_result(self, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        response_data = {"success": True, "message": "List of sessions", "data": [mock_whatsapp_session_api_data]}
        result_data = {"response": response_data, "rate_limit": mock_rate_limit_info_dict}
        model = GetAllWhatsAppSessionsResult(**result_data)
        assert model.response.success is True
        assert len(model.response.data) == 1
        assert isinstance(model.response.data[0], WhatsAppSession)
        assert model.response.data[0].id == mock_whatsapp_session_api_data["id"]

    def test_get_whatsapp_session_details_result(self, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        response_data = {"success": True, "message": "Session details", "data": mock_whatsapp_session_api_data}
        result_data = {"response": response_data, "rate_limit": mock_rate_limit_info_dict}
        model = GetWhatsAppSessionDetailsResult(**result_data)
        assert isinstance(model.response.data, WhatsAppSession)
        assert model.response.data.name == mock_whatsapp_session_api_data["name"]

    def test_create_whatsapp_session_result(self, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        response_data = {"success": True, "message": "Session created", "data": mock_whatsapp_session_api_data}
        result_data = {"response": response_data, "rate_limit": mock_rate_limit_info_dict}
        model = CreateWhatsAppSessionResult(**result_data)
        assert model.response.data.status == WhatsAppSessionStatus.CONNECTED

    def test_update_whatsapp_session_result(self, mock_whatsapp_session_api_data, mock_rate_limit_info_dict):
        updated_data = {**mock_whatsapp_session_api_data, "name": "Updated Name API"}
        response_data = {"success": True, "message": "Session updated", "data": updated_data}
        result_data = {"response": response_data, "rate_limit": mock_rate_limit_info_dict}
        model = UpdateWhatsAppSessionResult(**result_data)
        assert model.response.data.name == "Updated Name API"

    def test_delete_whatsapp_session_result(self, mock_rate_limit_info_dict):
        # Delete response has data: None
        response_data = {"success": True, "message": "Session deleted", "data": None}
        result_data = {"response": response_data, "rate_limit": mock_rate_limit_info_dict}
        model = DeleteWhatsAppSessionResult(**result_data)
        assert model.response.success is True
        assert model.response.data is None

# ... (TestSessionsClientMethods to be refactored next) ... 
