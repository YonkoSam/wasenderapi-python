from typing import Dict, List, Optional, Union, Any, TypeAlias
from pydantic import BaseModel, Field
from .models import RateLimitInfo

WasenderErrorDetail: TypeAlias = Dict[str, List[str]]

class WasenderErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: Optional[WasenderErrorDetail] = None
    retry_after: Optional[int] = Field(None, alias="retryAfter")

class WasenderSuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None

WasenderAPIRawResponse = Union[WasenderSuccessResponse, WasenderErrorResponse]

class WasenderAPIError(Exception):
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_message: Optional[str] = None,
        error_details: Optional[WasenderErrorDetail] = None,
        rate_limit: Optional[RateLimitInfo] = None,
        retry_after: Optional[int] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.api_message = api_message if api_message is not None else message
        self.error_details = error_details
        self.rate_limit = rate_limit
        self.retry_after = retry_after
        self.success = False 