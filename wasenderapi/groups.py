from typing import List, Optional
from pydantic import BaseModel, Field
from .models import RateLimitInfo

class GroupParticipant(BaseModel):
    jid: str
    is_admin: bool = Field(..., alias="isAdmin")
    is_super_admin: bool = Field(..., alias="isSuperAdmin")

class BasicGroupInfo(BaseModel):
    jid: str
    name: Optional[str] = None
    img_url: Optional[str] = Field(None, alias="imgUrl")

class GroupMetadata(BasicGroupInfo):
    creation: int
    owner: Optional[str] = None
    desc: Optional[str] = None
    participants: List[GroupParticipant]
    subject: Optional[str] = None

class ModifyGroupParticipantsPayload(BaseModel):
    participants: List[str]

class UpdateGroupSettingsPayload(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    announce: Optional[bool] = None
    restrict: Optional[bool] = None

class ParticipantActionStatus(BaseModel):
    status: int
    jid: str
    message: str

class UpdateGroupSettingsResponseData(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None

class GetAllGroupsResponse(BaseModel):
    success: bool = True
    message: str
    data: List[BasicGroupInfo]

class GetGroupMetadataResponse(BaseModel):
    success: bool = True
    message: str
    data: GroupMetadata

class GetGroupParticipantsResponse(BaseModel):
    success: bool = True
    message: str
    data: List[GroupParticipant]

class ModifyGroupParticipantsResponse(BaseModel):
    success: bool = True
    message: str
    data: List[ParticipantActionStatus]

class UpdateGroupSettingsResponse(BaseModel):
    success: bool = True
    message: str
    data: UpdateGroupSettingsResponseData

# Result types including rate limiting
class GetAllGroupsResult(BaseModel):
    response: GetAllGroupsResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetGroupMetadataResult(BaseModel):
    response: GetGroupMetadataResponse
    rate_limit: Optional[RateLimitInfo] = None

class GetGroupParticipantsResult(BaseModel):
    response: GetGroupParticipantsResponse
    rate_limit: Optional[RateLimitInfo] = None

class ModifyGroupParticipantsResult(BaseModel):
    response: ModifyGroupParticipantsResponse
    rate_limit: Optional[RateLimitInfo] = None

class UpdateGroupSettingsResult(BaseModel):
    response: UpdateGroupSettingsResponse
    rate_limit: Optional[RateLimitInfo] = None 