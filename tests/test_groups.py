import pytest
# Client and requests related imports removed as client method tests are removed
# from unittest.mock import Mock, patch
# from wasenderapi.client import WasenderClient
# import json
# import requests
from wasenderapi.models import RateLimitInfo # Keep if used by type def tests, seems so by mock_rate_limit_info
from wasenderapi.groups import (
    GroupParticipant, BasicGroupInfo, GroupMetadata,
    ModifyGroupParticipantsPayload, UpdateGroupSettingsPayload,
    ParticipantActionStatus, UpdateGroupSettingsResponseData, # Sub-structures for responses
    GetAllGroupsResult, GetGroupMetadataResult, GetGroupParticipantsResult,
    ModifyGroupParticipantsResult, UpdateGroupSettingsResult
)
from pydantic import ValidationError
from datetime import datetime
from wasenderapi import create_async_wasender
from wasenderapi.models import RetryConfig
from unittest.mock import AsyncMock

# Fixtures for client method tests - REMOVED
# @pytest.fixture
# def mock_client(): ...
# @pytest.fixture
# def mock_groups_response(): ...
# @pytest.fixture
# def mock_group_metadata_response(): ...
# @pytest.fixture
# def mock_group_settings_response(): ...

# Fixtures for type definition tests - RETAINED
@pytest.fixture
def mock_rate_limit_info_dict(): # Renamed from mock_rate_limit_info
    return {
        "limit": 100,
        "remaining": 99,
        "reset_timestamp": int(datetime.now().timestamp()) + 3600
    }

@pytest.fixture
def mock_admin_participant_api_data(): # API-like data (camelCase)
    return {
        "jid": "admin@s.whatsapp.net",
        "isAdmin": True,
        "isSuperAdmin": True
    }

@pytest.fixture
def mock_participant_api_data(): # API-like data (camelCase)
    return {
        "jid": "participant@s.whatsapp.net",
        "isAdmin": False,
        "isSuperAdmin": False
    }

@pytest.fixture
def mock_basic_group_info_api_data(): # API-like data (camelCase)
    return {
        "jid": "1234567890-1234567890@g.us",
        "name": "Test Group Name API",
        "imgUrl": "https://group.pic/api.png"
    }

@pytest.fixture
def mock_basic_group_info_nulls_api_data(): # API-like data (camelCase)
    return {
        "jid": "1234567890-1234567891@g.us",
        "name": None,
        "imgUrl": None
    }

@pytest.fixture
def mock_group_metadata_api_data(mock_basic_group_info_api_data, mock_admin_participant_api_data, mock_participant_api_data):
    return {
        **mock_basic_group_info_api_data, # spread basic group info
        "creation": 1678886400,
        "owner": "owner@s.whatsapp.net",
        "desc": "This is a test group description API.",
        "participants": [mock_admin_participant_api_data, mock_participant_api_data],
        "subject": "Test Group Subject API"
    }

# Client method tests - REMOVED
# @pytest.mark.asyncio
# async def test_get_all_groups(mock_client, mock_groups_response): ...
# @pytest.mark.asyncio
# async def test_get_group_metadata(mock_client, mock_group_metadata_response): ...
# @pytest.mark.asyncio
# async def test_update_group_settings(mock_client, mock_group_settings_response): ...
# (and any other client method tests that might have been below the initially viewed part)

@pytest.fixture
async def async_client_groups_mocked_internals():
    retry_config_disabled = RetryConfig(enabled=False)
    client = create_async_wasender(api_key="test_groups_key", retry_options=retry_config_disabled)
    client._get_internal = AsyncMock(name="_get_internal")
    client._post_internal = AsyncMock(name="_post_internal")
    client._put_internal = AsyncMock(name="_put_internal") # For update_group_settings
    return client

