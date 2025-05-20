# Wasender API Python SDK

**Python SDK Author:** YonkoSam
**Original Node.js SDK Author:** Shreshth Arora

[![PyPI Version](https://img.shields.io/pypi/v/wasenderapi?style=flat)](https://pypi.org/project/wasenderapi/)
[![PyPI Downloads](https://img.shields.io/pypi/dm/wasenderapi?style=flat)](https://pypi.org/project/wasenderapi/)
[![License](https://img.shields.io/pypi/l/wasenderapi?style=flat)](LICENSE)
[![Python](https://img.shields.io/badge/written%20in-Python-blue?style=flat&logo=python)](https://www.python.org/)
[![CI](https://github.com/YOUR_USERNAME/YOUR_PYTHON_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YonkoSam/wasenderapi-python/actions/workflows/ci.yml)

A lightweight and robust Python SDK for interacting with the Wasender API ([https://www.wasenderapi.com](https://www.wasenderapi.com)). This SDK simplifies sending various types of WhatsApp messages, managing contacts and groups, handling session statuses, and processing incoming webhooks.

## Features

- **Pydantic Models:** Leverages Pydantic for robust request/response validation and serialization, especially for the generic `send()` method and webhook event parsing.
- **Message Sending:**
  - Simplified helper methods (e.g., `client.send_text(to="...", text_body="...")`, `client.send_image(to="...", url="...", caption="...")`) that accept direct parameters for common message types.
  - Generic `client.send(payload: BaseMessage)` method for advanced use cases or less common message types, accepting a Pydantic model.
  - Support for text, image, video, document, audio, sticker, contact card, and location messages.
- **Contact Management:** List, retrieve details, get profile pictures, block, and unblock contacts.
- **Group Management:** List groups, fetch metadata, manage participants (add/remove), and update group settings.
- **Channel Messaging:** Send text messages to WhatsApp Channels.
- **Session Management:** Create, list, update, delete sessions, connect/disconnect, get QR codes, and check session status.
- **Webhook Handling:** Securely verify and parse incoming webhook events from Wasender using Pydantic models.
- **Error Handling:** Comprehensive `WasenderAPIError` class with detailed error information.
- **Rate Limiting:** Access to rate limit information on API responses.
- **Retry Mechanism:** Optional automatic retries for rate-limited requests (HTTP 429) via `RetryConfig`.
- **Customizable HTTP Client:** Allows providing a custom `httpx.AsyncClient` instance for the asynchronous client.

## Prerequisites

- Python (version 3.8 or higher recommended).
- A Wasender API Key from [https://www.wasenderapi.com](https://www.wasenderapi.com).
- If using webhooks:
  - A publicly accessible HTTPS URL for your webhook endpoint.
  - A Webhook Secret generated from the Wasender dashboard.

## Installation

```bash
pip install wasenderapi
```

## SDK Initialization

The SDK now provides both a synchronous and an asynchronous client.

### Synchronous Client

```python
import os
from wasenderapi import WasenderSyncClient, create_sync_wasender
from wasenderapi.models import RetryConfig

# Required credentials
api_key = os.getenv("WASENDER_API_KEY")
# For account-scoped endpoints like session management:
personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN") 
# For webhook verification:
webhook_secret = os.getenv("WASENDER_WEBHOOK_SECRET")     

if not api_key:
    raise ValueError("WASENDER_API_KEY environment variable not set.")

# Initialize synchronous client using the factory function
sync_client = create_sync_wasender(
    api_key=api_key,
    personal_access_token=personal_access_token, # Optional, for session management
    webhook_secret=webhook_secret,             # Optional, for webhook handling
)

# Or initialize directly
# sync_client = WasenderSyncClient(
#     api_key=api_key,
#     personal_access_token=personal_access_token,
#     webhook_secret=webhook_secret,
# )
```

### Asynchronous Client

```python
import os
import asyncio
import httpx # httpx is used by the async client
from wasenderapi import WasenderAsyncClient, create_async_wasender
from wasenderapi.models import RetryConfig

# Required credentials (same as sync client)
api_key = os.getenv("WASENDER_API_KEY")
personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN")
webhook_secret = os.getenv("WASENDER_WEBHOOK_SECRET")

if not api_key:
    raise ValueError("WASENDER_API_KEY environment variable not set.")

async def main():
    # Initialize asynchronous client using the factory function
    # You can optionally pass your own httpx.AsyncClient instance
    # custom_http_client = httpx.AsyncClient()
    async_client = create_async_wasender(
        api_key=api_key,
        personal_access_token=personal_access_token,
        webhook_secret=webhook_secret,
    )

    # Or initialize directly
    # async_client = WasenderAsyncClient(
    #     api_key=api_key,
    #     personal_access_token=personal_access_token,
    #     webhook_secret=webhook_secret,
    # )

    # It's recommended to use the async client as a context manager
    # to ensure the underlying httpx.AsyncClient is properly closed.
    async with async_client:
        # Use the client for API calls
        # contacts = await async_client.get_contacts()
        # print(contacts)
        pass

    # If not using 'async with', and if you didn't provide your own httpx_client,
    # you might need to manually close the client if it created one internally,
    # though the current implementation aims to manage this with __aenter__/__aexit__.
    # For safety with direct instantiation without 'async with':
    # if async_client._created_http_client and async_client._http_client:
    #     await async_client._http_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

Using the SDK involves calling methods on the initialized client instance. For example, to send a message with the synchronous client:

```python
from wasenderapi.errors import WasenderAPIError

try:
    response = sync_client.send_text(to="1234567890", text_body="Hello from Python SDK!")
    print(f"Message sent successfully: {response.response.data.message_id}")
    if response.rate_limit:
        print(f"Rate limit info: Remaining {response.rate_limit.remaining}")
except WasenderAPIError as e:
    print(f"API Error: {e.message} (Status: {e.status_code})")
```

For the asynchronous client:

```python
import asyncio
from wasenderapi.errors import WasenderAPIError

# Assuming async_client is initialized within an async context as shown above
async def send_async_text_message(client):
    try:
        response = await client.send_text(to="1234567890", text_body="Hello from Async Python SDK!")
        print(f"Message sent successfully: {response.response.data.message_id}")
        if response.rate_limit:
            print(f"Rate limit info: Remaining {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"API Error: {e.message} (Status: {e.status_code})")

# async def main_async_send_example(): # Renamed to avoid conflict with earlier main
#     # ... (async_client initialization as shown in SDK Initialization section)
#     # Example: 
#     # api_key = os.getenv("WASENDER_API_KEY")
#     # async_client = create_async_wasender(api_key=api_key)
#     async with async_client: # Ensure client is available in this scope
#         await send_async_text_message(async_client)

# if __name__ == "__main__":
#     asyncio.run(main_async_send_example()) # Example of how to run it
```

## Usage Overview

Using the SDK involves calling methods on the initialized client instance. For example, to send a message with the synchronous client:

```python
from wasenderapi.errors import WasenderAPIError

try:
    response = sync_client.send_text(to="1234567890", text_body="Hello from Python SDK!")
    print(f"Message sent successfully: {response.response.data.message_id}")
    if response.rate_limit:
        print(f"Rate limit info: Remaining {response.rate_limit.remaining}")
except WasenderAPIError as e:
    print(f"API Error: {e.message} (Status: {e.status_code})")
```

## Authentication

The SDK supports two types of authentication tokens passed during client initialization (e.g., to `create_sync_wasender` or `create_async_wasender`):

1. **API Key (`api_key`)** (Required for most API calls)
   - Used for most endpoints, typically those interacting with a specific WhatsApp session (e.g., sending messages, getting contacts for that session).
   - This is the primary token for session-specific operations.

2. **Personal Access Token (`personal_access_token`)** (Optional; for account-scoped endpoints)
   - Used for account management endpoints that are not tied to a single session, such as listing all WhatsApp sessions under your account, creating new sessions, etc.
   - If you only work with a single session and its API key, you might not need this.

The client prioritizes tokens passed directly to its constructor/factory function.

## Core Concepts

### Message Sending: Helpers vs. Generic `send()`

The SDK offers two main ways to send messages:

1.  **Specific Helper Methods (Recommended for most common cases):**
    Methods like `client.send_text()`, `client.send_image()`, `client.send_video()`, etc., provide a straightforward way to send common message types.
    - They accept direct parameters relevant to the message type (e.g., `to: str`, `text_body: str` for `send_text`; `to: str`, `url: str`, `caption: Optional[str]` for `send_image`).
    - These methods internally construct the necessary payload structure and Pydantic models.
    - They simplify the sending process as you don't need to manually create payload objects.
    - Example: `sync_client.send_text(to="PHONE_NUMBER", text_body="Hello!")`
    - Example: `await async_client.send_image(to="PHONE_NUMBER", url="http://example.com/image.jpg", caption="My Image")`

2.  **Generic `client.send(payload: BaseMessage)` Method:**
    - This method provides maximum flexibility and is used for:
        - Sending message types that might not have dedicated helper methods.
        - Scenarios where you prefer to construct the message payload object (an instance of a class derived from `BaseMessage` in `./models.py`) yourself.
    - It requires you to import the appropriate Pydantic model for your message (e.g., `TextOnlyMessage`, `ImageMessage` from `wasenderapi.models`), instantiate it with the necessary data, and then pass it to `client.send()`.
    - Example:
      ```python
      from wasenderapi.models import TextOnlyMessage # Or ImageMessage, etc.
      # For sync client:
      # msg_payload = TextOnlyMessage(to="PHONE_NUMBER", text={"body": "Hello via generic send"})
      # response = sync_client.send(msg_payload)
      # For async client:
      # msg_payload = TextOnlyMessage(to="PHONE_NUMBER", text={"body": "Hello via generic send"})
      # response = await client.send(msg_payload)
      ```

While Pydantic models are used internally by the helper methods and are essential for the generic `send()` method and webhook event parsing, direct interaction with these models for sending common messages is now optional thanks to the simplified helper methods.

### Error Handling

API errors are raised as instances of `WasenderAPIError` (from `wasenderapi.errors`). This exception object includes attributes such as:
- `status_code` (int): The HTTP status code of the error response.
- `api_message` (Optional[str]): The error message from the Wasender API.
- `error_details` (Optional[WasenderErrorDetail]): Further details about the error, if provided by the API.
- `rate_limit` (Optional[RateLimitInfo]): Rate limit information at the time of the error.

### Rate Limiting

Successful API response objects (e.g., `WasenderSendResult`, `WasenderSession`) and `WasenderAPIError` instances may include a `rate_limit` attribute. This attribute is an instance of the `RateLimitInfo` Pydantic model (from `wasenderapi.models`) and provides details about your current API usage limits: `limit`, `remaining`, and `reset_timestamp`.

Rate limit information is primarily expected for `/send-message` related calls but might be present or `None` for other endpoints.

### Webhooks

The Python SDK provides `client.handle_webhook_event(headers: dict, raw_body: bytes, webhook_secret: Optional[str] = None)` for processing incoming webhooks. This method:
1. Verifies the webhook signature using the provided `X-Wasender-Signature` header and the `webhook_secret`.
   - The `webhook_secret` can be passed directly to this method or pre-configured on the `WasenderClient` instance during initialization.
2. Parses the validated `raw_body` (which should be the raw bytes of the request body) into a Pydantic `WasenderWebhookEvent` model (a `Union` of specific event types like `MessagesUpsertData`, `SessionStatusData`, etc., defined in `wasenderapi.webhook`).

Unlike some other SDKs, you don't need to implement a separate request adapter; simply pass the necessary request components (headers dictionary and raw body bytes) to the method.

## Usage Examples

This SDK provides a comprehensive suite of functionalities. Below is an overview with links to detailed documentation for each module. For more comprehensive information on all features, please refer to the files in the [`docs`](./docs/) directory.

### 1. Sending Messages

Send various types of messages including text, media (images, videos, documents, audio, stickers), contact cards, and location pins. The easiest way is to use the specific helper methods.

- **Detailed Documentation & Examples:** [`docs/messages.md`](./docs/messages.md)

#### Using the Synchronous Client (`WasenderSyncClient`)

```python
import os
from wasenderapi import create_sync_wasender # Or WasenderSyncClient directly
from wasenderapi.errors import WasenderAPIError

# Initialize client (ensure WASENDER_API_KEY is set)
api_key = os.getenv("WASENDER_API_KEY", "YOUR_SYNC_API_KEY")
sync_client = create_sync_wasender(api_key=api_key)

def send_sync_messages_example():
    if sync_client.api_key == "YOUR_SYNC_API_KEY":
        print("Please set your WASENDER_API_KEY to run sync examples.")
        return

    # Example 1: Sending a Text Message
    try:
        print("Sending text message (sync)...")
        response = sync_client.send_text(
            to="YOUR_RECIPIENT_PHONE", 
            text_body="Hello from Wasender Python SDK (Sync)!"
        )
        print(f"  Text message sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending text: {e.message}")

    # Example 2: Sending an Image Message
    try:
        print("Sending image message (sync)...")
        response = sync_client.send_image(
            to="YOUR_RECIPIENT_PHONE",
            url="https://picsum.photos/seed/wasenderpy_sync/300/200", # Replace with your image URL
            caption="Test Image from Sync SDK"
        )
        print(f"  Image message sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending image: {e.message}")

    # Add more examples for send_video, send_document, etc. as needed.

# To run this specific example:
# if __name__ == "__main__":
#     send_sync_messages_example()
```

#### Using the Asynchronous Client (`WasenderAsyncClient`)

```python
import asyncio
import os
from wasenderapi import create_async_wasender # Or WasenderAsyncClient directly
from wasenderapi.errors import WasenderAPIError
# from wasenderapi.models import TextOnlyMessage # Keep for generic send example if shown

# Initialize client (ensure WASENDER_API_KEY is set)
api_key = os.getenv("WASENDER_API_KEY", "YOUR_ASYNC_API_KEY")

async def send_async_messages_example(async_client):
    if async_client.api_key == "YOUR_ASYNC_API_KEY":
        print("Please set your WASENDER_API_KEY to run async examples.")
        return

    # Example 1: Sending a Text Message using helper
    try:
        print("Sending text message (async)...")
        response = await async_client.send_text(
            to="YOUR_RECIPIENT_PHONE", 
            text_body="Hello from Wasender Python SDK (Async)!"
        )
        print(f"  Text message sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending text: {e.message}")

    # Example 2: Sending an Image Message using helper
    try:
        print("Sending image message (async)...")
        response = await async_client.send_image(
            to="YOUR_RECIPIENT_PHONE",
            url="https://picsum.photos/seed/wasenderpy_async/300/200", # Replace with your image URL
            caption="Test Image from Async SDK"
        )
        print(f"  Image message sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending image: {e.message}")

    # Example 3: Sending a Text Message using generic client.send() (for comparison or advanced use)
    # from wasenderapi.models import TextOnlyMessage # Ensure import if using this
    # try:
    #     print("Sending text message via generic send (async)...")
    #     text_payload = TextOnlyMessage(
    #         to="YOUR_RECIPIENT_PHONE",
    #         text={"body": "Hello again via generic send (Async)!"} 
    #     )
    #     response = await async_client.send(text_payload)
    #     print(f"  Generic text message sent: Status {response.response.message}")
    # except WasenderAPIError as e:
    #     print(f"  Error sending generic text: {e.message}")

async def main_run_async_examples():
    # It's recommended to use the async client as a context manager.
    async_client = create_async_wasender(api_key=api_key)
    async with async_client:
        await send_async_messages_example(async_client)

# To run this specific example:
# if __name__ == "__main__":
#     if api_key == "YOUR_ASYNC_API_KEY":
#         print("Please set your WASENDER_API_KEY environment variable to run this example.")
#     else:
#         asyncio.run(main_run_async_examples())
```

### 2. Managing Contacts

Retrieve your contact list, fetch information about specific contacts, get their profile pictures, and block or unblock contacts.

- **Detailed Documentation & Examples:** [`docs/contacts.md`](./docs/contacts.md)

```python
import asyncio
import os
from wasenderapi import create_async_wasender # Use the factory for async client
from wasenderapi.errors import WasenderAPIError

# api_key = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE") # Define API key

async def manage_contacts_example():
    # Initialize client within the async function or pass it as an argument
    # This example assumes api_key is defined in the scope
    local_api_key = os.getenv("WASENDER_API_KEY", "YOUR_CONTACTS_API_KEY")
    if local_api_key == "YOUR_CONTACTS_API_KEY":
        print("Error: WASENDER_API_KEY not set for contacts example.")
        return

    async with create_async_wasender(api_key=local_api_key) as async_client:
        print("\nAttempting to fetch contacts...")
        try:
            result = await async_client.get_contacts()
            
            if result.response and result.response.data is not None:
                contacts = result.response.data
                print(f"Successfully fetched {len(contacts)} contacts.")
                if contacts:
                    first_contact = contacts[0]
                    print(f"  First contact - JID: {first_contact.jid}, Name: {first_contact.name or 'N/A'}")
            else:
                print("No contact data received.")

            if result.rate_limit: print(f"Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit}")

        except WasenderAPIError as e:
            print(f"API Error fetching contacts: {e.message}")
        except Exception as e:
            print(f"An unexpected error: {e}")

# To run this example (ensure WASENDER_API_KEY is set):
# if __name__ == "__main__":
#     asyncio.run(manage_contacts_example())
```

### 3. Managing Groups

List groups your account is part of, get group metadata, manage participants, and update group settings.

- **Detailed Documentation & Examples:** [`docs/groups.md`](./docs/groups.md)

```python
import asyncio
import os
from wasenderapi import create_async_wasender # Use the factory for async client
from wasenderapi.errors import WasenderAPIError

async def manage_groups_example():
    local_api_key = os.getenv("WASENDER_API_KEY", "YOUR_GROUPS_API_KEY")
    if local_api_key == "YOUR_GROUPS_API_KEY":
        print("Error: WASENDER_API_KEY not set for groups example.")
        return

    async with create_async_wasender(api_key=local_api_key) as async_client:
        print("\nAttempting to fetch groups...")
        try:
            groups_result = await async_client.get_groups()
            
            if groups_result.response and groups_result.response.data is not None:
                groups = groups_result.response.data
                print(f"Successfully fetched {len(groups)} groups.")
                
                if groups:
                    first_group = groups[0]
                    print(f"  First group - JID: {first_group.jid}, Subject: {first_group.subject}")

                    # Example: Get metadata for the first group
                    print(f"  Fetching metadata for group: {first_group.jid}...")
                    try:
                        metadata_result = await async_client.get_group_metadata(group_jid=first_group.jid)
                        if metadata_result.response and metadata_result.response.data:
                            metadata = metadata_result.response.data
                            participant_count = len(metadata.participants) if metadata.participants else 0
                            print(f"    Group Subject: {metadata.subject}, Participants: {participant_count}")
                        else:
                            print(f"    Could not retrieve metadata for group {first_group.jid}.")
                        if metadata_result.rate_limit: print(f"    Metadata Rate limit: {metadata_result.rate_limit.remaining}")
                    except WasenderAPIError as e_meta:
                        print(f"    API Error fetching group metadata: {e_meta.message}")
            else:
                print("No group data received.")

            if groups_result.rate_limit: print(f"Groups List Rate limit: {groups_result.rate_limit.remaining}")

        except WasenderAPIError as e:
            print(f"API Error fetching groups list: {e.message}")
        except Exception as e:
            print(f"An unexpected error: {e}")

# To run this example (ensure WASENDER_API_KEY is set):
# if __name__ == "__main__":
#     asyncio.run(manage_groups_example())
```

### 4. Sending Messages to WhatsApp Channels

Send text messages to WhatsApp Channels.

- **Detailed Documentation & Examples:** [`docs/channel.md`](./docs/channel.md)

```python
import asyncio
import os
from wasenderapi import create_async_wasender # Use factory for async client
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import ChannelTextMessage # This model is for generic send()

async def send_to_channel_example(channel_jid: str, text_message: str):
    local_api_key = os.getenv("WASENDER_API_KEY", "YOUR_CHANNEL_API_KEY")
    if local_api_key == "YOUR_CHANNEL_API_KEY":
        print("Error: WASENDER_API_KEY not set for channel example.")
        return

    # For sending to channels, the SDK might have a specific helper or use the generic send.
    # This example assumes use of generic send() with ChannelTextMessage model as shown previously.
    # If a client.send_channel_text() helper exists, prefer that.

    async with create_async_wasender(api_key=local_api_key) as async_client:
        print(f"\nAttempting to send to WhatsApp Channel {channel_jid}...")
        try:
            payload = ChannelTextMessage(
                to=channel_jid, 
                message_type="text", # Assuming model requires this
                text=text_message
            )
            # Using generic send method for channel messages as per original example
            result = await async_client.send(payload) 
            
            print(f"Message sent to channel successfully.")
            if result.response: print(f"  Message ID: {result.response.message_id}, Status: {result.response.message}")
            if result.rate_limit: print(f"Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit}")

        except WasenderAPIError as e:
            print(f"API Error sending to channel: {e.message}")
        except Exception as e:
            print(f"An unexpected error: {e}")

# To run this example (ensure WASENDER_API_KEY and TEST_CHANNEL_JID are set):
# async def main_run_channel_example():
#     test_channel_jid = os.getenv("TEST_CHANNEL_JID", "YOUR_CHANNEL_JID@newsletter")
#     message = "Hello Channel from SDK Example!"
#     if test_channel_jid == "YOUR_CHANNEL_JID@newsletter":
#         print("Please set a valid TEST_CHANNEL_JID environment variable.")
#         return
#     await send_to_channel_example(channel_jid=test_channel_jid, text_message=message)

# if __name__ == "__main__":
#     asyncio.run(main_run_channel_example())
```

### 5. Handling Incoming Webhooks

Process real-time events from Wasender. The `handle_webhook_event` method is available on both sync and async clients, but it is an `async` method in both cases.

- **Detailed Documentation & Examples:** [`docs/webhook.md`](./docs/webhook.md)

```python
import os
import json # For pretty printing
# Use the appropriate client factory
from wasenderapi import create_sync_wasender, create_async_wasender 
from wasenderapi.webhook import WasenderWebhookEvent, WasenderWebhookEventType
from wasenderapi.errors import SignatureVerificationError, WasenderAPIError 

# Client initialization for webhook handling:
# Webhook secret is the key component here.
webhook_secret_from_env = os.getenv("WASENDER_WEBHOOK_SECRET")
if not webhook_secret_from_env:
    print("CRITICAL: WASENDER_WEBHOOK_SECRET environment variable is not set.")
    # webhook_secret_from_env = "YOUR_PLACEHOLDER_WEBHOOK_SECRET" # For structure viewing

# You can use either sync or async client to access handle_webhook_event.
# However, since handle_webhook_event itself is async, using it in a purely
# synchronous web framework like standard Flask requires special handling (e.g., asyncio.run_coroutine_threadsafe).
# For an async framework (like FastAPI, Quart), you'd use the async client.

# Example: Initialize a sync client for its config, but note the method is async.
sync_client_for_webhook = create_sync_wasender(
    api_key="DUMMY_API_KEY_NOT_USED_FOR_WEBHOOK_LOGIC", # API key not strictly needed for webhook verification logic
    webhook_secret=webhook_secret_from_env
)

# --- Conceptual Example: How to use with a web framework (e.g., Flask) ---
# This illustrates the logic. Actual integration needs to handle the async nature
# of handle_webhook_event within the sync framework.
#
# from flask import Flask, request, jsonify
# import asyncio
#
# app = Flask(__name__)
#
# def run_async_in_sync(coro):
#     # A simple way to run an async function from sync code (for demonstration)
#     # In production, use framework-specific solutions or proper async event loop management.
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     return loop.run_until_complete(coro)
#
# @app.route("/wasender-webhook", methods=["POST"])
# def flask_webhook_handler():
#     raw_body_bytes = request.get_data()
#     headers_dict = dict(request.headers)
#
#     if not sync_client_for_webhook.webhook_secret:
#         print("Error: Webhook secret not configured.")
#         return jsonify({"error": "Webhook secret not configured"}), 500
#
#     try:
#         # handle_webhook_event is async, so needs to be run in an event loop
#         event: WasenderWebhookEvent = run_async_in_sync(
#             sync_client_for_webhook.handle_webhook_event(
#                 request_body_bytes=raw_body_bytes, # Pass raw_body_bytes here
#                 signature_header=headers_dict.get(WasenderWebhookEvent.SIGNATURE_HEADER) # Pass correct header
#             )
#         )
#         print(f"Webhook Type: {event.event_type.value}")
#         # ... (process event.data based on event.event_type) ...
#         return jsonify({"status": "success"}), 200
#     except SignatureVerificationError as e:
#         return jsonify({"error": "Signature verification failed"}), 400
#     except WasenderAPIError as e: # Handles other SDK errors like bad payload
#         return jsonify({"error": f"Webhook processing error: {e.message}"}), 400
#     except Exception as e:
#         return jsonify({"error": "Internal server error"}), 500

# Dummy data for local testing (if __name__ == "__main__")
# ... (The existing dummy data and call simulation can be kept but adapted ...)
# ... ensure to call sync_client_for_webhook.handle_webhook_event ...

# if __name__ == "__main__":
#     # ... (simulation code using sync_client_for_webhook.handle_webhook_event)
#     # Remember the async nature when simulating the call directly.
#     pass 
```

### 6. Managing WhatsApp Sessions

Create, list, update, delete sessions, connect/disconnect, get QR codes, and check session status. Listing all sessions or creating new ones typically requires a `personal_access_token`.

- **Detailed Documentation & Examples:** [`docs/sessions.md`](./docs/sessions.md)

```python
import asyncio
import os
from wasenderapi import create_async_wasender # Use factory for async client
from wasenderapi.errors import WasenderAPIError

async def manage_whatsapp_sessions_example():
    local_api_key = os.getenv("WASENDER_API_KEY", "YOUR_SESSIONS_API_KEY")
    # For listing all sessions or creating new ones, a personal access token is often needed.
    local_personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN") 

    if local_api_key == "YOUR_SESSIONS_API_KEY":
        print("Error: WASENDER_API_KEY not set for sessions example.")
        return
    
    # Client for session-specific actions (uses api_key of that session)
    # Client for account-level session actions (uses personal_access_token)
    # We'll use one client, assuming personal_access_token is for listing/creating if needed,
    # and api_key for specific session operations if that's how the SDK/API is structured.
    # The create_async_wasender can take both.

    async with create_async_wasender(api_key=local_api_key, personal_access_token=local_personal_access_token) as async_client:
        if not local_personal_access_token:
            print("Warning: WASENDER_PERSONAL_ACCESS_TOKEN not set. Listing all sessions might fail or be restricted.")

        print("\nAttempting to list WhatsApp sessions...")
        try:
            # get_all_whatsapp_sessions is the method for listing all sessions
            list_sessions_result = await async_client.get_all_whatsapp_sessions() 

            if list_sessions_result.response and list_sessions_result.response.data is not None:
                sessions = list_sessions_result.response.data
                print(f"Successfully fetched {len(sessions)} session(s).")
                if sessions:
                    for session_info in sessions:
                        print(f"  Session ID: {session_info.session_id}, Status: {session_info.status.value if session_info.status else 'N/A'}")
                else:
                    print("  No active sessions found for this account.")
            else:
                print("No session data received.")

            if list_sessions_result.rate_limit: print(f"List Sessions Rate limit: {list_sessions_result.rate_limit.remaining}")

            # Example for get_session_status (uses api_key of a specific session)
            # if sessions:
            #     target_session_id = sessions[0].session_id # This is numeric ID from the list
            #     # To get status, you typically use the API key associated with *that* session_id,
            #     # which might be different from the local_api_key if it's a PAT.
            #     # For this example, we assume async_client was initialized with the correct session's API key
            #     # if we were to uncomment and run the following. Or, one might re-initialize a client
            #     # specifically for that session if its API key is known.
            #     print(f"\nAttempting to get status for session: {target_session_id}")
            #     try:
            #         # Assuming local_api_key IS the key for this specific session if we call get_session_status
            #         # If not, this call might not be correctly authorized.
            #         status_result = await async_client.get_session_status(session_id=str(target_session_id)) # Ensure session_id is string if required
            #         if status_result.response and status_result.response.data:
            #             print(f"  Status for {target_session_id}: {status_result.response.data.status.value}")
            #     except WasenderAPIError as e_status:
            #         print(f"  Error getting status for {target_session_id}: {e_status.message}")

        except WasenderAPIError as e:
            print(f"API Error managing sessions: {e.message}")
        except Exception as e:
            print(f"An unexpected error: {e}")

# To run this example (ensure WASENDER_API_KEY and optionally WASENDER_PERSONAL_ACCESS_TOKEN are set):
# if __name__ == "__main__":
#     asyncio.run(manage_whatsapp_sessions_example())
```

## Advanced Topics

### Configuring Retries

The SDK supports automatic retries, primarily for handling HTTP 429 (Too Many Requests) errors. This is configured via the `RetryConfig` object passed to `retry_options` during client initialization.

```python
from wasenderapi import create_sync_wasender, create_async_wasender
from wasenderapi.models import RetryConfig

# Configure retries: enable and set max retries
retry_settings = RetryConfig(enabled=True, max_retries=3)

# For synchronous client
sync_client_with_retries = create_sync_wasender(
    api_key="YOUR_API_KEY", 
    retry_options=retry_settings
)

# For asynchronous client
async_client_with_retries = create_async_wasender(
    api_key="YOUR_API_KEY", 
    retry_options=retry_settings
)

# Example usage (sync)
# try:
#     sync_client_with_retries.send_text(to="PHONE", text_body="Test with retries")
# except WasenderAPIError as e:
#     print(f"Failed after retries: {e}")
```

By default, retries are disabled.

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## License

This SDK is released under the [MIT License](./LICENSE).
