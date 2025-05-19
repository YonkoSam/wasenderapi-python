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

- **Pydantic Models:** Leverages Pydantic for robust request/response validation and serialization.
- **Message Sending:**
  - Generic `client.send()` method for all supported message types.
  - Specific helper methods (e.g., `client.send_text()`, `client.send_image()`) for convenience.
  - Support for text, image, video, document, audio, sticker, contact card, and location messages.
- **Contact Management:** List, retrieve details, get profile pictures, block, and unblock contacts.
- **Group Management:** List groups, fetch metadata, manage participants (add/remove), and update group settings.
- **Channel Messaging:** Send text messages to WhatsApp Channels.
- **Session Management:** Create, list, update, delete sessions, connect/disconnect, get QR codes, and check session status.
- **Webhook Handling:** Securely verify and parse incoming webhook events from Wasender using Pydantic models.
- **Error Handling:** Comprehensive `WasenderAPIError` class with detailed error information.
- **Rate Limiting:** Access to rate limit information on API responses.
- **Retry Mechanism:** Optional automatic retries for rate-limited requests (HTTP 429) via `RetryConfig`.
- **Customizable HTTP Client:** Allows providing a custom `fetch_implementation` (compatible with `requests.request` or an async equivalent) for specialized HTTP handling or testing.

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

```python
import os
from wasenderapi import WasenderClient
from wasenderapi.models import RetryConfig # Assuming RetryConfig is in models
# from wasenderapi.client import FetchImplementation # If you expose custom fetch

# Required credentials
api_key = os.getenv("WASENDER_API_KEY")
persona_token = os.getenv("WASENDER_PERSONA_ACCESS_TOKEN") # Required for account-scoped endpoints
webhook_secret = os.getenv("WASENDER_WEBHOOK_SECRET")     # Required for webhook handling

if not api_key:
    raise ValueError("WASENDER_API_KEY environment variable not set.")

# Optional: Configure retry behavior for rate limit errors (HTTP 429)
retry_config = RetryConfig(
    enabled=True,
    max_retries=3, # Attempt up to 3 retries
    # backoff_factor=0.5 # Optional: factor to calculate delay
)

# Initialize with all options
# Note: If using a custom fetch_implementation, it should be compatible with 'requests.request'
# or an async equivalent if your client is async.
# For this example, we'll use the default internal HTTP client.
# custom_fetch_impl: Optional[FetchImplementation] = None 

wasender_client_full = WasenderClient(
    api_key=api_key,
    # base_url="https://www.wasenderapi.com/api", # Defaults to this
    # fetch_implementation=custom_fetch_impl,
    retry_config=retry_config,
    webhook_secret=webhook_secret,
    personal_token=persona_token
)

# Basic initialization (session-scoped endpoints only, no retries, no webhooks)
basic_wasender_client = WasenderClient(api_key=api_key)

# Initialize with persona token (for account management, no retries, no webhooks)
account_wasender_client = WasenderClient(
    api_key=api_key,
    personal_token=persona_token
)

# Initialize with webhook secret (for webhook handling, no retries, no account management)
webhook_handler_client = WasenderClient(
    api_key=api_key,
    webhook_secret=webhook_secret
)

print("WasenderClient initialized.")
```

**Important:** 
- Store your credentials securely (e.g., as environment variables)
- `WASENDER_API_KEY` is required for all API calls.
- `WASENDER_PERSONA_ACCESS_TOKEN` is required for account-scoped endpoints (e.g., managing general account settings, if applicable through the API).
- `WASENDER_WEBHOOK_SECRET` is required if you plan to use webhook signature verification.

## Authentication

The SDK supports two types of authentication:

1. **API Key Authentication** (Required for all API calls)
   - Used for most endpoints, typically those interacting with a specific WhatsApp session.
   - Set via the `WASENDER_API_KEY` environment variable, which is read by the `WasenderClient` by default if the `api_key` parameter is not directly provided during instantiation.
   - Alternatively, pass the `api_key` string directly to the `WasenderClient` constructor.

2. **Persona Access Token** (Required for account-scoped endpoints)
   - Used for account management endpoints (if applicable via the API, e.g., managing general account settings rather than session-specific ones).
   - Set via the `WASENDER_PERSONA_ACCESS_TOKEN` environment variable, which can be read by `WasenderClient` if the `persona_token` parameter is not directly provided.
   - Alternatively, pass the `persona_token` string directly to the `WasenderClient` constructor.

The `WasenderClient` will prioritize tokens passed directly to its constructor over environment variables.

## Core Concepts

### Message Payloads

The Python SDK uses Pydantic models for defining message payloads. The core payload type is `WasenderMessagePayload` (a `Union` of all specific message types like `TextOnlyMessage`, `ImageMessage`, etc.). Each specific message model requires a `message_type` field (e.g., `"text"`, `"image"`) which acts as a discriminator, along with other relevant fields for that message type.

### Generic `send()` vs. Specific Helpers

