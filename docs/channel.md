# Wasender Python SDK: Sending Messages to WhatsApp Channels

This document explains how to send messages to WhatsApp Channels using the Wasender Python SDK.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Overview

Sending a message to a WhatsApp Channel utilizes the existing generic `client.send()` method from the Wasender Python SDK. The key differences compared to sending a message to a regular user or group are:

1.  **Recipient (`to` field):** The `to` field in the message payload must be the unique **Channel ID** (also known as Channel JID). This typically looks like `12345678901234567890@newsletter`.
2.  **Message Type Restriction:** Currently, the Wasender API (and thus the SDK) generally **only supports sending text messages** to channels. Attempting to send other message types (images, videos, documents, etc.) to channels via the standard `send()` method may not be supported or could result in an API error. Always refer to the latest official Wasender API documentation for channel messaging capabilities.

## Prerequisites

1.  **Obtain a Channel ID:** You need the specific ID of the channel you want to send a message to. One way to obtain a Channel ID is by listening for webhook events (e.g., `message.upsert` or `message.created` if your provider supports it for channels), as this event data for messages originating from a channel will include the channel's JID.
2.  **SDK Initialization:** Ensure the Wasender Python SDK is correctly initialized in your project. This involves:
    *   Installing the SDK: `pip install wasenderapi`
    *   Setting the environment variable `WASENDER_API_KEY`. This API key should correspond to the specific WhatsApp session you intend to use for sending channel messages.
    *   Creating an instance of `WasenderClient`.
    (Refer to `README.md` or `docs/messages.md` for detailed SDK initialization examples.)

## How to Send a Message to a Channel

You will use the `client.send()` method with a `TextPayload` Pydantic model. The Python SDK also provides a specific type alias `wasenderapi.models.channel.ChannelTextMessage` which is an alias for `TextPayload`, intended for conceptual clarity when working with channels.

### Python Model for Channel Messages

The relevant Pydantic model from `wasenderapi.models.channel` is:

```python
# From wasenderapi/models/channel.py
# (Conceptual - actual import would be from wasenderapi.models)
from ..models.message import TextPayload # Relative import path for illustration

ChannelTextMessage = TextPayload
```
This means you can directly use `TextPayload` from `wasenderapi.models` when constructing your message for a channel.

### Code Example

Here's how you can send a text message to a WhatsApp Channel in Python:

