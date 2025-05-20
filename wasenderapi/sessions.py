from typing import List, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from .models import RateLimitInfo

class WhatsAppSessionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    NEED_SCAN = "need_scan"
    CONNECTING = "connecting"
    LOGGED_OUT = "logged_out"
    EXPIRED = "expired"

class WhatsAppSession(BaseModel):
    id: int
    user_id: int = Field(..., alias="userId")
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    status: WhatsAppSessionStatus
    api_key: str = Field(..., alias="apiKey")
    session_data: dict = Field(..., alias="sessionData")
    last_active_at: datetime = Field(..., alias="lastActiveAt")
    account_protection: bool = Field(..., alias="accountProtection")
    log_messages: bool = Field(..., alias="logMessages")
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")
    webhook_enabled: bool = Field(..., alias="webhookEnabled")
    webhook_events: Optional[List[str]] = Field(None, alias="webhookEvents")
    webhook_secret: str = Field(..., alias="webhookSecret")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")




class CreateWhatsAppSessionPayload(BaseModel):
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    account_protection: bool = Field(..., alias="accountProtection")
    log_messages: bool = Field(..., alias="logMessages")
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")
    webhook_enabled: Optional[bool] = Field(None, alias="webhookEnabled")
    webhook_events: Optional[List[str]] = Field(None, alias="webhookEvents")

class UpdateWhatsAppSessionPayload(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    account_protection: Optional[bool] = Field(None, alias="accountProtection")
    log_messages: Optional[bool] = Field(None, alias="logMessages")
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")
    webhook_enabled: Optional[bool] = Field(None, alias="webhookEnabled")
    webhook_events: Optional[List[str]] = Field(None, alias="webhookEvents")

class ConnectSessionPayload(BaseModel):
    qr_as_image: Optional[bool] = Field(None, alias="qrAsImage")

class ConnectSessionResponseData(BaseModel):
    status: WhatsAppSessionStatus
    qr_code: Optional[str] = Field(None, alias="qrCode")
    message: Optional[str] = None

class QRCodeResponseData(BaseModel):
    qr_code: str = Field(..., alias="qrCode")

class DisconnectSessionResponseData(BaseModel):
    status: WhatsAppSessionStatus
    message: Optional[str] = None

class RegenerateApiKeyResponse(BaseModel):
    success: bool = True
    api_key: str = Field(..., alias="apiKey")

class SessionStatusData(BaseModel):
    status: WhatsAppSessionStatus

class GetAllWhatsAppSessionsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[WhatsAppSession]

class GetWhatsAppSessionDetailsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: WhatsAppSession

class CreateWhatsAppSessionResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: WhatsAppSession

class UpdateWhatsAppSessionResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: WhatsAppSession

class DeleteWhatsAppSessionResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: None

class ConnectSessionResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: ConnectSessionResponseData

class GetQRCodeResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: QRCodeResponseData

class DisconnectSessionResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: DisconnectSessionResponseData

class GetSessionStatusResponse(BaseModel):
    status: WhatsAppSessionStatus

# Result types including rate limiting
class GetAllWhatsAppSessionsResult(BaseModel):
    response: GetAllWhatsAppSessionsResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetWhatsAppSessionDetailsResult(BaseModel):
    response: GetWhatsAppSessionDetailsResponse
    rate_limit: Optional[RateLimitInfo] = None

class CreateWhatsAppSessionResult(BaseModel):
    response: CreateWhatsAppSessionResponse
    rate_limit: Optional[RateLimitInfo] = None

class UpdateWhatsAppSessionResult(BaseModel):
    response: UpdateWhatsAppSessionResponse
    rate_limit: Optional[RateLimitInfo] = None

class DeleteWhatsAppSessionResult(BaseModel):
    response: DeleteWhatsAppSessionResponse
    rate_limit: Optional[RateLimitInfo] = None

class ConnectSessionResult(BaseModel):
    response: ConnectSessionResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetQRCodeResult(BaseModel):
    response: GetQRCodeResponse
    rate_limit: Optional[RateLimitInfo] = None

class DisconnectSessionResult(BaseModel):
    response: DisconnectSessionResponse
    rate_limit: Optional[RateLimitInfo] = None

class RegenerateApiKeyResult(BaseModel):
    response: RegenerateApiKeyResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetSessionStatusResult(BaseModel):
    response: GetSessionStatusResponse
    rate_limit: Optional[RateLimitInfo] = None 