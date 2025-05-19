import pytest
import json # Added json for client.handle_webhook_event body
# Unittest.mock and requests might not be needed if client tests are fully removed
# from unittest.mock import Mock, patch 
from wasenderapi.client import WasenderClient # Client import for testing its handle_webhook_event
from wasenderapi.errors import WasenderAPIError # For asserting exceptions from client
from wasenderapi.webhook import (
    verify_wasender_webhook_signature,
    WEBHOOK_SIGNATURE_HEADER,
    WasenderWebhookEventType as WebhookEventType,
    # WebhookHandler, # Removed: Does not exist
    WasenderWebhookEvent # Import the Union type for direct parsing tests
)
from typing import Dict, Any
from dataclasses import dataclass
from pydantic import TypeAdapter # Add this import

SECRET = "shh!"

@dataclass
class MockRequest: # This might still be useful for constructing headers for client tests
    headers: Dict[str, str]
    body: bytes # Changed to bytes for client.handle_webhook_event

    async def json(self): # This method might not be used if we parse directly
        return json.loads(self.body.decode('utf-8'))

def make_req_for_client_test(body: Dict[str, Any], signature: str = None) -> MockRequest:
    headers = {}
    if signature:
        headers[WEBHOOK_SIGNATURE_HEADER] = signature
    return MockRequest(headers=headers, body=json.dumps(body).encode('utf-8'))

# Removed webhook_handler fixture
# @pytest.fixture
# def webhook_handler(): ...

@pytest.fixture
def client_for_webhook_tests():
    # Minimal client, only needs webhook_secret for these tests
    return WasenderClient(api_key="test_api_key_for_webhook", webhook_secret=SECRET)

class TestWebhookSignatureVerification:
    def test_rejects_missing_signature(self):
        assert not verify_wasender_webhook_signature(None, SECRET)

    def test_rejects_incorrect_signature(self):
        assert not verify_wasender_webhook_signature("wrongsecret", SECRET)

    def test_accepts_correct_signature(self):
        assert verify_wasender_webhook_signature(SECRET, SECRET)

    def test_rejects_empty_configured_secret(self):
        assert not verify_wasender_webhook_signature(SECRET, "")

    def test_rejects_none_configured_secret(self):
        assert not verify_wasender_webhook_signature(SECRET, None)

