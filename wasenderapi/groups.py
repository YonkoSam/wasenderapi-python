from typing import List, Optional
from pydantic import BaseModel, Field
from .models import RateLimitInfo

class GroupParticipant(BaseModel):
    id: str
    admin: Optional[str] = None

class BasicGroupInfo(BaseModel):
    id: str
    name: Optional[str] = None
    img_url: Optional[str] = Field(None, alias="imgUrl")

class GroupMetadata(BasicGroupInfo):
    creation: int
    owner: Optional[str] = None
    subject: Optional[str] = None
    subject_owner: Optional[str] = Field(None, alias="subjectOwner")
    subject_time: Optional[int] = Field(None, alias="subjectTime")
    desc: Optional[str] = None
    desc_owner: Optional[str] = Field(None, alias="descOwner")
    desc_id: Optional[str] = Field(None, alias="descId")
    restrict: Optional[bool] = None
    announce: Optional[bool] = None
    is_community: Optional[bool] = Field(None, alias="isCommunity")
    is_community_announce: Optional[bool] = Field(None, alias="isCommunityAnnounce")
    join_approval_mode: Optional[bool] = Field(None, alias="joinApprovalMode")
    member_add_mode: Optional[bool] = Field(None, alias="memberAddMode")
    author: Optional[str] = None
    size: Optional[int] = None
    participants: List[GroupParticipant]
    ephemeral_duration: Optional[int] = Field(None, alias="ephemeralDuration")
    invite_code: Optional[str] = Field(None, alias="inviteCode")

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
    message: Optional[str] = None
    data: List[BasicGroupInfo]

class GetGroupMetadataResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: GroupMetadata

class GetGroupParticipantsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[GroupParticipant]

class ModifyGroupParticipantsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: List[ParticipantActionStatus]

class UpdateGroupSettingsResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
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