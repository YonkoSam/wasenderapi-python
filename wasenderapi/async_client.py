import json
import time
import asyncio # Added for async operations
from typing import Optional, Dict, Any, Union, List, TypeVar, Generic, Callable
import httpx # Added for async HTTP requests
from urllib.parse import urlencode
from ._version import __version__ as SDK_VERSION # Import from _version.py
from .models import (
    BaseMessage,
    WasenderSuccessResponse,
    RateLimitInfo,
    WasenderSendResult,
    RetryConfig
)
from .errors import WasenderAPIError
from .webhook import (
    WEBHOOK_SIGNATURE_HEADER,
    verify_wasender_webhook_signature,
    WasenderWebhookEvent
)
from .contacts import (
    GetAllContactsResult,
    GetContactInfoResult,
    GetContactProfilePictureResult,
    ContactActionResult
)
from .groups import (
    GetAllGroupsResult,
    GetGroupMetadataResult,
    GetGroupParticipantsResult,
    ModifyGroupParticipantsResult,
    ModifyGroupParticipantsPayload,
    UpdateGroupSettingsPayload,
    UpdateGroupSettingsResult
)
from .sessions import (
    CreateWhatsAppSessionPayload,
    UpdateWhatsAppSessionPayload,
    GetAllWhatsAppSessionsResult,
    GetWhatsAppSessionDetailsResult,
    CreateWhatsAppSessionResult,
    UpdateWhatsAppSessionResult,
    DeleteWhatsAppSessionResult,
    ConnectSessionResult,
    GetQRCodeResult,
    DisconnectSessionResult,
    RegenerateApiKeyResult,
    GetSessionStatusResult
)
from pydantic import TypeAdapter

class WebhookRequestAdapter:
    def __init__(self, headers: Dict[str, str], body: str):
        self.headers = headers
        self.body = body

    def get_header(self, name: str) -> Optional[str]:
        return self.headers.get(name.lower())

    def get_raw_body(self) -> str:
        return self.body

class WasenderAsyncClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.wasenderapi.com/api",
        retry_options: Optional[RetryConfig] = None,
        webhook_secret: Optional[str] = None,
        personal_access_token: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None # Added for custom async client
    ):
        if not api_key:
            raise ValueError("WASENDER_API_KEY is required to initialize the Wasender SDK.")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.retry_config = retry_options if retry_options is not None else RetryConfig()
        self.webhook_secret = webhook_secret
        self.personal_access_token = personal_access_token
        self._http_client = http_client
        self._created_http_client = False

    async def __aenter__(self):
        if self._http_client is None:
            self._http_client = httpx.AsyncClient()
            self._created_http_client = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._created_http_client and self._http_client:
            await self._http_client.aclose()

    @property
    def http_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            # This case should ideally be handled by __aenter__ if used as a context manager
            # Or the user should provide a client instance or manage its lifecycle.
            # For direct instantiation without 'async with', we create one but it won't be closed automatically.
            # Consider warning the user or requiring 'async with' for proper resource management.
            self._http_client = httpx.AsyncClient()
            self._created_http_client = True # Mark as created so it can be closed if __aexit__ is somehow called
        return self._http_client

    def _parse_rate_limit_headers(self, headers: httpx.Headers) -> RateLimitInfo:
        limit = headers.get("X-RateLimit-Limit")
        remaining = headers.get("X-RateLimit-Remaining")
        reset = headers.get("X-RateLimit-Reset")

        reset_timestamp = int(reset) if reset else None

        return RateLimitInfo(
            limit=int(limit) if limit else None,
            remaining=int(remaining) if remaining else None,
            reset_timestamp=reset_timestamp
        )

    async def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
        use_personal_token: bool = False
    ) -> Any:
        url = f"{self.base_url}{path}"
        headers = {
            "Accept": "application/json",
            "User-Agent": f"wasenderapi-python-sdk/{SDK_VERSION}"
        }

        if use_personal_token and self.personal_access_token:
            headers["Authorization"] = f"Bearer {self.personal_access_token}"
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"

        processed_body = body.copy() if body else None

        if processed_body and isinstance(processed_body, dict) and processed_body.get("messageType") == "location":
            location_payload = processed_body.get("location", {})
            if isinstance(location_payload.get("latitude"), str):
                location_payload["latitude"] = float(location_payload["latitude"])
            if isinstance(location_payload.get("longitude"), str):
                location_payload["longitude"] = float(location_payload["longitude"])

        request_kwargs = {
            "method": method,
            "url": url,
            "headers": headers
        }

        if method in ["POST", "PUT"]:
            headers["Content-Type"] = "application/json"
            request_kwargs["json"] = processed_body or {}

        attempts = 0
        rate_limit_info: Optional[RateLimitInfo] = None

        while True:
            attempts += 1
            try:
                raw_response = await self.http_client.request(**request_kwargs)
                
                if method == "POST" and path == "/send-message":
                    rate_limit_info = self._parse_rate_limit_headers(raw_response.headers)

                response_dict: Dict[str, Any] = {}

                if raw_response.status_code == 204:
                    response_content: Dict[str, Any]
                    if method == "DELETE" and path.startswith("/whatsapp-sessions/"):
                        response_content = {"success": True, "data": None}
                    elif (method == "POST" or method == "PUT") and ("block" in path or "unblock" in path or "participants" in path or "settings" in path):
                        action_message = "Action completed successfully."
                        if "block" in path: action_message = "Contact blocked/unblocked successfully."
                        if "participants" in path: action_message = "Participants modified successfully."
                        if "settings" in path: action_message = "Settings updated successfully."
                        response_content = {"success": True, "message": action_message, "data": { "message": action_message } }
                    else:
                        response_content = {"success": True, "message": "Operation successful, no content returned."}
                    
                    response_dict["response"] = response_content
                    if rate_limit_info:
                        response_dict["rate_limit"] = rate_limit_info
                    return response_dict

                response_body = raw_response.json()

                if not raw_response.is_success:
                    error_response_data = response_body
                    
                    # Handle rate limiting with retry logic
                    if raw_response.status_code == 429:
                        if self.retry_config.enabled and attempts <= self.retry_config.max_retries:
                            # Get retry_after from response headers or body
                            retry_after = None
                            if 'Retry-After' in raw_response.headers:
                                try:
                                    retry_after = int(raw_response.headers['Retry-After'])
                                except ValueError:
                                    pass
                            elif error_response_data.get("retry_after"):
                                retry_after = error_response_data.get("retry_after")
                            
                            sleep_time = retry_after if retry_after is not None and retry_after > 0 else 1
                            await asyncio.sleep(sleep_time)
                            continue
                    
                    # If not rate limited or retries exhausted/disabled, raise the error
                    raise WasenderAPIError(
                        message=error_response_data.get("message", "API request failed"),
                        status_code=raw_response.status_code,
                        api_message=error_response_data.get("message"),
                        error_details=error_response_data.get("errors"),
                        rate_limit=rate_limit_info,
                        retry_after=error_response_data.get("retry_after")
                    )
                response_dict["response"] = response_body
                if rate_limit_info:
                    response_dict["rate_limit"] = rate_limit_info
                return response_dict

            except WasenderAPIError as e:
                # If it's a rate limit error and we can retry, handle it
                if e.status_code == 429 and self.retry_config.enabled and attempts <= self.retry_config.max_retries:
                    sleep_time = e.retry_after if e.retry_after is not None and e.retry_after > 0 else 1
                    await asyncio.sleep(sleep_time)
                    continue
                else:
                    raise

            except httpx.RequestError as e:
                if attempts > self.retry_config.max_retries:
                    raise WasenderAPIError(message=f"Network error: {str(e)}", status_code=None) from e
                if not self.retry_config.enabled:
                    raise WasenderAPIError(message=f"Network error: {str(e)}", status_code=None) from e
                await asyncio.sleep(1) # Use asyncio.sleep for async

            except json.JSONDecodeError as e:
                raise WasenderAPIError(
                    message="Failed to decode API response (not JSON).", 
                    status_code=raw_response.status_code,
                    api_message=raw_response.text
                ) from e

    async def _post_internal(self, path: str, payload: Optional[Dict[str, Any]], use_personal_token: bool = False) -> Dict[str, Any]:
        return await self._request("POST", path, body=payload, use_personal_token=use_personal_token)

    async def _get_internal(self, path: str, use_personal_token: bool = False) -> Dict[str, Any]:
        return await self._request("GET", path, use_personal_token=use_personal_token)

    async def _put_internal(self, path: str, payload: Dict[str, Any], use_personal_token: bool = False) -> Dict[str, Any]:
        return await self._request("PUT", path, body=payload, use_personal_token=use_personal_token)

    async def _delete_internal(self, path: str, use_personal_token: bool = False) -> Dict[str, Any]:
        return await self._request("DELETE", path, use_personal_token=use_personal_token)

    async def send(self, payload: BaseMessage) -> WasenderSendResult:
        result = await self._post_internal("/send-message", payload.model_dump(by_alias=True))
        return WasenderSendResult(**result)

    async def send_text(self, to: str, text_body: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "text"
        payload["text"] = text_body
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    async def send_image(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "image"
        payload["imageUrl"] = url
        if caption:
            payload["text"] = caption
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    async def send_video(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "video"
        payload["videoUrl"] = url
        if caption:
            payload["text"] = caption
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    async def send_document(self, to: str, url: str, filename: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "document"
        payload["documentUrl"] = url
        payload["fileName"] = filename
        if caption:
            payload["text"] = caption
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    async def send_audio(self, to: str, url: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "audio"
        payload["audioUrl"] = url
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    async def send_sticker(self, to: str, url: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "sticker"
        payload["stickerUrl"] = url
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    async def send_contact(self, to: str, contact_name: str, contact_phone_number: str, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "contact"
        payload["contact"] = {"name": contact_name, "phone": contact_phone_number}
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)

    async def send_location(self, to: str, latitude: float, longitude: float, name: Optional[str] = None, address: Optional[str] = None, **kwargs: Any) -> WasenderSendResult:
        payload: Dict[str, Any] = {**kwargs}
        payload["to"] = to
        payload["messageType"] = "location"
        location_payload = {"latitude": latitude, "longitude": longitude}
        if name:
            location_payload["name"] = name
        if address:
            location_payload["address"] = address
        payload["location"] = location_payload
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)
    
    async def send_poll(self,
        to: str,
        question: str,
        options: List[str],
        is_multiple_choice: bool = False,
    ) -> WasenderSendResult:
        payload: Dict[str, Any] = {
            "to": to,
            "messageType": "poll",
            "poll": {
                "question": question,
                "options": options,
                "multiSelect": is_multiple_choice
            }
        }
        result = await self._post_internal("/send-message", payload)
        return WasenderSendResult(**result)
    
    async def get_contacts(self) -> GetAllContactsResult:
        result = await self._get_internal("/contacts")
        return GetAllContactsResult(**result)

    async def get_contact_info(self, contact_phone_number: str) -> GetContactInfoResult:
        result = await self._get_internal(f"/contacts/{contact_phone_number}")
        return GetContactInfoResult(**result)

    async def get_contact_profile_picture(self, contact_phone_number: str) -> GetContactProfilePictureResult:
        result = await self._get_internal(f"/contacts/{contact_phone_number}/profile-picture")
        return GetContactProfilePictureResult(**result)

    async def block_contact(self, contact_phone_number: str) -> ContactActionResult:
        result = await self._post_internal(f"/contacts/{contact_phone_number}/block", None)
        return ContactActionResult(**result)

    async def unblock_contact(self, contact_phone_number: str) -> ContactActionResult:
        result = await self._post_internal(f"/contacts/{contact_phone_number}/unblock", None)
        return ContactActionResult(**result)

    async def get_groups(self) -> GetAllGroupsResult:
        result = await self._get_internal("/groups")
        return GetAllGroupsResult(**result)

    async def get_group_metadata(self, group_jid: str) -> GetGroupMetadataResult:
        result = await self._get_internal(f"/groups/{group_jid}/metadata")
        return GetGroupMetadataResult(**result)

    async def get_group_participants(self, group_jid: str) -> GetGroupParticipantsResult:
        result = await self._get_internal(f"/groups/{group_jid}/participants")
        return GetGroupParticipantsResult(**result)

    async def add_group_participants(self, group_jid: str, participants: List[str]) -> ModifyGroupParticipantsResult:
        payload = ModifyGroupParticipantsPayload(participants=participants).model_dump(by_alias=True)
        result = await self._post_internal(f"/groups/{group_jid}/participants/add", payload)
        return ModifyGroupParticipantsResult(**result)

    async def remove_group_participants(self, group_jid: str, participants: List[str]) -> ModifyGroupParticipantsResult:
        payload = ModifyGroupParticipantsPayload(participants=participants).model_dump(by_alias=True)
        result = await self._post_internal(f"/groups/{group_jid}/participants/remove", payload)
        return ModifyGroupParticipantsResult(**result)

    async def update_group_settings(self, group_jid: str, settings: UpdateGroupSettingsPayload) -> UpdateGroupSettingsResult:
        payload_dict = settings.model_dump(by_alias=True, exclude_none=True)
        result = await self._put_internal(f"/groups/{group_jid}/settings", payload_dict)
        return UpdateGroupSettingsResult(**result)

    async def get_all_whatsapp_sessions(self) -> GetAllWhatsAppSessionsResult:
        result = await self._get_internal("/whatsapp-sessions", use_personal_token=True)
        return GetAllWhatsAppSessionsResult(**result)

    async def create_whatsapp_session(self, payload: CreateWhatsAppSessionPayload) -> CreateWhatsAppSessionResult:
        payload_dict = payload.model_dump(by_alias=True)
        result = await self._post_internal("/whatsapp-sessions", payload_dict, use_personal_token=True)
        return CreateWhatsAppSessionResult(**result)

    async def get_whatsapp_session_details(self, session_id: int) -> GetWhatsAppSessionDetailsResult:
        result = await self._get_internal(f"/whatsapp-sessions/{session_id}", use_personal_token=True)
        return GetWhatsAppSessionDetailsResult(**result)

    async def update_whatsapp_session(self, session_id: int, payload: UpdateWhatsAppSessionPayload) -> UpdateWhatsAppSessionResult:
        payload_dict = payload.model_dump(by_alias=True, exclude_none=True)
        result = await self._put_internal(f"/whatsapp-sessions/{session_id}", payload_dict, use_personal_token=True)
        return UpdateWhatsAppSessionResult(**result)

    async def delete_whatsapp_session(self, session_id: int) -> DeleteWhatsAppSessionResult:
        result = await self._delete_internal(f"/whatsapp-sessions/{session_id}", use_personal_token=True)
        return DeleteWhatsAppSessionResult(**result)

    async def connect_whatsapp_session(self, session_id: int, qr_as_image: Optional[bool] = None) -> ConnectSessionResult:
        params = {"qrAsImage": "true"} if qr_as_image else {}
        path = f"/whatsapp-sessions/{session_id}/connect"
        if params:
            path += "?" + urlencode(params)
        result = await self._post_internal(path, None, use_personal_token=True)
        return ConnectSessionResult(**result)

    async def get_whatsapp_session_qr_code(self, session_id: int) -> GetQRCodeResult:
        result = await self._get_internal(f"/whatsapp-sessions/{session_id}/qr-code", use_personal_token=True)
        return GetQRCodeResult(**result)

    async def disconnect_whatsapp_session(self, session_id: int) -> DisconnectSessionResult:
        result = await self._post_internal(f"/whatsapp-sessions/{session_id}/disconnect", None, use_personal_token=True)
        return DisconnectSessionResult(**result)

    async def regenerate_api_key(self, session_id: int) -> RegenerateApiKeyResult:
        result = await self._post_internal(f"/whatsapp-sessions/{session_id}/regenerate-api-key", None, use_personal_token=True)
        return RegenerateApiKeyResult(**result)

    async def get_session_status(self, session_id: str) -> GetSessionStatusResult:
        result = await self._get_internal(f"/sessions/{session_id}/status", use_personal_token=True)
        return GetSessionStatusResult(**result)

    async def handle_webhook_event(
        self,
        request_body_bytes: bytes,
        signature_header: Optional[str]
    ) -> WasenderWebhookEvent:
        if not self.webhook_secret:
            raise ValueError("Webhook secret is not configured in the client.")
        
        if not verify_wasender_webhook_signature(signature_header, self.webhook_secret):
            raise WasenderAPIError("Invalid webhook signature", status_code=400)

        try:
            request_body_str = request_body_bytes.decode('utf-8')
            data = json.loads(request_body_str)
            adapter = TypeAdapter(WasenderWebhookEvent)
            parsed_event = adapter.validate_python(data)
            return parsed_event
        except json.JSONDecodeError as e:
            raise WasenderAPIError("Invalid JSON in webhook body", status_code=400) from e
        except Exception as e:
            raise WasenderAPIError(f"Invalid webhook event data: {str(e)}", status_code=400) from e

def create_async_wasender(
    api_key: str,
    base_url: Optional[str] = None,
    retry_options: Optional[RetryConfig] = None,
    webhook_secret: Optional[str] = None,
    personal_access_token: Optional[str] = None,
    http_client: Optional[httpx.AsyncClient] = None # Added for custom async client
) -> WasenderAsyncClient:
    """Create a new instance of the WasenderAsyncClient.

    Args:
        api_key: Your Wasender API key
        base_url: Optional custom base URL for the API
        retry_options: Optional retry configuration
        webhook_secret: Optional webhook secret for verifying webhook requests
        personal_access_token: Optional personal access token for authentication
        http_client: Optional custom httpx.AsyncClient instance.

    Returns:
        A new WasenderAsyncClient instance
    """
    return WasenderAsyncClient(
        api_key=api_key,
        base_url=base_url or "https://www.wasenderapi.com/api",
        retry_options=retry_options,
        webhook_secret=webhook_secret,
        personal_access_token=personal_access_token,
        http_client=http_client
    )