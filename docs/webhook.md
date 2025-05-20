# Handling Wasender Webhooks with Python

This document explains how to receive and process webhook events from Wasender using the Wasender Python SDK. Webhooks allow your application to be notified in real-time about events such as incoming messages, message status updates, session status changes, and more.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Prerequisites

1.  **Webhook Endpoint:** A publicly accessible HTTPS URL on your server where Wasender can send POST requests (e.g., `https://your-app.com/wasender-webhook`).
2.  **Webhook Secret:** A secret string obtained from your Wasender dashboard or API provider. This is crucial for verifying the authenticity of incoming webhooks.
3.  **SDK Installation:** Ensure the Wasender Python SDK is correctly installed (`pip install wasenderapi`).
4.  **Web Framework:** A Python web framework (like Flask, FastAPI, Django, etc.) to receive the incoming HTTP POST requests from Wasender.

## Processing Incoming Webhooks with the SDK

The Wasender Python SDK provides a `client.handle_webhook_event()` method (available on both `WasenderAsyncClient` and `WasenderSyncClient`) to simplify webhook processing. This method performs two key actions:

1.  **Signature Verification:** It verifies the incoming request using the `webhook_secret` (configured on the client instance) and the signature sent by Wasender (typically in an `x-webhook-signature` or similar header).
2.  **Event Parsing:** If the signature is valid, it parses the request body into a typed `WasenderWebhookEvent` Pydantic model.

### Using `client.handle_webhook_event()`

For `WasenderAsyncClient`, the method signature is:
```python
async def handle_webhook_event(
    self,
    request_body_bytes: bytes, # Raw request body as bytes
    signature_header: Optional[str] # Value of the signature header (e.g., X-Wasender-Signature)
) -> WasenderWebhookEvent:
    # ... implementation details ...
```
*(The `WasenderSyncClient` also has an `async def handle_webhook_event` with the same signature, which might be unexpected for a sync client. For webhook handling in an async framework like Flask/FastAPI, using `WasenderAsyncClient` is generally more natural.)*

To use it (example with `WasenderAsyncClient`):
1.  Initialize your `WasenderAsyncClient` (or `WasenderSyncClient`) with your `api_key` and `webhook_secret`.
2.  Obtain the **raw request body as bytes** from your web framework. It is critical to use the raw body *before* any JSON parsing by your framework's middlewares for accurate signature verification.
3.  Obtain the value of the signature header (e.g., `X-Wasender-Signature`) from the request headers.

The method returns a parsed `WasenderWebhookEvent` object on success or raises a `WasenderAPIError` if:
*   The `webhook_secret` is not configured on the client or is invalid.
*   The signature header is missing or the signature is invalid (status code 401 or 400 will be in the error).
*   The request body cannot be read or parsed correctly as JSON after signature verification.

**Important:** The `webhook_secret` **must be provided during client initialization** (e.g., to `create_async_wasender`) for `handle_webhook_event` to work, as it uses `self.webhook_secret`.

## Webhook Event Structure in Python

All webhook events are Pydantic models and are part of the `WasenderWebhookEvent` discriminated union, defined in `wasenderapi.models.webhook`. The specific type of event is determined by the `type` field, which corresponds to the `WasenderWebhookEventType` enum.

```python
# Conceptual structure from wasenderapi/models/webhook.py
from enum import Enum
from typing import Union, Generic, TypeVar, Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field

class WasenderWebhookEventType(str, Enum):
    MESSAGE_CREATED = "message.created" # Example event type
    MESSAGE_UPDATED = "message.updated"
    SESSION_STATUS = "session.status"
    # ... many other event types, e.g.:
    # MESSAGES_UPSERT = "messages.upsert"
    # MESSAGES_UPDATE = "messages.update" # For status like sent, delivered, read
    # SESSION_QR_CODE_UPDATED = "session.qr_code.updated"
    # GROUP_PARTICIPANTS_UPDATE = "group.participants.update"

DT = TypeVar("DT") # Type variable for the data field

class BaseWebhookEvent(BaseModel, Generic[DT]):
    type: WasenderWebhookEventType
    timestamp: Optional[int] = None # Unix timestamp of event generation
    data: DT
    # These fields might vary based on your specific API provider/SDK version
    session_id: Optional[str] = Field(None, alias="sessionId")
    instance_id: Optional[str] = Field(None, alias="instanceId") 
    api_key_id: Optional[str] = Field(None, alias="apiKeyId")

# --- Example Specific Event Data Models (Illustrative) ---
# (Refer to actual models in wasenderapi.models.webhook_events for accuracy)

class MessageInfo(BaseModel):
    id: str
    from_number: str = Field(alias="from")
    to_number: str = Field(alias="to")
    type: str # e.g., "text", "image"
    text: Optional[str] = None # For text messages
    # ... other common message fields like timestamp, media_url, etc.

class MessageCreatedData(BaseModel):
    message: MessageInfo
    # ... other potential fields in message.created data

class MessageCreatedEvent(BaseWebhookEvent[MessageCreatedData]):
    type: Literal[WasenderWebhookEventType.MESSAGE_CREATED] = WasenderWebhookEventType.MESSAGE_CREATED
    data: MessageCreatedData

class SessionStatusData(BaseModel):
    status: str # e.g., "CONNECTED", "NEED_SCAN", "DISCONNECTED"
    reason: Optional[str] = None

class SessionStatusEvent(BaseWebhookEvent[SessionStatusData]):
    type: Literal[WasenderWebhookEventType.SESSION_STATUS] = WasenderWebhookEventType.SESSION_STATUS
    data: SessionStatusData

# The main discriminated union would be defined in wasenderapi.models.webhook as:
# WasenderWebhookEvent = Union[
# MessageCreatedEvent,
# SessionStatusEvent,
# MessagesUpsertEvent, # Actual event types from the SDK
# MessagesUpdateEvent,
# GroupUpdateEvent,
# ... etc.
# ]
```

