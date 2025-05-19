from typing import List, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field
from .models import RateLimitInfo

class WhatsAppSessionStatus(str, Enum):
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    NEED_SCAN = "NEED_SCAN"
    CONNECTING = "CONNECTING"
    LOGGED_OUT = "LOGGED_OUT"
    EXPIRED = "EXPIRED"

class WhatsAppSession(BaseModel):
    id: int
    name: str
    phone_number: str = Field(..., alias="phoneNumber")
    status: WhatsAppSessionStatus
    account_protection: bool = Field(..., alias="accountProtection")
    log_messages: bool = Field(..., alias="logMessages")
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")
    webhook_enabled: bool = Field(..., alias="webhookEnabled")
    webhook_events: Optional[List[str]] = Field(None, alias="webhookEvents")
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
    message: str

class RegenerateApiKeyResponse(BaseModel):
    success: bool = True
    api_key: str = Field(..., alias="apiKey")

class SessionStatusData(BaseModel):
    status: WhatsAppSessionStatus

class GetAllWhatsAppSessionsResponse(BaseModel):
    success: bool = True
    message: str
    data: List[WhatsAppSession]

class GetWhatsAppSessionDetailsResponse(BaseModel):
    success: bool = True
    message: str
    data: WhatsAppSession

class CreateWhatsAppSessionResponse(BaseModel):
    success: bool = True
    message: str
    data: WhatsAppSession

class UpdateWhatsAppSessionResponse(BaseModel):
    success: bool = True
    message: str
    data: WhatsAppSession

class DeleteWhatsAppSessionResponse(BaseModel):
    success: bool = True
    message: str
    data: None

class ConnectSessionResponse(BaseModel):
    success: bool = True
    message: str
    data: ConnectSessionResponseData

class GetQRCodeResponse(BaseModel):
    success: bool = True
    message: str
    data: QRCodeResponseData

class DisconnectSessionResponse(BaseModel):
    success: bool = True
    message: str
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