```python
# examples/send_channel_message.py
import asyncio
import os
import logging
from datetime import datetime
from typing import Optional

from wasenderapi import WasenderClient
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    TextPayload, # Equivalent to ChannelTextMessage
    WasenderSendResult,
    RateLimitInfo
)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SDK Initialization (Minimal for this example) ---
api_key = os.getenv("WASENDER_API_KEY") # API Key for the session sending the message

if not api_key:
    logger.error("Error: WASENDER_API_KEY environment variable is not set.")
    exit(1)

# For sending messages via an existing session, typically only the session's API key is needed.
client = WasenderClient(api_key=api_key)

# The personal_access_token is generally used for account-level session management (create, list, delete sessions),
# not for sending messages through an already established session.
# # personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN") # Token for account-level session operations
# # client = WasenderClient(api_key=api_key, personal_access_token=personal_access_token) # If needed for specific advanced scenarios or different auth models

# --- Helper to log rate limits (can be imported from a common utils module) ---
def log_rate_limit_info(rate_limit: Optional[RateLimitInfo]):
    if rate_limit:
        reset_time_str = datetime.fromtimestamp(rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if rate_limit.reset_timestamp else "N/A"
        logger.info(
            f"Rate Limit Info: Remaining = {rate_limit.remaining}, Limit = {rate_limit.limit}, Resets at = {reset_time_str}"
        )
    else:
        logger.info("Rate limit information not available for this request.")

# --- Generic Error Handler (can be imported) ---
def handle_channel_api_error(error: Exception, operation: str, channel_jid: Optional[str] = None):
    target = f" for channel {channel_jid}" if channel_jid else ""
    if isinstance(error, WasenderAPIError):
        logger.error(f"API Error during {operation}{target}:")
        logger.error(f"  Message: {error.message}")
        logger.error(f"  Status Code: {error.status_code or 'N/A'}")
        if error.api_message: logger.error(f"  API Message: {error.api_message}")
        if error.error_details: logger.error(f"  Error Details: {error.error_details}")
        if error.rate_limit: log_rate_limit_info(error.rate_limit)
    else:
        logger.error(f"An unexpected error occurred during {operation}{target}: {error}")

# --- Main function to send message to channel ---
async def send_message_to_channel_example(channel_jid: str, message_text: str):
    logger.info(f"\\n--- Attempting to Send Message to Channel: {channel_jid} ---")
    if not channel_jid:
        logger.error("Channel JID is required.")
        return
    if not message_text:
        logger.error("Message text is required.")
        return

    # Use TextPayload (aliased as ChannelTextMessage in the SDK for conceptual clarity)
    channel_payload = TextPayload(
        to=channel_jid,
        text=message_text,
        # messageType defaults to "text" in TextPayload model, so explicit set is optional
        # but good for clarity with channels: message_type="text"
    )

    try:
        result = await client.send(payload=channel_payload)
        send_result: WasenderSendResult = result.response.data
        
        logger.info(f"Message sent to channel {channel_jid} successfully.")
        logger.info(f"  Message ID: {send_result.message_id}")
        logger.info(f"  Status: {send_result.status}")
        if send_result.detail:
            logger.info(f"  Detail: {send_result.detail}")
        
        log_rate_limit_info(result.rate_limit)

    except Exception as e:
        handle_channel_api_error(e, "sending message", channel_jid=channel_jid)

async def main():
    # Replace with the actual Channel ID you want to send a message to
    target_channel_jid = "12345678901234567890@newsletter" # Example JID
    message = "Hello Channel! This is a test message from the Python SDK."

    if target_channel_jid == "12345678901234567890@newsletter":
        logger.warning("Please replace `target_channel_jid` with a real Channel ID before running.")
    else:
        await send_message_to_channel_example(target_channel_jid, message)
    
    # Example for another channel or message:
    # another_channel_jid = "09876543210987654321@newsletter"
    # await send_message_to_channel_example(another_channel_jid, "Another important update!")

if __name__ == "__main__":
    # Before running, ensure WASENDER_API_KEY is set in your environment.
    # Also, replace target_channel_jid in main() with a valid Channel ID.
    logger.info("Starting channel message example. Ensure JID and API Key are set.")
    asyncio.run(main())

```

### Key Points from the Example:

-   **`to`**: Set to the `target_channel_jid`.
-   **`TextPayload`**: Used to construct the message. The `message_type` attribute within `TextPayload` defaults to `"text"`, which is what channels typically require. You can explicitly set `message_type="text"` for clarity if desired.
-   **`text`**: Contains the content of your message.
-   The example includes minimal SDK initialization, error handling, and rate limit logging.

## Important Considerations

-   **Channel ID Accuracy:** Ensure the Channel ID (ending in `@newsletter`) is correct. Sending to an incorrect ID will fail.
-   **Message Content:** As emphasized, typically only text messages are supported for channels via this standard send method. Sending other types will likely result in an API error. Always verify with current API documentation.
-   **API Limitations:** The ability to send messages to channels, supported message types, and any other restrictions are determined by the underlying Wasender API. Refer to the official Wasender API documentation for the most up-to-date information.
-   **Webhook for Channel IDs:** Using webhooks to listen for relevant message events (like `message.created` or `message.upsert`) is a practical way to discover Channel IDs your connected number interacts with or is part of, especially if these channels are not self-created.

This guide should provide you with the necessary information to send text messages to WhatsApp Channels using the Wasender Python SDK.