class TestGroupCoreModels:
    def test_group_participant_model(self, mock_admin_participant_api_data, mock_participant_api_data):
        admin_model = GroupParticipant(**mock_admin_participant_api_data) # camelCase from API to model
        assert admin_model.jid == mock_admin_participant_api_data["jid"]
        assert admin_model.is_admin is True
        assert admin_model.is_super_admin is True
        # Test serialization with by_alias=True
        assert admin_model.model_dump(by_alias=True)["isAdmin"] is True

        member_model = GroupParticipant(**mock_participant_api_data)
        assert member_model.is_admin is False
        with pytest.raises(ValidationError): # is_admin is required
            GroupParticipant(jid="test@s.whatsapp.net", isSuperAdmin=False)
    
    def test_basic_group_info_model(self, mock_basic_group_info_api_data, mock_basic_group_info_nulls_api_data):
        group_model = BasicGroupInfo(**mock_basic_group_info_api_data)
        assert group_model.jid == mock_basic_group_info_api_data["jid"]
        assert group_model.name == mock_basic_group_info_api_data["name"]
        assert group_model.img_url == mock_basic_group_info_api_data["imgUrl"]
        assert group_model.model_dump(by_alias=True)["imgUrl"] == mock_basic_group_info_api_data["imgUrl"]

        group_nulls_model = BasicGroupInfo(**mock_basic_group_info_nulls_api_data)
        assert group_nulls_model.name is None
        assert group_nulls_model.img_url is None
        assert "name" not in group_nulls_model.model_dump(by_alias=True, exclude_none=True)
        with pytest.raises(ValidationError): # jid is required
            BasicGroupInfo(name="Test")

    def test_group_metadata_model(self, mock_group_metadata_api_data, mock_participant_api_data):
        metadata_model = GroupMetadata(**mock_group_metadata_api_data)
        assert metadata_model.jid == mock_group_metadata_api_data["jid"]
        assert metadata_model.creation == mock_group_metadata_api_data["creation"]
        assert metadata_model.owner == mock_group_metadata_api_data["owner"]
        assert metadata_model.desc == mock_group_metadata_api_data["desc"]
        assert len(metadata_model.participants) == 2
        assert isinstance(metadata_model.participants[0], GroupParticipant)
        assert metadata_model.participants[0].is_super_admin is True
        assert metadata_model.subject == mock_group_metadata_api_data["subject"]

        # Test with minimal data (optional fields missing)
        minimal_participant_dict = mock_participant_api_data # This is already the dict result from the fixture
        minimal_data = {
            "jid": "groupjid@g.us",
            "creation": 1678886401,
            "participants": [minimal_participant_dict] 
            # owner, desc, subject, name, imgUrl are optional
        }
        minimal_model = GroupMetadata(**minimal_data)
        assert minimal_model.owner is None
        assert minimal_model.desc is None
        assert minimal_model.subject is None
        assert minimal_model.name is None # from BasicGroupInfo
        assert minimal_model.img_url is None # from BasicGroupInfo
        assert "owner" not in minimal_model.model_dump(by_alias=True, exclude_none=True)

class TestGroupRequestPayloadModels:
    def test_modify_group_participants_payload(self):
        payload_data = {"participants": ["123@s.whatsapp.net", "456@s.whatsapp.net"]}
        model = ModifyGroupParticipantsPayload(**payload_data)
        assert len(model.participants) == 2
        assert model.participants[0] == payload_data["participants"][0]
        assert model.model_dump() == payload_data # No aliases in this model
        with pytest.raises(ValidationError): # participants list is required
            ModifyGroupParticipantsPayload(participants=None)
        with pytest.raises(ValidationError): 
            ModifyGroupParticipantsPayload(participants=["123", 123]) # Items must be strings

    def test_update_group_settings_payload(self):
        # All fields
        payload_data_all = {
            "subject": "New Subject", "description": "New Description",
            "announce": True, "restrict": True
        }
        model_all = UpdateGroupSettingsPayload(**payload_data_all)
        assert model_all.subject == payload_data_all["subject"]
        assert model_all.announce is True
        assert model_all.model_dump(exclude_none=True) == payload_data_all

        # Partial updates (all fields are optional)
        model_partial = UpdateGroupSettingsPayload(subject="Only Subject")
        assert model_partial.subject == "Only Subject"
        assert model_partial.description is None
        dumped_partial = model_partial.model_dump(exclude_none=True)
        assert "description" not in dumped_partial
        assert dumped_partial["subject"] == "Only Subject"

        # Empty payload is valid
        model_empty = UpdateGroupSettingsPayload()
        assert model_empty.model_dump(exclude_none=True) == {}