When `handle_webhook_event()` successfully parses an event, you will get an instance of one of the specific event Pydantic models (e.g., `MessageCreatedEvent` or `SessionStatusEvent` if those are the actual names in your SDK). You can then access its `type` and `data` attributes, where `data` will be an instance of the corresponding data model (e.g., `MessageCreatedData`).

### Common Event Types (`WasenderWebhookEventType`)

The `type` property (an instance of `WasenderWebhookEventType` enum) indicates the kind of event. Key event categories often include:

*   **Message Events:**
    *   `MESSAGE_CREATED` (or similar like `MESSAGES_UPSERT`): New incoming message.
    *   `MESSAGE_UPDATED` (or similar like `MESSAGES_UPDATE`): Message status update (e.g., sent, delivered, read).
*   **Session Events:**
    *   `SESSION_STATUS`: Changes in your session status (e.g., connected, disconnected, need_scan).
    *   `SESSION_QR_CODE_UPDATED`: A new QR code is available for scanning.
*   **Group Events:** `GROUP_UPDATE`, `GROUP_PARTICIPANTS_UPDATE`, etc.

*This is not an exhaustive list. Always refer to the specific `WasenderWebhookEventType` enum and the event model definitions in `wasenderapi.models.webhook` and `wasenderapi.models.webhook_events` (or similar paths in your SDK) for the definitive list of supported event types and their data structures.*

## Detailed Python Webhook Handler Example (Flask)

This example demonstrates handling webhooks using **Flask** with `WasenderAsyncClient`.