class TestWebhookEventHandling:
    @pytest.mark.asyncio
    async def test_client_handle_webhook_rejects_invalid_signature(self, client_for_webhook_tests):
        payload = {"type": "something"}
        mock_req = make_req_for_client_test(payload) # No signature
        with pytest.raises(WasenderAPIError, match="Invalid webhook signature"):
            await client_for_webhook_tests.handle_webhook_event(
                request_body_bytes=mock_req.body, 
                signature_header=mock_req.headers.get(WEBHOOK_SIGNATURE_HEADER)
            )

    @pytest.mark.asyncio
    async def test_client_handle_webhook_rejects_incorrect_signature(self, client_for_webhook_tests):
        payload = {"type": "something"}
        mock_req = make_req_for_client_test(payload, "wrongsecret")
        with pytest.raises(WasenderAPIError, match="Invalid webhook signature"):
            await client_for_webhook_tests.handle_webhook_event(
                request_body_bytes=mock_req.body, 
                signature_header=mock_req.headers.get(WEBHOOK_SIGNATURE_HEADER)
            )
    
    @pytest.mark.asyncio
    async def test_client_handle_webhook_parses_valid_event(self, client_for_webhook_tests):
        chat_entry = {
            "id": "1234567890", "name": "Contact Name", 
            "conversationTimestamp": 1633456789, "unreadCount": 2
        }
        payload = {
            "type": WebhookEventType.CHATS_UPSERT.value,
            "timestamp": 1633456789,
            "data": [chat_entry],
            "sessionId": "session-id-123"
        }
        mock_req = make_req_for_client_test(payload, SECRET)
        evt = await client_for_webhook_tests.handle_webhook_event(
            request_body_bytes=mock_req.body,
            signature_header=mock_req.headers.get(WEBHOOK_SIGNATURE_HEADER)
        )
        assert evt.type == WebhookEventType.CHATS_UPSERT
        assert evt.data[0].id == chat_entry["id"]
        assert evt.timestamp == 1633456789
        assert evt.session_id == "session-id-123"

    # Tests for direct Pydantic model parsing
    def test_parses_chats_upsert_event_correctly_model(self):
        chat_entry_data = {
            "id": "1234567890", "name": "Contact Name",
            "conversationTimestamp": 1633456789, "unreadCount": 2
        }
        payload = {
            "type": WebhookEventType.CHATS_UPSERT.value,
            "timestamp": 1633456789,
            "data": [chat_entry_data],
            "sessionId": "session-id-123"
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.CHATS_UPSERT
        assert isinstance(evt.data, list)
        assert evt.data[0].id == chat_entry_data["id"]
        assert evt.data[0].name == chat_entry_data["name"]
        assert evt.timestamp == 1633456789
        assert evt.session_id == "session-id-123"

    def test_parses_chats_update_event_correctly_model(self):
        chat_update_data = {
            "id": "1234567890", "unreadCount": 0, "conversationTimestamp": 1633456789
        }
        payload = {
            "type": WebhookEventType.CHATS_UPDATE.value,
            "timestamp": 1633456789,
            "data": [chat_update_data]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.CHATS_UPDATE
        assert evt.data[0].unread_count == chat_update_data["unreadCount"]

    def test_parses_chats_delete_event_correctly_model(self):
        payload = {
            "type": WebhookEventType.CHATS_DELETE.value,
            "timestamp": 1633456789,
            "data": ["1234567890"]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.CHATS_DELETE
        assert evt.data == ["1234567890"]

    def test_parses_groups_upsert_event_correctly_model(self):
        participant1_data = {"jid": "1234567890", "isAdmin": True, "isSuperAdmin": True}
        group_data = {
            "jid": "123456789-987654321@g.us", "subject": "Group Name", "creation": 1633456700,
            "owner": "1234567890", "desc": "Group description", "participants": [participant1_data]
        }
        payload = {
            "type": WebhookEventType.GROUPS_UPSERT.value,
            "timestamp": 1633456789,
            "data": [group_data]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.GROUPS_UPSERT
        assert evt.data[0].jid == group_data["jid"]
        assert evt.data[0].participants[0].is_admin == True

    def test_parses_groups_update_event_correctly_model(self):
        group_update_data = {
            "jid": "123456789-987654321@g.us", 
            "subject": "Test Group Subject",
            "announce": True, 
            "restrict": False
        }
        payload = {
            "type": WebhookEventType.GROUPS_UPDATE.value,
            "timestamp": 1633456789,
            "data": [group_update_data]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.GROUPS_UPDATE
        assert evt.data[0].announce == group_update_data["announce"]

    def test_parses_group_participants_update_event_correctly_model(self):
        participants_update_data = {
            "jid": "123456789-987654321@g.us", "participants": ["1234567890"], "action": "add"
        }
        payload = {
            "type": WebhookEventType.GROUP_PARTICIPANTS_UPDATE.value,
            "timestamp": 1633456789,
            "data": participants_update_data
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.GROUP_PARTICIPANTS_UPDATE
        assert evt.data.action == participants_update_data["action"]

    def test_parses_contacts_upsert_event_correctly_model(self):
        contact_data = {
            "jid": "1234567890", "name": "Contact Name", "notify": "Contact Display Name",
            "verifiedName": "Verified Business Name", "status": "Hey there! I am using WhatsApp."
        }
        payload = {
            "type": WebhookEventType.CONTACTS_UPSERT.value,
            "timestamp": 1633456789,
            "data": [contact_data]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.CONTACTS_UPSERT
        assert evt.data[0].verified_name == contact_data["verifiedName"]

    def test_parses_contacts_update_event_correctly_model(self):
        contact_update_data = {
            "jid": "1234567890",
            "imgUrl": "https://pps.whatsapp.net/v/t61.24694-24/some.jpg"
        }
        payload = {
            "type": WebhookEventType.CONTACTS_UPDATE.value,
            "timestamp": 1633456789,
            "data": [contact_update_data]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.CONTACTS_UPDATE
        assert evt.data[0].img_url == contact_update_data["imgUrl"]
        assert evt.data[0].jid == contact_update_data["jid"]

    def test_parses_messages_upsert_event_correctly_model(self):
        message_key_data = {"remoteJid": "remote@s.whatsapp.net", "id": "ABC", "fromMe": False}
        message_content_data = {"text": "Hello"}
        messages_upsert_data = {
            "key": message_key_data, "messageTimestamp": 1633456789,
            "message": message_content_data, "pushName": "Sender Name"
        }
        payload = {
            "type": WebhookEventType.MESSAGES_UPSERT.value,
            "timestamp": 1633456789,
            "data": messages_upsert_data # Note: Node.js data was List[MessageUpsertData]
                                        # Python model in webhook.py is MessagesUpsertData (singular)
                                        # Test adapted to singular data based on Python model def.
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.MESSAGES_UPSERT
        assert evt.data.key.id == message_key_data["id"]

    def test_parses_messages_update_event_correctly_model(self):
        message_key_data = {"remoteJid": "remote@s.whatsapp.net", "id": "ABC", "fromMe": True}
        message_update_data = {"status": "read"}
        messages_update_data_entry = {"key": message_key_data, "update": message_update_data}
        payload = {
            "type": WebhookEventType.MESSAGES_UPDATE.value,
            "timestamp": 1633456789,
            "data": [messages_update_data_entry]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.MESSAGES_UPDATE
        assert evt.data[0].key.id == message_key_data["id"]
        assert evt.data[0].update.status == message_update_data["status"]

    def test_parses_messages_delete_event_correctly_model(self):
        message_key_data = {"remoteJid": "remote@s.whatsapp.net", "id": "DEF", "fromMe": False}
        payload = {
            "type": WebhookEventType.MESSAGES_DELETE.value,
            "timestamp": 1633456789,
            "data": {"keys": [message_key_data]}
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.MESSAGES_DELETE
        assert evt.data.keys[0].id == message_key_data["id"]

    def test_parses_message_sent_event_correctly_model(self):
        message_sent_data = {
            "key": {"remoteJid": "r@w.net", "id": "MSGID", "fromMe": True}, # Added key to match model
            "status": "sent", "timestamp": 1633456789
        }
        payload = {
            "type": WebhookEventType.MESSAGE_SENT.value,
            "timestamp": 1633456789,
            "data": message_sent_data
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.MESSAGE_SENT
        assert evt.data.status == message_sent_data["status"]
        assert evt.data.key.id == message_sent_data["key"]["id"]

    def test_parses_message_receipt_update_event_correctly_model(self):
        receipt_data = {"userJid": "u@w.net", "status": "read", "t": 1633456800}
        message_key_data = {"remoteJid": "r@w.net", "id": "MSGID", "fromMe": True}
        message_receipt_update_data_entry = {"key": message_key_data, "receipt": receipt_data}
        payload = {
            "type": WebhookEventType.MESSAGE_RECEIPT_UPDATE.value,
            "timestamp": 1633456789,
            "data": [message_receipt_update_data_entry] # Data is a list
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.MESSAGE_RECEIPT_UPDATE
        assert evt.data[0].key.id == message_key_data["id"]
        assert evt.data[0].receipt.status == receipt_data["status"]

    def test_parses_messages_reaction_event_correctly_model(self):
        reaction_key_data = {"remoteJid": "chat@g.us", "id": "REACTION_ID", "fromMe": False}
        reaction_data = {"text": "👍", "key": reaction_key_data}
        message_key_data = {"remoteJid": "user@s.whatsapp.net", "id": "MSG_ID", "fromMe": True}
        messages_reaction_data_entry = {"key": message_key_data, "reaction": reaction_data}
        payload = {
            "type": WebhookEventType.MESSAGES_REACTION.value,
            "timestamp": 1633456789,
            "data": [messages_reaction_data_entry]
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.MESSAGES_REACTION
        assert evt.data[0].key.id == message_key_data["id"]
        assert evt.data[0].reaction.text == reaction_data["text"]

    def test_parses_session_status_event_correctly_model(self):
        session_status_data = {"status": "CONNECTED", "reason": "User initiated connection"}
        payload = {
            "type": WebhookEventType.SESSION_STATUS.value,
            "timestamp": 1633456789,
            "data": session_status_data
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.SESSION_STATUS
        assert evt.data.status == session_status_data["status"]

    def test_parses_qr_code_updated_event_correctly_model(self):
        qr_code_updated_data = {"qr": "new_qr_code_string", "sessionId": "123-456-789"}
        payload = {
            "type": WebhookEventType.QRCODE_UPDATED.value,
            "timestamp": 1633456789,
            "data": qr_code_updated_data
        }
        adapter = TypeAdapter(WasenderWebhookEvent)
        evt = adapter.validate_python(payload)
        assert evt.type == WebhookEventType.QRCODE_UPDATED
        assert evt.data.qr == qr_code_updated_data["qr"]
        assert evt.data.session_id == qr_code_updated_data["sessionId"]

# Client specific fixtures and tests - REMOVED
# @pytest.fixture
# def mock_client(): ...
# @pytest.fixture
# def mock_webhook_response(): ...
# @pytest.mark.asyncio
# async def test_set_webhook(mock_client, mock_webhook_response): ...
# @pytest.mark.asyncio
# async def test_get_webhook_config(mock_client, mock_webhook_response): ...
# @pytest.mark.asyncio
# async def test_delete_webhook(mock_client, mock_webhook_response): ... 