class TestGroupResultModels:
    def test_participant_action_status_model(self): # Testing this sub-model directly
        data1 = {"status": 200, "jid": "123@s.whatsapp.net", "message": "added"}
        model1 = ParticipantActionStatus(**data1)
        assert model1.status == 200
        assert model1.jid == data1["jid"]
        assert model1.message == data1["message"]

        data2 = {"status": 403, "jid": "456@s.whatsapp.net", "message": "not-authorized"}
        model2 = ParticipantActionStatus(**data2)
        assert model2.status == 403
        with pytest.raises(ValidationError): # jid is required
            ParticipantActionStatus(status=200, message="ok")

    def test_update_group_settings_response_data_model(self): # Testing this sub-model
        data_all = {"subject": "Updated Subject", "description": "Updated Description"}
        model_all = UpdateGroupSettingsResponseData(**data_all)
        assert model_all.subject == data_all["subject"]
        assert model_all.description == data_all["description"]

        data_partial = {"subject": "Only Subject Updated"}
        model_partial = UpdateGroupSettingsResponseData(**data_partial)
        assert model_partial.subject == data_partial["subject"]
        assert model_partial.description is None
        assert model_partial.model_dump(exclude_none=True) == data_partial
        
        model_empty = UpdateGroupSettingsResponseData() # All fields optional
        assert model_empty.model_dump(exclude_none=True) == {}

    def test_get_all_groups_result(self, mock_basic_group_info_api_data, mock_basic_group_info_nulls_api_data, mock_rate_limit_info_dict):
        api_data_list = [mock_basic_group_info_api_data, mock_basic_group_info_nulls_api_data]
        raw_response_data = {"success": True, "message": "Groups retrieved", "data": api_data_list}
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}
        
        result_model = GetAllGroupsResult(**full_result_data)
        assert result_model.response.success is True
        assert len(result_model.response.data) == 2
        assert isinstance(result_model.response.data[0], BasicGroupInfo)
        assert result_model.response.data[0].name == mock_basic_group_info_api_data["name"]
        assert result_model.response.data[1].name is None
        assert result_model.response.data[0].img_url == mock_basic_group_info_api_data["imgUrl"] # Check aliasing
        assert result_model.rate_limit.limit == mock_rate_limit_info_dict["limit"]

    def test_get_group_metadata_result(self, mock_group_metadata_api_data, mock_rate_limit_info_dict):
        raw_response_data = {"success": True, "message": "Metadata retrieved", "data": mock_group_metadata_api_data}
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}

        result_model = GetGroupMetadataResult(**full_result_data)
        assert result_model.response.success is True
        assert isinstance(result_model.response.data, GroupMetadata)
        assert result_model.response.data.desc == mock_group_metadata_api_data["desc"]
        assert result_model.response.data.participants[0].is_admin == mock_group_metadata_api_data["participants"][0]["isAdmin"]
        assert result_model.rate_limit.remaining == mock_rate_limit_info_dict["remaining"]

    def test_get_group_participants_result(self, mock_admin_participant_api_data, mock_participant_api_data, mock_rate_limit_info_dict):
        api_participants_list = [mock_admin_participant_api_data, mock_participant_api_data]
        raw_response_data = {"success": True, "message": "Participants retrieved", "data": api_participants_list}
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}

        result_model = GetGroupParticipantsResult(**full_result_data)
        assert result_model.response.success is True
        assert len(result_model.response.data) == 2
        assert isinstance(result_model.response.data[0], GroupParticipant)
        assert result_model.response.data[0].is_super_admin == api_participants_list[0]["isSuperAdmin"]
        assert result_model.rate_limit is not None

    def test_modify_group_participants_result(self, mock_rate_limit_info_dict):
        action_status_api_data = [{"status": 200, "jid": "123@s.whatsapp.net", "message": "added"}]
        raw_response_data = {"success": True, "message": "Participants modified", "data": action_status_api_data}
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}
        
        result_model = ModifyGroupParticipantsResult(**full_result_data)
        assert result_model.response.success is True
        assert len(result_model.response.data) == 1
        assert isinstance(result_model.response.data[0], ParticipantActionStatus)
        assert result_model.response.data[0].status == action_status_api_data[0]["status"]

    def test_update_group_settings_result(self, mock_rate_limit_info_dict):
        settings_response_api_data = {"subject": "New Subject API"}
        raw_response_data = {"success": True, "message": "Settings updated", "data": settings_response_api_data}
        full_result_data = {"response": raw_response_data, "rate_limit": mock_rate_limit_info_dict}
        
        result_model = UpdateGroupSettingsResult(**full_result_data)
        assert result_model.response.success is True
        assert isinstance(result_model.response.data, UpdateGroupSettingsResponseData)
        assert result_model.response.data.subject == settings_response_api_data["subject"]
        assert result_model.rate_limit.limit == mock_rate_limit_info_dict["limit"]