- **`client.send(payload: WasenderMessagePayload)`:** A versatile method that accepts any valid Pydantic message payload model.
- **`client.send_text(...)`**, **`client.send_image(...)`**, etc.: Convenience helper methods that construct the appropriate Pydantic model and pre-fill the `message_type` for you. They typically accept parameters like `to`, `text`, `image_url`, etc., directly.

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

Send various types of messages including text, media (images, videos, documents, audio, stickers), contact cards, and location pins.

- **Detailed Documentation & Examples:** [`docs/messages.md`](./docs/messages.md)

```python
import asyncio
import os
from wasenderapi import WasenderClient
from wasenderapi.errors import WasenderAPIError
# from wasenderapi.models import TextOnlyMessage # Use if constructing payload for client.send()

# It's good practice to initialize the client once and reuse it.
# Ensure WASENDER_API_KEY is set in your environment variables.
api_key = os.getenv("WASENDER_API_KEY")
if not api_key:
    print("Error: WASENDER_API_KEY environment variable not set.")
    # exit(1) # Or handle appropriately
    # For example purposes, we'll assign a placeholder if not found, 
    # but in a real app, you should ensure it's set.
    api_key = "YOUR_API_KEY_HERE" 

client = WasenderClient(api_key=api_key)

async def send_simple_text_example():
    try:
        # Example using the send_text helper method for convenience
        result = await client.send_text(
            to_jid="+1234567890",  # Recipient's JID (e.g., phone_number@s.whatsapp.net)
            text="Hello from the Wasender Python SDK!"
        )
        print(f"Message sent successfully. Message ID: {result.response.message_id}")
        print(f"Status: {result.response.message}")
        
        if result.rate_limit:
            print(f"Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit}, resets at {result.rate_limit.reset_timestamp}")
        else:
            print("Rate limit information not available for this response.")

        # Example using the generic client.send() method with a Pydantic model
        # from wasenderapi.models import TextOnlyMessage
        # text_payload = TextOnlyMessage(
        #     message_type="text",
        #     to="+1234567890",
        #     text="Hello again via generic send!"
        # )
        # generic_result = await client.send(text_payload)
        # print(f"Generic message sent: {generic_result.response.message}")

    except WasenderAPIError as e:
        print(f"API Error sending message: Status {e.status_code}, Message: {e.api_message or 'N/A'}")
        if e.error_details:
            print(f"Details: Code {e.error_details.code}, Message: {e.error_details.message}")
        if e.rate_limit:
            print(f"Rate limit at error: {e.rate_limit.remaining}/{e.rate_limit.limit}, resets at {e.rate_limit.reset_timestamp}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def main():
    if api_key == "YOUR_API_KEY_HERE":
        print("Please set your WASENDER_API_KEY environment variable to run this example.")
        return
    await send_simple_text_example()

if __name__ == "__main__":
    # In a real application, you would typically run the asyncio event loop like this:
    # asyncio.run(main())
    # For a README example, we'll just show the function call pattern.
    # To run this specific example: python your_file_name.py
    # Ensure you have `asyncio` and `python-dotenv` (if using .env for API key) installed.
    print("Running send_simple_text_example... (This will make an API call if API key is valid)")
    # Note: Top-level await is available in Python 3.8+ in REPL and scripts.
    # For broader compatibility in scripts, use asyncio.run().
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "cannot be called from a running event loop" in str(e):
            # If already in an event loop (e.g. Jupyter notebook)
            # just await it directly. This is a common pattern for library examples.
            # await main() 
            # For a simple script, the above asyncio.run() is standard.
            print("If running in an environment like Jupyter, you might need to 'await main()' directly.")
        else:
            raise

```

### 2. Managing Contacts

Retrieve your contact list, fetch information about specific contacts, get their profile pictures, and block or unblock contacts.

- **Detailed Documentation & Examples:** [`docs/contacts.md`](./docs/contacts.md)

