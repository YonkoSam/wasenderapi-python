import json
from enum import Enum
from typing import Dict, Any, Optional, List, Union, TypeVar, Generic, Literal
from pydantic import BaseModel, Field
from .groups import GroupParticipant

WEBHOOK_SIGNATURE_HEADER = 'x-webhook-signature'

def verify_wasender_webhook_signature(
    request_signature: Optional[str],
    configured_secret: str
) -> bool:
    """Verify the webhook signature from Wasender.
    
    IMPORTANT: The current Wasender documentation example shows a direct string comparison
    for the signature and secret. This is a very simple verification method. Most webhook 
    systems use HMAC-SHA256 or similar cryptographic hashes for security.
    
    Please VERIFY with Wasender's official documentation or support if this simple string
    comparison is indeed the correct and only method for signature verification.
    """
    if not request_signature or not configured_secret:
        return False
    return request_signature == configured_secret

class WasenderWebhookEventType(str, Enum):
    # Chat Events
    CHATS_UPSERT = 'chats.upsert'
    CHATS_UPDATE = 'chats.update'
    CHATS_DELETE = 'chats.delete'
    # Group Events
    GROUPS_UPSERT = 'groups.upsert'
    GROUPS_UPDATE = 'groups.update'
    GROUP_PARTICIPANTS_UPDATE = 'group-participants.update'
    # Contact Events
    CONTACTS_UPSERT = 'contacts.upsert'
    CONTACTS_UPDATE = 'contacts.update'
    # Message Events
    MESSAGES_UPSERT = 'messages.upsert'      # New upcoming message will include fromMe to identify if it's a sent or received message
    MESSAGES_UPDATE = 'messages.update'      # Message status update
    MESSAGES_DELETE = 'messages.delete'
    MESSAGES_REACTION = 'messages.reaction'
    # Message Receipt
    MESSAGE_RECEIPT_UPDATE = 'message-receipt.update'
    # Session Events
    MESSAGE_SENT = 'message.sent'          # Message successfully sent
    SESSION_STATUS = 'session.status'
    QRCODE_UPDATED = 'qrcode.updated'

EventType = TypeVar('EventType', bound=WasenderWebhookEventType)
DataType = TypeVar('DataType')

class BaseWebhookEvent(BaseModel, Generic[EventType, DataType]):
    type: EventType
    timestamp: Optional[int] = None
    data: DataType
    session_id: Optional[str] = Field(None, alias="sessionId")

    def __getitem__(self, key: str) -> Any:
        try:
            return getattr(self, key)
        except AttributeError:
            for field_name, field_model in self.model_fields.items():
                if field_model.alias == key:
                    return getattr(self, field_name)
            raise KeyError(key)

class MessageKey(BaseModel):
    id: str
    from_me: bool = Field(..., alias="fromMe")
    remote_jid: str = Field(..., alias="remoteJid")
    participant: Optional[str] = None

# Chat Event Models
class ChatEntry(BaseModel):
    id: str
    name: Optional[str] = None
    conversation_timestamp: Optional[int] = Field(None, alias="conversationTimestamp")
    unread_count: Optional[int] = Field(None, alias="unreadCount")
    mute_end_time: Optional[int] = Field(None, alias="muteEndTime")
    is_spam: Optional[bool] = Field(None, alias="isSpam")

# Group Event Models
class GroupMetadata(BaseModel):
    jid: str
    subject: str
    creation: Optional[int] = None
    owner: Optional[str] = None
    desc: Optional[str] = None
    participants: Optional[List[GroupParticipant]] = None
    announce: Optional[bool] = None
    restrict: Optional[bool] = None

class GroupParticipantsUpdateData(BaseModel):
    jid: str
    participants: List[Union[str, GroupParticipant]]
    action: Literal['add', 'remove', 'promote', 'demote']

# Contact Event Models
class ContactEntry(BaseModel):
    jid: str
    name: Optional[str] = None
    notify: Optional[str] = None
    verified_name: Optional[str] = Field(None, alias="verifiedName")
    status: Optional[str] = None
    img_url: Optional[str] = Field(None, alias="imgUrl")

# Message Event Models
class MessageContent(BaseModel):
    conversation: Optional[str] = None
    image_message: Optional[Dict[str, Any]] = Field(None, alias="imageMessage")
    video_message: Optional[Dict[str, Any]] = Field(None, alias="videoMessage")
    document_message: Optional[Dict[str, Any]] = Field(None, alias="documentMessage")
    audio_message: Optional[Dict[str, Any]] = Field(None, alias="audioMessage")
    sticker_message: Optional[Dict[str, Any]] = Field(None, alias="stickerMessage")
    contact_message: Optional[Dict[str, Any]] = Field(None, alias="contactMessage")
    location_message: Optional[Dict[str, Any]] = Field(None, alias="locationMessage")

