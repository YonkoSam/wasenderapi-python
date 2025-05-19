from typing import TypeAlias
from .models import TextOnlyMessage, WasenderSendResult

# Represents a text message specifically for sending to a WhatsApp Channel.
# Currently, only text messages are supported for channels.
# The `to` field must be a valid Channel JID (e.g., '1234567890@newsletter').
ChannelTextMessage: TypeAlias = TextOnlyMessage

# The result of sending a message to a channel is the same as a standard send operation.
SendChannelMessageResult: TypeAlias = WasenderSendResult 