```python
import asyncio
import os
from wasenderapi import WasenderClient # Assuming client is initialized as in previous examples
from wasenderapi.errors import WasenderAPIError

# Ensure client is initialized (e.g., from a shared section or a previous example)
# For this snippet, we'll re-state a basic initialization for clarity.
api_key = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE") # Default to placeholder
client = WasenderClient(api_key=api_key)

async def get_my_contacts_example():
    if client.api_key == "YOUR_API_KEY_HERE":
        print("Error: WASENDER_API_KEY not set. Please set it to run the contacts example.")
        return

    print("\nAttempting to fetch contacts...")
    try:
        result = await client.get_contacts()
        
        if result.response and result.response.data is not None:
            contacts = result.response.data
            print(f"Successfully fetched {len(contacts)} contacts.")
            if contacts:
                first_contact = contacts[0]
                print(f"  First contact - JID: {first_contact.jid}, Name: {first_contact.name or 'N/A'}")
                # You can access other contact attributes like first_contact.notify, first_contact.short_name etc.
                # print(f"    Full details: {first_contact.model_dump_json(indent=2)}")
        else:
            print("No contact data received in the response.") # Should ideally not happen if API call is successful

        if result.rate_limit:
            print(f"Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit}, Resets at: {result.rate_limit.reset_timestamp}")
        else:
            print("Rate limit information not available for this response.")

    except WasenderAPIError as e:
        print(f"API Error fetching contacts: Status {e.status_code}, Message: {e.api_message or 'N/A'}")
        if e.error_details:
            print(f"  Details: Code {e.error_details.code}, Message: {e.error_details.message}")
        if e.rate_limit:
            print(f"  Rate limit at error: {e.rate_limit.remaining}/{e.rate_limit.limit}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def run_contacts_main():
    await get_my_contacts_example()

if __name__ == "__main__":
    # This block allows running this example script directly.
    # Remember to set your WASENDER_API_KEY environment variable.
    print("Executing contacts example (ensure WASENDER_API_KEY is set)...")
    asyncio.run(run_contacts_main())
    # Example output (if successful):
    # Attempting to fetch contacts...
    # Successfully fetched 5 contacts.
    #   First contact - JID: 1234567890@s.whatsapp.net, Name: John Doe
    # Rate limit: 99/100, Resets at: 1678886400

### 3. Managing Groups

List groups your account is part of, get group metadata (like subject and participants), add or remove participants, and update group settings (subject, description, announce/restrict modes).

- **Detailed Documentation & Examples:** [`docs/groups.md`](./docs/groups.md)

```python
import asyncio
import os
from wasenderapi import WasenderClient # Assuming client is initialized
from wasenderapi.errors import WasenderAPIError

# Client initialization (assuming from a shared part or previous example)
api_key = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE")
client = WasenderClient(api_key=api_key)