class TestGroupsClientMethods:
    @pytest.mark.asyncio
    async def test_get_groups(self, async_client_groups_mocked_internals, mock_basic_group_info_api_data, mock_rate_limit_info_dict):
        client = async_client_groups_mocked_internals
        mock_api_response_data = {"success": True, "message": "Groups list", "data": [mock_basic_group_info_api_data]}
        client._get_internal.return_value = {"response": mock_api_response_data, "rate_limit": mock_rate_limit_info_dict}

        result: GetAllGroupsResult = await client.get_groups()

        client._get_internal.assert_called_once_with("/groups")
        assert isinstance(result, GetAllGroupsResult)
        assert len(result.response.data) == 1

    @pytest.mark.asyncio
    async def test_get_group_metadata(self, async_client_groups_mocked_internals, mock_group_metadata_api_data, mock_rate_limit_info_dict):
        client = async_client_groups_mocked_internals
        group_jid = "testgroup@g.us"
        mock_response_payload = {"success": True, "message": "Group metadata", "data": mock_group_metadata_api_data}
        client._get_internal.return_value = {"response": mock_response_payload, "rate_limit": mock_rate_limit_info_dict}

        result: GetGroupMetadataResult = await client.get_group_metadata(group_jid=group_jid)

        client._get_internal.assert_called_once_with(f"/groups/{group_jid}")
        assert isinstance(result, GetGroupMetadataResult)
        assert result.response.data.jid == mock_group_metadata_api_data["jid"]

    @pytest.mark.asyncio
    async def test_get_group_participants(self, async_client_groups_mocked_internals, mock_admin_participant_api_data, mock_rate_limit_info_dict):
        client = async_client_groups_mocked_internals
        group_jid = "testgroup@g.us"
        api_participants_list = [mock_admin_participant_api_data]
        mock_response_payload = {"success": True, "message": "Group participants list", "data": api_participants_list}
        client._get_internal.return_value = {"response": mock_response_payload, "rate_limit": mock_rate_limit_info_dict}

        result: GetGroupParticipantsResult = await client.get_group_participants(group_jid=group_jid)

        client._get_internal.assert_called_once_with(f"/groups/{group_jid}/participants")
        assert isinstance(result, GetGroupParticipantsResult)
        assert len(result.response.data) == 1

    @pytest.mark.asyncio
    async def test_add_group_participants(self, async_client_groups_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_groups_mocked_internals
        group_jid = "testgroup@g.us"
        participants_to_add = ["participant1@s.whatsapp.net", "participant2@s.whatsapp.net"]
        action_status_api_data = [{"status": 200, "jid": p, "message": "added"} for p in participants_to_add]
        mock_response_payload = {"success": True, "message": "Participants added", "data": action_status_api_data}
        client._post_internal.return_value = {"response": mock_response_payload, "rate_limit": mock_rate_limit_info_dict}

        payload_model = ModifyGroupParticipantsPayload(participants=participants_to_add)
        result: ModifyGroupParticipantsResult = await client.add_group_participants(group_jid=group_jid, participants=participants_to_add)

        client._post_internal.assert_called_once_with(
            f"/groups/{group_jid}/participants/add",
            payload_model.model_dump(by_alias=True)
        )
        assert isinstance(result, ModifyGroupParticipantsResult)
        assert len(result.response.data) == len(participants_to_add)

    @pytest.mark.asyncio
    async def test_remove_group_participants(self, async_client_groups_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_groups_mocked_internals
        group_jid = "testgroup@g.us"
        participants_to_remove = ["participant1@s.whatsapp.net"]
        action_status_api_data = [{"status": 200, "jid": p, "message": "removed"} for p in participants_to_remove]
        mock_response_payload = {"success": True, "message": "Participants removed", "data": action_status_api_data}
        client._post_internal.return_value = {"response": mock_response_payload, "rate_limit": mock_rate_limit_info_dict}

        payload_model = ModifyGroupParticipantsPayload(participants=participants_to_remove)
        result: ModifyGroupParticipantsResult = await client.remove_group_participants(group_jid=group_jid, participants=participants_to_remove)

        client._post_internal.assert_called_once_with(
            f"/groups/{group_jid}/participants/remove",
            payload_model.model_dump(by_alias=True)
        )
        assert isinstance(result, ModifyGroupParticipantsResult)

    @pytest.mark.asyncio
    async def test_update_group_settings(self, async_client_groups_mocked_internals, mock_rate_limit_info_dict):
        client = async_client_groups_mocked_internals
        group_jid = "testgroup@g.us"
        settings_to_update = UpdateGroupSettingsPayload(subject="New Group Subject", announce=True)
        updated_settings_api_data = {"subject": "New Group Subject", "description": None, "announce": True, "restrict": None}
        mock_response_payload = {"success": True, "message": "Settings updated", "data": updated_settings_api_data}
        client._put_internal.return_value = {"response": mock_response_payload, "rate_limit": mock_rate_limit_info_dict}

        result: UpdateGroupSettingsResult = await client.update_group_settings(group_jid=group_jid, settings=settings_to_update)

        client._put_internal.assert_called_once_with(
            f"/groups/{group_jid}/settings",
            settings_to_update.model_dump(by_alias=True, exclude_none=True)
        )
        assert isinstance(result, UpdateGroupSettingsResult)
        assert result.response.data.subject == "New Group Subject"

# Client method tests will be added after this class.
# The old TestAPIResponseDataStructures, TestAPISuccessResponseTypes, TestResultTypes should be removed. 