# Wasender Python SDK: Sending Messages to WhatsApp Channels

This document explains how to send messages to WhatsApp Channels using the Wasender Python SDK.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Overview

Sending a message to a WhatsApp Channel is straightforward with the Wasender Python SDK. You will typically use the `client.send_text()` helper method.

1.  **Recipient (`to` field):** The `to` field in the `send_text()` method must be the unique **Channel ID** (also known as Channel JID). This typically looks like `12345678901234567890@newsletter`.
2.  **Message Type Restriction:** Currently, the Wasender API (and thus the SDK) generally **only supports sending text messages** to channels using the standard helper methods. Attempting to send other message types might not be supported. Always refer to the latest official Wasender API documentation for channel messaging capabilities.

## Prerequisites

1.  **Obtain a Channel ID:** You need the specific ID of the channel you want to send a message to.
2.  **SDK Initialization:** Ensure the Wasender Python SDK is correctly initialized.
    *   Installing the SDK: `pip install wasenderapi`
    *   Setting the environment variable `WASENDER_API_KEY`.
    *   Creating an instance of `WasenderAsyncClient` (or `WasenderSyncClient`).

## How to Send a Message to a Channel

Use the `client.send_text()` method.

### Code Example

Here's how you can send a text message to a WhatsApp Channel in Python using the async client:

```python
# examples/send_channel_message.py
import asyncio
import os
import logging
from datetime import datetime
from typing import Optional

# Corrected imports
from wasenderapi import create_async_wasender, WasenderAsyncClient # For type hinting
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    WasenderSendResult, # Result from send_text
    RateLimitInfo
    # RetryConfig could be imported here if configuring retries
)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SDK Initialization (Minimal for this example) ---
api_key = os.getenv("WASENDER_API_KEY")

if not api_key:
    logger.error("Error: WASENDER_API_KEY environment variable not set.")
    api_key = "YOUR_API_KEY_PLACEHOLDER" # Use a placeholder for docs

# Initialize async client
async_client = create_async_wasender(api_key=api_key)

# --- Helper to log rate limits (can be imported from a common utils module) ---
# (Assuming log_rate_limit_info and handle_channel_api_error are defined as in the original doc or a shared util)

# --- Main function to send message to channel ---
async def send_message_to_channel_example(client: WasenderAsyncClient, channel_jid: str, message_text: str):
    logger.info(f"\n--- Attempting to Send Message to Channel: {channel_jid} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for send_message_to_channel {channel_jid}: API key is placeholder.")
        return
    if not channel_jid:
        logger.error("Channel JID is required.")
        return
    if not message_text:
        logger.error("Message text is required.")
        return

    try:
        # Use the send_text helper method
        response: WasenderSendResult = await client.send_text(
            to=channel_jid,
            text_body=message_text
        )
        
        logger.info(f"Message sent to channel {channel_jid} successfully.")
        if response.response and response.response.data:
            logger.info(f"  Message ID: {response.response.data.message_id}")
        logger.info(f"  Status: {response.response.message}")
        
        # log_rate_limit_info(response.rate_limit) # Assuming log_rate_limit_info is defined
        if response.rate_limit:
            logger.info(f"  Rate limit remaining: {response.rate_limit.remaining}")

    except WasenderAPIError as e:
        # handle_channel_api_error(e, "sending message", channel_jid=channel_jid) # Assuming defined
        logger.error(f"API Error sending to channel {channel_jid}: {e.message}")
    except Exception as e:
        logger.error(f"Unexpected error sending to channel {channel_jid}: {e}")

async def main():
    # Replace with the actual Channel ID you want to send a message to
    target_channel_jid = "12345678901234567890@newsletter" # Example JID
    message = "Hello Channel! This is a test message from the Python SDK."

    if target_channel_jid == "12345678901234567890@newsletter" or async_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning("Please replace `target_channel_jid` with a real Channel ID and ensure API key is set before running.")
    else:
        async with async_client: # Use async context manager for the client
            await send_message_to_channel_example(async_client, target_channel_jid, message)
    
if __name__ == "__main__":
    logger.info("Starting channel message example. Ensure JID and API Key are set.")
    asyncio.run(main())

```

### Key Points from the Example:

-   **`create_async_wasender`**: Used to initialize the client.
-   **`client.send_text(to=channel_jid, text_body=message_text)`**: The recommended way to send text to a channel.
-   The example includes minimal SDK initialization and basic error logging.

## Important Considerations

-   **Channel ID Accuracy:** Ensure the Channel ID (ending in `@newsletter`) is correct. Sending to an incorrect ID will fail.
-   **Message Content:** As emphasized, typically only text messages are supported for channels via this standard send method. Sending other types will likely result in an API error. Always verify with current API documentation.
-   **API Limitations:** The ability to send messages to channels, supported message types, and any other restrictions are determined by the underlying Wasender API. Refer to the official Wasender API documentation for the most up-to-date information.
-   **Webhook for Channel IDs:** Using webhooks to listen for relevant message events (like `message.created` or `message.upsert`) is a practical way to discover Channel IDs your connected number interacts with or is part of, especially if these channels are not self-created.

This guide should provide you with the necessary information to send text messages to WhatsApp Channels using the Wasender Python SDK.