async def manage_groups_example():
    if client.api_key == "YOUR_API_KEY_HERE":
        print("Error: WASENDER_API_KEY not set. Please set it to run the groups example.")
        return

    print("\nAttempting to fetch groups...")
    try:
        groups_result = await client.get_groups()
        
        if groups_result.response and groups_result.response.data is not None:
            groups = groups_result.response.data
            print(f"Successfully fetched {len(groups)} groups.")
            
            if groups:
                first_group = groups[0]
                print(f"  First group - JID: {first_group.jid}, Subject: {first_group.subject}")
                # print(f"    Creation: {first_group.creation}, Owner: {first_group.owner_jid}")

                # Example: Get metadata for the first group
                print(f"  Fetching metadata for group: {first_group.jid}...")
                try:
                    metadata_result = await client.get_group_metadata(group_jid=first_group.jid)
                    if metadata_result.response and metadata_result.response.data:
                        metadata = metadata_result.response.data
                        participant_count = len(metadata.participants) if metadata.participants else 0
                        print(f"    Group Subject: {metadata.subject}")
                        print(f"    Participant count: {participant_count}")
                        # if metadata.participants:
                        #     print(f"    First participant: {metadata.participants[0].model_dump_json()}")
                        # print(f"    Full metadata: {metadata.model_dump_json(indent=2)}")
                    else:
                        print(f"    Could not retrieve metadata for group {first_group.jid}.")
                    
                    if metadata_result.rate_limit:
                         print(f"    Metadata Rate limit: {metadata_result.rate_limit.remaining}/{metadata_result.rate_limit.limit}")

                except WasenderAPIError as e_meta:
                    print(f"    API Error fetching group metadata: Status {e_meta.status_code}, Msg: {e_meta.api_message}")
                except Exception as e_inner:
                    print(f"    Unexpected error fetching group metadata: {e_inner}")
        else:
            print("No group data received in the response.")

        if groups_result.rate_limit:
            print(f"Groups List Rate limit: {groups_result.rate_limit.remaining}/{groups_result.rate_limit.limit}")
        else:
            print("Rate limit information not available for get_groups response.")

    except WasenderAPIError as e:
        print(f"API Error fetching groups list: Status {e.status_code}, Message: {e.api_message or 'N/A'}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def run_groups_main():
    await manage_groups_example()

if __name__ == "__main__":
    print("Executing groups example (ensure WASENDER_API_KEY is set)...")
    asyncio.run(run_groups_main())
    # Example output (if successful and group exists):
    # Attempting to fetch groups...
    # Successfully fetched 1 groups.
    #   First group - JID: 1234567890-12345678@g.us, Subject: My Test Group
    #   Fetching metadata for group: 1234567890-12345678@g.us...
    #     Group Subject: My Test Group
    #     Participant count: 2
    #     Metadata Rate limit: 99/100
    # Groups List Rate limit: 98/100

### 4. Sending Messages to WhatsApp Channels

Send text messages to WhatsApp Channels (within Communities).

- **Detailed Documentation & Examples:** [`docs/channel.md`](./docs/channel.md)

```python
import asyncio
import os
from wasenderapi import WasenderClient
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import ChannelTextMessage # Ensure this model is defined in your SDK

# Client initialization
api_key = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE")
client = WasenderClient(api_key=api_key)

async def send_to_channel_example(channel_jid: str, text_message: str):
    if client.api_key == "YOUR_API_KEY_HERE":
        print("Error: WASENDER_API_KEY not set. Please set it to run the channel messaging example.")
        return

    print(f"\nAttempting to send message to WhatsApp Channel {channel_jid}...")
    try:
        # Construct the payload using the Pydantic model for channel text messages
        # The `message_type` is typically part of the model's definition or fields.
        # For ChannelTextMessage, it might be implicitly "text" or need to be specified.
        # Let's assume it needs to be specified, matching common patterns.
        payload = ChannelTextMessage(
            to=channel_jid,  # The JID of the channel, e.g., "12345678901234567890@newsletter"
            message_type="text", # Explicitly set, assuming it's required by ChannelTextMessage
            text=text_message
        )
        
        # Use the generic client.send() method
        result = await client.send(payload)
        
        print(f"Message sent to channel successfully.")
        if result.response:
            print(f"  Message ID: {result.response.message_id}")
            print(f"  Status: {result.response.message}")
        
        if result.rate_limit:
            print(f"Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit}, Resets at: {result.rate_limit.reset_timestamp}")
        else:
            print("Rate limit information not available for this response.")

    except WasenderAPIError as e:
        print(f"API Error sending to channel: Status {e.status_code}, Message: {e.api_message or 'N/A'}")
        if e.error_details:
            print(f"  Details: Code {e.error_details.code}, Message: {e.error_details.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

async def run_channel_message_main():
    # IMPORTANT: Replace with a valid channel JID you have access to post to,
    # and ensure your API key/session is authorized for channel messaging.
    test_channel_jid = os.getenv("TEST_CHANNEL_JID", "YOUR_CHANNEL_JID@newsletter") 
    message_to_send = "Hello Channel Subscribers from the Wasender Python SDK!"
    
    if client.api_key == "YOUR_API_KEY_HERE" or test_channel_jid == "YOUR_CHANNEL_JID@newsletter":
        print("Please set your WASENDER_API_KEY and a valid TEST_CHANNEL_JID environment variable (or update the script) to run this example.")
        return
        
    await send_to_channel_example(channel_jid=test_channel_jid, text_message=message_to_send)

if __name__ == "__main__":
    print("Executing send to WhatsApp Channel example...")
    print("Ensure WASENDER_API_KEY is set and you have a valid channel JID in TEST_CHANNEL_JID or in the script.")
    asyncio.run(run_channel_message_main())
    # Example output (if successful):
    # Attempting to send message to WhatsApp Channel 12345678901234567890@newsletter...
    # Message sent to channel successfully.
    #   Message ID: some_unique_message_id@s.whatsapp.net
    #   Status: Message accepted for delivery to channel
    # Rate limit: 99/100, Resets at: 1678886400

### 5. Handling Incoming Webhooks

Process real-time events from Wasender such as new messages, message status updates, and session status changes.

- **Detailed Documentation & Examples:** [`docs/webhook.md`](./docs/webhook.md)

```python
import os
import json # For pretty printing in the example output
from wasenderapi import WasenderClient
from wasenderapi.webhook import WasenderWebhookEvent, WasenderWebhookEventType, SignatureVerificationError
# Import specific data models for type hinting if needed, e.g.:
# from wasenderapi.webhook import MessagesUpsertData, SessionStatusData, QrcodeUpdatedData

# Client initialization:
# The webhook_secret can be set on the client or passed directly to handle_webhook_event.
# For this example, we'll assume it's set via an environment variable and configured on the client.
api_key = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE_FOR_CLIENT") # API key might not be used by webhook handler itself
webhook_secret_from_env = os.getenv("WASENDER_WEBHOOK_SECRET")

if not webhook_secret_from_env:
    print("CRITICAL: WASENDER_WEBHOOK_SECRET environment variable is not set.")
    print("Webhook signature verification will fail. Please set it for a real application.")
    # For example purposes, you might use a placeholder if you're just inspecting structure
    # webhook_secret_from_env = "YOUR_ACTUAL_WEBHOOK_SECRET" 

client = WasenderClient(api_key=api_key, webhook_secret=webhook_secret_from_env)

# --- Conceptual Example: How to use with a web framework like Flask ---
# You would integrate this logic into your web server's request handler.
#
# from flask import Flask, request, jsonify # Example imports
#
# app = Flask(__name__)
#
# @app.route("/wasender-webhook", methods=["POST"])
# def flask_webhook_handler():
#     # 1. Get the raw request body as bytes
#     # IMPORTANT: Ensure you get the raw body BEFORE any JSON parsing by your framework.
#     raw_body_bytes = request.get_data() 
#
#     # 2. Get request headers as a dictionary
#     headers_dict = dict(request.headers)
#
#     # 3. Get the webhook secret. 
#     #    The client.handle_webhook_event will use the secret configured on the client 
#     #    if not explicitly passed to the method.
#     #    Ensure client.webhook_secret is set, or pass webhook_secret_from_env directly.
#     if not client.webhook_secret:
#          print("Error: Webhook secret not configured on the client or passed to handler.")
#          return jsonify({"error": "Webhook secret not configured"}), 500
#
#     try:
#         # 4. Process the event
#         event: WasenderWebhookEvent = client.handle_webhook_event(
#             headers=headers_dict,
#             raw_body=raw_body_bytes
#             # Or pass secret explicitly: webhook_secret=webhook_secret_from_env 
#         )
#
#         print(f"Successfully verified and parsed webhook. Event Type: {event.event_type.value}")
#
#         # 5. Handle the event based on its type
#         if event.event_type == WasenderWebhookEventType.MESSAGES_UPSERT:
#             # event.data is now safely typed as MessagesUpsertData (or the correct Pydantic model)
#             messages_data = event.data # type: ignore
#             print(f"  Event: Messages Upsert. Received {len(messages_data.messages)} message(s).")
#             for msg_info in messages_data.messages:
#                 print(f"    - From: {msg_info.key.remote_jid}, ID: {msg_info.key.id}")
#                 if msg_info.message and msg_info.message.conversation:
#                     print(f"      Text: '{msg_info.message.conversation}'")
#                 # Access other message details via msg_info.message...
#         
#         elif event.event_type == WasenderWebhookEventType.SESSION_STATUS:
#             session_data = event.data # type: ignore
#             print(f"  Event: Session Status. Session ID: {session_data.session_id}, Status: {session_data.status.value}")
#             if session_data.qr_code:
#                 print(f"    QR Code available (first 50 chars): {session_data.qr_code[:50]}...")
#         
#         elif event.event_type == WasenderWebhookEventType.QRCODE_UPDATED: 
#             qr_data = event.data # type: ignore
#             print(f"  Event: QR Code Updated. Session ID: {qr_data.session_id}")
#             print(f"    QR Code (first 50 chars): {qr_data.qr_code[:50]}...")
#
#         # Add more handlers for other event types like:
#         # WasenderWebhookEventType.CONTACTS_SET, WasenderWebhookEventType.GROUPS_UPDATE, etc.
#
#         else:
#             print(f"  Unhandled event type: {event.event_type.value}")
#             # print(f"    Raw data: {event.data.model_dump_json(indent=2)}")
#
#         return jsonify({"status": "success", "received_event_type": event.event_type.value}), 200
#
#     except SignatureVerificationError as e:
#         print(f"Webhook Signature Verification Failed: {e}")
#         return jsonify({"error": "Signature verification failed", "details": str(e)}), 400 # HTTP 400 or 401
#     except ValueError as e: # Catches Pydantic validation errors or JSON parsing issues from SDK
#         print(f"Webhook Data Processing Error (e.g., Pydantic validation): {e}")
#         return jsonify({"error": "Invalid payload format or data", "details": str(e)}), 400
#     except Exception as e:
#         print(f"An unexpected error occurred in webhook handler: {type(e).__name__} - {e}")
#         return jsonify({"error": "Internal server error", "details": str(e)}), 500
#
# # To run the Flask example (conceptual):
# # 1. Install Flask: `pip install Flask`
# # 2. Set WASENDER_WEBHOOK_SECRET (and WASENDER_API_KEY) environment variables.
# # 3. Uncomment the Flask app code blocks above.
# # 4. Run this Python script.
# # 5. Use ngrok or similar to expose your local Flask server (e.g., http://localhost:5000) to a public URL.
# # 6. Configure this public URL in your Wasender dashboard's webhook settings.

if __name__ == "__main__":
    print("Python SDK Webhook Handling Example (Conceptual - Flask based)")
    print("------------------------------------------------------------")
    print("This script defines a conceptual Flask webhook handler and simulates a call.")
    print("See comments in the code for how to set up and run a live Flask server.")

    if not client.webhook_secret:
        print("\nWARNING: client.webhook_secret is not set from WASENDER_WEBHOOK_SECRET.")
        print("The simulated call below will likely bypass actual signature verification or fail if a dummy signature is used.")
    
    # Dummy data for illustration (replace with actual data from a Wasender webhook POST for real testing)
    dummy_headers = {
        # X-Wasender-Signature is crucial. For a real test, generate one using your secret and the dummy_raw_body_bytes.
        # Example: hmac.new(webhook_secret.encode('utf-8'), dummy_raw_body_bytes, hashlib.sha1).hexdigest()
        "X-Wasender-Signature": "sha1=0123456789abcdef0123456789abcdef01234567", # Placeholder signature
        "Content-Type": "application/json"
    }
    dummy_payload_dict = {
        "eventType": "sessionStatus", # Corresponds to WasenderWebhookEventType.SESSION_STATUS.value
        "instanceId": "example-instance",
        "sessionId": "session_example_123",
        "data": {
            "sessionId": "session_example_123",
            "status": "CONNECTED", # Corresponds to WhatsAppSessionStatus.CONNECTED.value
            "qrCode": None,
            "message": "Session is now connected."
        }
    }
    dummy_raw_body_bytes = json.dumps(dummy_payload_dict).encode('utf-8')

    print("\nSimulating a call to client.handle_webhook_event with dummy data...")
    print(f"  Client's webhook_secret is set: {bool(client.webhook_secret)}")
    try:
        # Note: With a placeholder X-Wasender-Signature, this will fail if a real webhook_secret is set.
        # If client.webhook_secret is None, signature verification might be skipped by the SDK (undesirable for production).
        print(f"  Attempting to process with dummy headers and body:")
        print(f"  Headers: {dummy_headers}")
        print(f"  Body (first 100 bytes): {dummy_raw_body_bytes[:100]}...")
        
        # We call it here to demonstrate SDK usage, but expect errors with dummy signature/secret.
        event = client.handle_webhook_event(
            headers=dummy_headers, 
            raw_body=dummy_raw_body_bytes
            # webhook_secret="override_secret_if_needed" # Optional: override client's secret
        )
        print(f"  SUCCESS (UNEXPECTED WITH DUMMY SIGNATURE unless secret is also placeholder/specific): Parsed dummy event: {event.event_type}")
        print(f"  Event data: {event.data.model_dump_json(indent=2)}")

    except SignatureVerificationError as e:
        print(f"  EXPECTED: Signature Verification Failed with dummy data as expected or secret mismatch: {e}")
    except ValueError as e: # Pydantic validation or JSON errors
        print(f"  Data processing error with dummy data: {e}")
    except Exception as e:
        print(f"  Unexpected error with dummy data: {type(e).__name__} - {e}")

    print("\nReminder: For live webhook handling, integrate the commented-out Flask (or other framework) code.")

### 6. Managing WhatsApp Sessions

Create, list, update, delete sessions, connect/disconnect, get QR codes, and check session status.

- **Detailed Documentation & Examples:** [`docs/sessions.md`](./docs/sessions.md)

```python
import asyncio
import os
from wasenderapi import WasenderClient
from wasenderapi.errors import WasenderAPIError
# from wasenderapi.models import WhatsAppSession # For type hinting if desired

# Client initialization
# Session management, especially listing all sessions, might require a persona_token.
api_key = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE")
persona_token = os.getenv("WASENDER_PERSONA_ACCESS_TOKEN") # Often needed for session overview

# Initialize client with API key and potentially persona_token for session management
client = WasenderClient(api_key=api_key, persona_token=persona_token)

async def manage_whatsapp_sessions_example():
    if client.api_key == "YOUR_API_KEY_HERE":
        print("Error: WASENDER_API_KEY not set. Please set it to run the sessions example.")
        return
    
    # Depending on the API, listing all sessions might require a persona_token.
    # Specific session actions (get_status, get_qr) usually use the api_key of that session.
    if not client.persona_token:
        print("Warning: WASENDER_PERSONA_ACCESS_TOKEN not set. Listing all sessions might fail or be restricted.")

    print("\nAttempting to list WhatsApp sessions...")
    try:
        # Example: List all sessions associated with the account (persona_token likely required)
        list_sessions_result = await client.get_sessions() 

        if list_sessions_result.response and list_sessions_result.response.data is not None:
            sessions = list_sessions_result.response.data
            print(f"Successfully fetched {len(sessions)} session(s)." )
            if sessions:
                for session_info in sessions:
                    print(f"  Session ID: {session_info.session_id}")
                    print(f"    Status: {session_info.status.value if session_info.status else 'N/A'}")
                    print(f"    Is Legacy: {session_info.is_legacy}")
                    print(f"    Created At: {session_info.created_at}")
                    # print(f"    Webhook URL: {session_info.webhook_url or 'Not set'}")
                    # For more details, you might need a specific get_session(id) call if available
                    # or inspect session_info.model_dump_json(indent=2)
            else:
                print("  No active sessions found for this account.")
        else:
            print("No session data (or empty list) received in the list_sessions response.")

        if list_sessions_result.rate_limit:
            print(f"List Sessions Rate limit: {list_sessions_result.rate_limit.remaining}/{list_sessions_result.rate_limit.limit}, Resets: {list_sessions_result.rate_limit.reset_timestamp}")
        else:
            print("Rate limit information not available for list_sessions response.")

        # Further examples (uncomment and adapt as needed):
        # if sessions:
        #     target_session_id = sessions[0].session_id
        #     print(f"\nAttempting to get status for session: {target_session_id}")
        #     try:
        #         status_result = await client.get_session_status(session_id=target_session_id)
        #         if status_result.response and status_result.response.data:
        #             print(f"  Status for {target_session_id}: {status_result.response.data.status.value}")
        #             if status_result.response.data.qr_code:
        #                 print(f"    QR Code available (first 30 chars): {status_result.response.data.qr_code[:30]}...")
        #     except WasenderAPIError as e_status:
        #         print(f"  Error getting status for {target_session_id}: {e_status.api_message}")

    except WasenderAPIError as e:
        print(f"API Error managing sessions: Status {e.status_code}, Message: {e.api_message or 'N/A'}")
        if e.error_details:
            print(f"  Details: Code {e.error_details.code}, Message: {e.error_details.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")

async def run_sessions_main():
    await manage_whatsapp_sessions_example()

if __name__ == "__main__":
    print("Executing WhatsApp sessions example...")
    print("Ensure WASENDER_API_KEY is set.")
    print("Ensure WASENDER_PERSONA_ACCESS_TOKEN is set if your account needs it for listing all sessions.")
    asyncio.run(run_sessions_main())
    # Example output (if successful):
    # Attempting to list WhatsApp sessions...
    # Successfully fetched 1 session(s).
    #   Session ID: my_session_123
    #     Status: CONNECTED
    #     Is Legacy: False
    #     Created At: 2023-10-26T10:00:00Z
    # List Sessions Rate limit: 49/50, Resets: 1678886400000

## Advanced Topics

### Custom Fetch Implementation

If you need to use a custom HTTP client (e.g., for specialized logging, mocking, specific proxy configurations, or if `httpx` is not suitable for your environment), you can provide your own asynchronous `fetch_implementation` during `WasenderClient` initialization. The Python SDK is asynchronous and designed to work with an async fetch mechanism.

```python
import asyncio
import os
from typing import Any, Callable, Coroutine, Mapping, Optional, Union
import httpx # Recommended library for async HTTP requests if not using default

from wasenderapi import WasenderClient, DEFAULT_BASE_URL
from wasenderapi.models import RetryConfig # For full client init signature

# Define the expected signature for an async fetch implementation.
# This matches what an async HTTP client like httpx.AsyncClient().request would provide.
AsyncFetchCallable = Callable[
    [str, str, Optional[Mapping[str, str]], Optional[Any], Optional[int]],
    Coroutine[Any, Any, httpx.Response] # Using httpx.Response as an example return type
]

# Example of a custom async fetch implementation using httpx
async def my_custom_async_fetch(
    method: str,
    url: str,
    headers: Optional[Mapping[str, str]] = None,
    json_data: Optional[Any] = None, # The SDK's _request method passes JSON-serializable data here
    timeout: Optional[int] = None  # Timeout in seconds
) -> httpx.Response: # Ensure your callable returns a response object the SDK can use
    print(f"Custom Async Fetch: Making {method.upper()} request to {url}")
    if headers:
        print(f"Custom Async Fetch: Headers: {headers}")
    if json_data:
        # In a real scenario, be careful about printing sensitive payload data
        print(f"Custom Async Fetch: JSON Payload (type): {type(json_data)}")

    async with httpx.AsyncClient() as http_client:
        response = await http_client.request(
            method=method.upper(), # httpx expects uppercase method
            url=url,
            headers=headers,
            json=json_data, # httpx uses 'json' parameter for dicts/serializable objects
            timeout=timeout if timeout is not None else httpx.USE_CLIENT_DEFAULT
        )
    print(f"Custom Async Fetch: Received status {response.status_code}")
    # The WasenderClient._request method will call response.raise_for_status()
    # if the status code indicates an error, so it's not strictly necessary here.
    return response

# Client initialization with custom async fetch
# Use a distinct api_key variable for this example to avoid conflicts if run in a larger script
api_key_for_custom_fetch = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE_FETCH_EXAMPLE")

# Only initialize and demonstrate if a real API key is provided for this specific example
if api_key_for_custom_fetch != "YOUR_API_KEY_HERE_FETCH_EXAMPLE":
    # For a complete WasenderClient signature, other params can be included:
    persona_token_example = os.getenv("WASENDER_PERSONA_ACCESS_TOKEN")
    webhook_secret_example = os.getenv("WASENDER_WEBHOOK_SECRET")
    # If your custom fetch handles retries, you might disable SDK's internal retries
    retry_config_example = RetryConfig(enabled=False) 

    custom_fetch_client = WasenderClient(
        api_key=api_key_for_custom_fetch,
        # base_url=DEFAULT_BASE_URL, # Optional, defaults to this
        fetch_implementation=my_custom_async_fetch, # Pass your custom callable
        retry_config=retry_config_example,
        webhook_secret=webhook_secret_example,
        persona_token=persona_token_example
    )
    print("\nWasenderClient initialized with custom async fetch implementation.")

    # Example of using a client method (which will then use your custom fetch)
    async def test_custom_fetch_usage():
        print("Attempting to use client with custom fetch (e.g., calling get_sessions)...")
        try:
            # Ensure persona_token is valid if get_sessions requires it for your account
            if not custom_fetch_client.persona_token:
                 print("WARN: Persona token not set for custom_fetch_client. The get_sessions call might fail or return limited/no data if persona token is required by the API for this action.")
            
            # Using get_sessions as an example API call that would trigger the fetch_implementation
            sessions_result = await custom_fetch_client.get_sessions() # This call will use my_custom_async_fetch
            
            if sessions_result.response and sessions_result.response.data is not None:
                 print(f"  Custom fetch call to get_sessions was successful. Found {len(sessions_result.response.data)} session(s).")
            else:
                print("  Custom fetch call to get_sessions returned a response, but it contained no session data or had an unexpected structure.")
        except Exception as e:
            print(f"  Error encountered while using custom fetch client with get_sessions: {type(e).__name__} - {e}")

    if __name__ == "__main__":
        # This block demonstrates how to run the test_custom_fetch_usage function.
        # To execute this:
        # 1. Ensure httpx is installed: `pip install httpx`
        # 2. Set the WASENDER_API_KEY environment variable (and WASENDER_PERSONA_ACCESS_TOKEN if get_sessions needs it).
        print("\nRunning custom fetch usage example (test_custom_fetch_usage)...")
        asyncio.run(test_custom_fetch_usage())
else:
    print("\nSkipping WasenderClient initialization with custom fetch: ")
    print("API key (WASENDER_API_KEY) is a placeholder ('YOUR_API_KEY_HERE_FETCH_EXAMPLE') or not set.")
    print("To run this example, please set a valid WASENDER_API_KEY environment variable.")

# Developer Note on `fetch_implementation` contract:
# The `fetch_implementation` callable provided to `WasenderClient` must be an `async` function.
# It should accept the following positional and keyword arguments:
#   - `method: str` (e.g., "GET", "POST")
#   - `url: str`
#   - `headers: Optional[Mapping[str, str]]`
#   - `json_data: Optional[Any]` (JSON-serializable data from the SDK)
#   - `timeout: Optional[int]` (timeout in seconds)
#
# It must return an awaitable that resolves to a response-like object. This object needs to provide:
#   - `.status_code: int` (e.g., 200, 404)
#   - `.headers: Mapping[str, str]` (e.g., a dictionary or `requests.structures.CaseInsensitiveDict`)
#   - `.json() -> Coroutine[Any, Any, Any]` (an async method returning the parsed JSON response, e.g., a dict or list)
#   - `.text: str` (a property or an awaitable returning the raw text response)
#   - `.content: bytes` (a property or an awaitable returning the raw byte content)
#   - `.raise_for_status() -> None` (a method that raises an appropriate error for HTTP 4xx/5xx responses)
#
# `httpx.Response` (from the `httpx` library) is a good example of an object that fulfills this contract.
# The SDK's internal `_request` method relies on these attributes and methods being available on the
# object returned by your `fetch_implementation`.

### Retry Configuration

The SDK can automatically retry requests that fail due to rate limiting (HTTP 429) or other specified server-side transient errors. This is configurable during `WasenderClient` initialization using the `RetryConfig` model.

```python
import os
from wasenderapi import WasenderClient
from wasenderapi.models import RetryConfig # Located in wasenderapi.models

# Example of configuring retry behavior.
# All parameters for RetryConfig are optional and have sensible defaults.
# Key defaults when enabled=True:
#   max_retries=3
#   initial_delay=1.0 (seconds)
#   backoff_factor=2.0
#   max_delay=60.0 (seconds)
#   http_status_codes_to_retry=[429, 500, 502, 503, 504]

# 1. Enable retries with default settings:
# This will enable retries (up to 3 attempts by default) for common transient errors like 429, 500, 502, 503, 504.
retry_config_default_enabled = RetryConfig(enabled=True)

# 2. Customize retry attempts, delays, and specific status codes:
custom_retry_config = RetryConfig(
    enabled=True,
    max_retries=5,                # Attempt up to 5 retries on specified errors
    initial_delay=0.5,            # Start with a 0.5-second delay for the first retry
    backoff_factor=1.5,           # Multiply delay by 1.5 for each subsequent retry (0.5s, 0.75s, 1.125s...)
    max_delay=30.0,               # Cap the maximum delay between retries at 30 seconds
    http_status_codes_to_retry=[429, 503] # Only retry on these specific HTTP status codes
)

# 3. Disable retries explicitly (this is also the default if no RetryConfig is provided):
retry_config_disabled = RetryConfig(enabled=False)


# Initialize clients with different retry configurations:
api_key_for_retry_example = os.getenv("WASENDER_API_KEY", "YOUR_API_KEY_HERE_RETRY_EXAMPLE")

if api_key_for_retry_example != "YOUR_API_KEY_HERE_RETRY_EXAMPLE":
    client_default_retries_on = WasenderClient(
        api_key=api_key_for_retry_example,
        retry_config=retry_config_default_enabled
    )
    print(f"Client initialized. Retries enabled (default settings): {client_default_retries_on.retry_config}")

    client_custom_retries = WasenderClient(
        api_key=api_key_for_retry_example,
        retry_config=custom_retry_config
    )
    print(f"Client initialized. Custom retries: {client_custom_retries.retry_config}")

    # Client with retries disabled (explicitly or by not passing retry_config)
    client_retries_disabled = WasenderClient(
        api_key=api_key_for_retry_example,
        retry_config=retry_config_disabled # or simply omit retry_config
    )
    print(f"Client initialized. Retries disabled: {client_retries_disabled.retry_config}")
else:
    print("\nSkipping WasenderClient initializations for retry config example: API key is a placeholder.")
    print("Set a valid WASENDER_API_KEY to see the initialized RetryConfig values.")

# Note on Behavior:
# - If the API response includes a `Retry-After` header (commonly sent with 429 errors),
#   the SDK will prioritize this header's value for the delay, overriding the calculated backoff.
# - Otherwise, it uses an exponential backoff strategy based on `initial_delay` and `backoff_factor`,
#   capped by `max_delay`.

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and create pull requests.

## License

This SDK is released under the [MIT License](./LICENSE).