```python
# app.py (Example Flask Webhook Handler)
import os
import logging
import asyncio # Required for running async client methods in Flask
from flask import Flask, request, jsonify
from typing import Dict, Optional # Optional for signature_header

# Corrected imports
from wasenderapi import create_async_wasender, WasenderAsyncClient
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models.webhook import (
    WasenderWebhookEvent,
    WasenderWebhookEventType,
    # Assuming these specific event types are correctly defined in your SDK:
    # from wasenderapi.models.webhook_events import MessageCreatedEvent, SessionStatusEvent
    # For the example, we'll rely on isinstance checks or access common fields.
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# --- SDK Initialization ---
API_KEY = os.getenv("WASENDER_API_KEY", "YOUR_FALLBACK_API_KEY") # Fallback for local dev if needed
WEBHOOK_SECRET = os.getenv("WASENDER_WEBHOOK_SECRET")

if not WEBHOOK_SECRET:
    logger.error("CRITICAL: WASENDER_WEBHOOK_SECRET environment variable not set.")
    # In a real app, you might want to prevent startup or handle this more gracefully

# Initialize WasenderAsyncClient with webhook_secret
# The API key might be needed if you intend to make API calls from within the webhook handler.
# If only verifying and parsing, a dummy API key might suffice if your client requires one.
async_wasender_client = create_async_wasender(
    api_key=API_KEY, 
    webhook_secret=WEBHOOK_SECRET
)

@app.route("/wasender-webhook", methods=["POST"])
async def handle_wasender_webhook(): # Flask allows async routes
    if not async_wasender_client.webhook_secret: # Check if client has secret
        logger.error("Webhook secret not configured on client. Rejecting request.")
        return jsonify({"error": "Webhook secret not configured on client"}), 500

    # Get signature header (ensure your header name matches what Wasender sends)
    # Common names: "x-wasender-signature", "x-webhook-signature", "x-hub-signature-256"
    signature: Optional[str] = request.headers.get("X-Wasender-Signature") 
    # Or adapt to the actual header name used by Wasender API

    # Get raw body as bytes
    raw_body: bytes = request.get_data()

    try:
        logger.info(f"Received webhook. Signature Header: {signature}, Body (first 100 bytes): {raw_body[:100]}...")
        
        # Process the webhook event using the SDK
        # Ensure the client is used in an async context if it manages an HTTP client internally
        async with async_wasender_client: # Use async context manager if client makes internal http calls or needs setup/teardown
            webhook_event: WasenderWebhookEvent = await async_wasender_client.handle_webhook_event(
                request_body_bytes=raw_body,
                signature_header=signature
            )

        logger.info(f"Successfully verified and parsed webhook. Event Type: {webhook_event.type.value}")

        # Handle the event based on its type
        # (Using if/elif for broader Python compatibility in docs, match is 3.10+)
        event_type_value = webhook_event.type.value

        if event_type_value == WasenderWebhookEventType.MESSAGE_CREATED.value: # Compare enum values
            # Accessing data safely (assuming data is a Pydantic model)
            # Actual specific event model (e.g., MessageCreatedEvent) should be used for type safety if available
            message_info = webhook_event.data.get("message") if isinstance(webhook_event.data, dict) else getattr(webhook_event.data, "message", None)
            if message_info:
                from_number = message_info.get("from") if isinstance(message_info, dict) else getattr(message_info, "from_number", None)
                text_content = message_info.get("text") if isinstance(message_info, dict) else getattr(message_info, "text", None)
                logger.info(f"New message from {from_number}: {text_content}")
            else:
                logger.warning(f"Message data not found in expected structure for MESSAGE_CREATED. Data: {webhook_event.data}")
        
        elif event_type_value == WasenderWebhookEventType.SESSION_STATUS.value:
            status_info = webhook_event.data.get("status") if isinstance(webhook_event.data, dict) else getattr(webhook_event.data, "status", None)
            session_id = webhook_event.session_id # Access common field from BaseWebhookEvent
            logger.info(f"Session status update for session {session_id}: {status_info}")
            if status_info == WhatsAppSessionStatus.NEED_SCAN.value:
                logger.info("Action: QR code needs to be scanned for the session.")
        
        # Add more elif blocks for other WasenderWebhookEventType members

        else:
            logger.info(f"Received an unhandled webhook event type: {event_type_value}")
            # data_dump = webhook_event.data.model_dump_json(indent=2) if hasattr(webhook_event.data, 'model_dump_json') else str(webhook_event.data)
            # logger.info(f"Unhandled event data: {data_dump}")

        # Always respond with a 2xx status code to acknowledge receipt
        return jsonify({"status": "success", "event_type_received": event_type_value}), 200

    except WasenderAPIError as e:
        logger.error(f"WasenderAPIError processing webhook: {e.message} (Status: {e.status_code})")
        return jsonify({"error": e.message, "details": e.api_message}), e.status_code or 400
    
    except Exception as e:
        logger.error(f"Generic error processing webhook: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

async def main(): # Added async main for running the app with an async server if needed
    # This part is for running Flask with an ASGI server like Hypercorn or Uvicorn
    # For simplicity in docs, we often show `app.run()`, but for async routes, ASGI is better.
    # Example: hypercorn app:app
    # If using app.run(), ensure it's compatible with async routes or use Flask-Async.
    pass

if __name__ == "__main__":
    if not WEBHOOK_SECRET:
        print("ERROR: The WASENDER_WEBHOOK_SECRET environment variable must be set.")
    else:
        logger.info("Flask app ready. Run with an ASGI server like Uvicorn or Hypercorn for async routes.")
        logger.info("Example: uvicorn app:app --host 0.0.0.0 --port 5000")
        # For development only, Flask's built-in server (not for production):
        # app.run(debug=True, port=5000) 
```

### Key Steps in the Flask Example:
1.  **SDK Initialization:** Initialize `WasenderAsyncClient` with your `api_key` and `webhook_secret`.
2.  **Signature Header:** Obtain the signature header from the request headers.
3.  **Raw Body:** Obtain the raw body as bytes from the request.
4.  **Event Processing:** Use the `handle_webhook_event` method to process the event.
5.  **Event Handling:** Handle the event based on its type.
6.  **Response:** Respond with a 2xx status code to acknowledge successful receipt and processing.

**Important Security Note:**

*   **Always verify webhook signatures.** The `handle_webhook_event` method does this for you if you provide the correct secret.
*   **Use HTTPS** for your webhook endpoint.
*   **Keep your webhook secret confidential.** Do not hardcode it; use environment variables or a secrets management system.
*   **Process asynchronously:** If your webhook processing involves lengthy tasks, perform them asynchronously (e.g., using a task queue like Celery or RQ) to ensure you respond to Wasender quickly (within a few seconds) to prevent timeouts and retries from Wasender.

This detailed example should help you integrate Wasender webhooks into your Python applications using Flask. Remember to adapt the specific event types and data models based on the exact definitions in your `wasenderapi.models.webhook` module.
