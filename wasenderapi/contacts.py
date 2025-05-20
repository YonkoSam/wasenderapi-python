from typing import Optional, List
from pydantic import BaseModel, Field
from .models import RateLimitInfo, Contact

class GetAllContactsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[Contact]

class GetContactInfoResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Contact

class ProfilePicData(BaseModel):
    img_url: Optional[str] = Field(None, alias="imgUrl")

class GetContactProfilePictureResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: ProfilePicData

class ContactActionData(BaseModel):
    message: Optional[str] = None

class ContactActionResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: ContactActionData

# Result types including rate limiting
class GetAllContactsResult(BaseModel):
    response: GetAllContactsResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetContactInfoResult(BaseModel):
    response: GetContactInfoResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetContactProfilePictureResult(BaseModel):
    response: GetContactProfilePictureResponse
    rate_limit: Optional[RateLimitInfo] = None

class ContactActionResult(BaseModel):
    response: ContactActionResponse
    rate_limit: Optional[RateLimitInfo] = None 