class MessagesUpsertData(BaseModel):
    key: MessageKey
    message: Optional[MessageContent] = None
    push_name: Optional[str] = Field(None, alias="pushName")
    message_timestamp: Optional[int] = Field(None, alias="messageTimestamp")

class MessageUpdate(BaseModel):
    status: str

class MessagesUpdateDataEntry(BaseModel):
    key: MessageKey
    update: MessageUpdate

class MessagesDeleteData(BaseModel):
    keys: List[MessageKey]

class Reaction(BaseModel):
    text: str
    key: MessageKey
    sender_timestamp_ms: Optional[str] = Field(None, alias="senderTimestampMs")
    read: Optional[bool] = None

class MessagesReactionDataEntry(BaseModel):
    key: MessageKey
    reaction: Reaction

# Message Receipt Models
class Receipt(BaseModel):
    user_jid: str = Field(..., alias="userJid")
    status: str
    t: Optional[int] = None

class MessageReceiptUpdateDataEntry(BaseModel):
    key: MessageKey
    receipt: Receipt

# Session Event Models
class MessageSentData(BaseModel):
    key: MessageKey
    message: Optional[MessageContent] = None
    status: Optional[str] = None

class SessionStatusData(BaseModel):
    status: Literal["CONNECTED", "DISCONNECTED", "NEED_SCAN", "CONNECTING", "LOGGED_OUT", "EXPIRED"]
    session_id: Optional[str] = Field(None, alias="sessionId")
    reason: Optional[str] = None

class QrCodeUpdatedData(BaseModel):
    qr: str
    session_id: Optional[str] = Field(None, alias="sessionId")

# Define specific event types using the generic BaseWebhookEvent
ChatsUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CHATS_UPSERT], List[ChatEntry]]
ChatsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CHATS_UPDATE], List[ChatEntry]]
ChatsDeleteEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CHATS_DELETE], List[str]]

GroupsUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.GROUPS_UPSERT], List[GroupMetadata]]
GroupsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.GROUPS_UPDATE], List[GroupMetadata]]
GroupParticipantsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.GROUP_PARTICIPANTS_UPDATE], GroupParticipantsUpdateData]

ContactsUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CONTACTS_UPSERT], List[ContactEntry]]
ContactsUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.CONTACTS_UPDATE], List[ContactEntry]]

MessagesUpsertEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_UPSERT], MessagesUpsertData]
MessagesUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_UPDATE], List[MessagesUpdateDataEntry]]
MessagesDeleteEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_DELETE], MessagesDeleteData]
MessagesReactionEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGES_REACTION], List[MessagesReactionDataEntry]]

MessageReceiptUpdateEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGE_RECEIPT_UPDATE], List[MessageReceiptUpdateDataEntry]]
MessageSentEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.MESSAGE_SENT], MessageSentData]
SessionStatusEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.SESSION_STATUS], SessionStatusData]
QrCodeUpdatedEvent = BaseWebhookEvent[Literal[WasenderWebhookEventType.QRCODE_UPDATED], QrCodeUpdatedData]

# Discriminated union of all specific event types for parsing
WasenderWebhookEvent = Union[
    ChatsUpsertEvent, ChatsUpdateEvent, ChatsDeleteEvent,
    GroupsUpsertEvent, GroupsUpdateEvent, GroupParticipantsUpdateEvent,
    ContactsUpsertEvent, ContactsUpdateEvent,
    MessagesUpsertEvent, MessagesUpdateEvent, MessagesDeleteEvent, MessagesReactionEvent,
    MessageReceiptUpdateEvent, MessageSentEvent, SessionStatusEvent, QrCodeUpdatedEvent
]

# Helper types for partial updates if needed (conceptual)
class PartialChatEntry(ChatEntry):
    id: Optional[str] = None
    name: Optional[str] = None
    conversation_timestamp: Optional[int] = Field(None, alias="conversationTimestamp")
    unread_count: Optional[int] = Field(None, alias="unreadCount")
    mute_end_time: Optional[int] = Field(None, alias="muteEndTime")
    is_spam: Optional[bool] = Field(None, alias="isSpam")

class PartialGroupMetadata(GroupMetadata):
    jid: Optional[str] = None
    subject: Optional[str] = None
    # ... make other fields optional

class PartialContactEntry(ContactEntry):
    jid: Optional[str] = None
    # ... make other fields optional 