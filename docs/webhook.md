# Handling Wasender Webhooks with Python

This document explains how to receive and process webhook events from Wasender using the Wasender Python SDK. Webhooks allow your application to be notified in real-time about events such as incoming messages, message status updates, session status changes, and more.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Prerequisites

1.  **Webhook Endpoint:** A publicly accessible HTTPS URL on your server where Wasender can send POST requests (e.g., `https://your-app.com/wasender-webhook`).
2.  **Webhook Secret:** A secret string obtained from your Wasender dashboard or API provider. This is crucial for verifying the authenticity of incoming webhooks.
3.  **SDK Installation:** Ensure the Wasender Python SDK is correctly installed (`pip install wasenderapi`).
4.  **Web Framework:** A Python web framework (like Flask, FastAPI, Django, etc.) to receive the incoming HTTP POST requests from Wasender.

## Processing Incoming Webhooks with the SDK

The Wasender Python SDK provides a `client.handle_webhook_event()` method to simplify webhook processing. This method performs two key actions:

1.  **Signature Verification:** It verifies the incoming request using the `webhook_secret` you provide and the signature sent by Wasender (typically in an `x-webhook-signature` or similar header).
2.  **Event Parsing:** If the signature is valid, it parses the request body into a typed `WasenderWebhookEvent` Pydantic model.

### Using `client.handle_webhook_event()`

The method signature is:
```python
async def handle_webhook_event(
    self,
    headers: Dict[str, str],
    raw_body: bytes, # Important: use raw bytes of the body
    webhook_secret: str,
    signature_header_name: str = "x-webhook-signature", # Default, can be overridden
    timestamp_header_name: str = "x-webhook-timestamp" # Default, can be overridden if your provider uses it
) -> WasenderWebhookEvent:
    # ... implementation details ...
```

To use it, you need to:
1.  Obtain the dictionary of request headers from your web framework.
2.  Obtain the **raw request body as bytes** from your web framework. It is critical to use the raw body *before* any JSON parsing by your framework's middlewares for accurate signature verification.
3.  Provide your `webhook_secret`.
4.  (Optional) If your webhook provider uses different header names for the signature or an included timestamp (for replay attack prevention), you can specify `signature_header_name` and `timestamp_header_name`.

The method returns a parsed `WasenderWebhookEvent` object on success or raises a `WasenderAPIError` if:
*   The `webhook_secret` is invalid or not provided to the method.
*   The signature header is missing.
*   The signature is invalid (status code 401 will be in the error).
*   The request body cannot be read or parsed correctly as JSON after signature verification.
*   A timestamp is provided in headers and is outside the acceptable tolerance window (to prevent replay attacks).

**Important:** Your `WasenderClient` instance itself does **not** need to be initialized with the webhook secret. The secret is passed directly to the `handle_webhook_event` method when a webhook request is being processed.

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

This example demonstrates handling webhooks using **Flask**. Similar principles apply to FastAPI, Django, or other Python web frameworks.

```python
# app.py (Example Flask Webhook Handler)
import os
import logging
from flask import Flask, request, jsonify
from typing import Dict

from wasenderapi import WasenderClient
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models.webhook import (
    WasenderWebhookEvent,
    WasenderWebhookEventType,
    MessageCreatedEvent, # Assuming this is a defined specific event model
    SessionStatusEvent,  # Assuming this is a defined specific event model
    # Import other specific event types you want to handle explicitly
    # e.g., from wasenderapi.models.webhook_events import MessagesUpsertEvent, MessagesUpdateEvent
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize WasenderClient (API key and Persona Token might not be needed for just webhook handling)
# However, if your webhook handler also needs to make API calls, initialize client fully.
# For this example, we only need a client instance to access handle_webhook_event.
# The actual API calls within the handler would require a properly authenticated client.
wasender_client = WasenderClient(api_key="YOUR_DUMMY_API_KEY_IF_ONLY_HANDLING_WEBHOOKS") # Or your actual API key

# Get webhook secret from environment variable
WEBHOOK_SECRET = os.getenv("WASENDER_WEBHOOK_SECRET")

if not WEBHOOK_SECRET:
    logger.error("CRITICAL: WASENDER_WEBHOOK_SECRET environment variable not set.")
    # In a real app, you might want to prevent startup or handle this more gracefully

@app.route("/wasender-webhook", methods=["POST"])
async def handle_wasender_webhook():
    if not WEBHOOK_SECRET:
        logger.error("Webhook secret not configured. Rejecting request.")
        return jsonify({"error": "Webhook secret not configured"}), 500

    # Get headers as a dictionary
    headers_dict: Dict[str, str] = {k.lower(): v for k, v in request.headers.items()}
    
    # Get raw body as bytes
    raw_body: bytes = request.get_data()

    try:
        logger.info(f"Received webhook. Headers: {headers_dict}, Body (first 100 bytes): {raw_body[:100]}...")
        
        # Process the webhook event using the SDK
        webhook_event: WasenderWebhookEvent = await wasender_client.handle_webhook_event(
            headers=headers_dict,
            raw_body=raw_body,
            webhook_secret=WEBHOOK_SECRET
            # signature_header_name="x-wasender-signature" # If your provider uses a different header
        )

        logger.info(f"Successfully verified and parsed webhook. Event Type: {webhook_event.type.value}")

        # Handle the event based on its type
        # Using match statement (Python 3.10+)
        match webhook_event.type:
            case WasenderWebhookEventType.MESSAGE_CREATED: # Or the exact enum member from your SDK
                # Ensure webhook_event is narrowed to the correct type if possible, or access data carefully
                # For example, if your SDK uses a Union that Pydantic resolves:
                if isinstance(webhook_event, MessageCreatedEvent):
                    message_data = webhook_event.data.message
                    logger.info(f"New message from {message_data.from_number}: {message_data.text}")
                    # Add your business logic here (e.g., save to DB, send auto-reply)
                else:
                    logger.warning(f"Received MESSAGE_CREATED but model was {type(webhook_event)}. Data: {webhook_event.data}")
            
            case WasenderWebhookEventType.SESSION_STATUS:
                if isinstance(webhook_event, SessionStatusEvent):
                    status_data = webhook_event.data
                    logger.info(f"Session status update for session {webhook_event.session_id}: {status_data.status}")
                    if status_data.status == "NEED_SCAN":
                        logger.info("Action: QR code needs to be scanned for the session.")
                    # Add your logic for session status changes
                else:
                    logger.warning(f"Received SESSION_STATUS but model was {type(webhook_event)}. Data: {webhook_event.data}")

            # Add more cases for other WasenderWebhookEventType members you care about
            # e.g., WasenderWebhookEventType.MESSAGES_UPSERT, WasenderWebhookEventType.MESSAGES_UPDATE etc.
            
            case _:
                logger.info(f"Received an unhandled webhook event type: {webhook_event.type.value}")
                logger.info(f"Unhandled event data: {webhook_event.data.model_dump_json(indent=2) if hasattr(webhook_event.data, 'model_dump_json') else webhook_event.data}")

        # Always respond with a 2xx status code to acknowledge receipt
        return jsonify({"status": "success", "event_type_received": webhook_event.type.value}), 200

    except WasenderAPIError as e:
        logger.error(f"WasenderAPIError processing webhook: {e.message} (Status: {e.status_code})")
        # Respond with an appropriate error status based on the error type
        # e.g., 401 for signature mismatch, 400 for bad request
        return jsonify({"error": e.message, "details": e.api_message}), e.status_code or 400
    
    except Exception as e:
        logger.error(f"Generic error processing webhook: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    if not WEBHOOK_SECRET:
        print("ERROR: The WASENDER_WEBHOOK_SECRET environment variable must be set to run this Flask app.")
        print("Please set it and try again. Example: export WASENDER_WEBHOOK_SECRET='your_secret_here'")
    else:
        print(f"Webhook secret loaded. Starting Flask server on http://localhost:5000/wasender-webhook")
        # For production, use a proper WSGI server like Gunicorn or uWSGI
        # Example: gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
        app.run(debug=True, port=5000) # debug=True is not for production

```

**Explanation of the Flask Example:**

1.  **Imports:** Relevant modules from Flask, `wasenderapi`, and standard libraries.
2.  **Flask App & Client:** Initializes the Flask app and a `WasenderClient` instance. The client doesn't strictly need full API credentials if it's *only* used for `handle_webhook_event`, but if your handler needs to make calls back to the Wasender API (e.g., to fetch more details or send a reply), it should be fully initialized.
3.  **Webhook Secret:** Fetches the `WEBHOOK_SECRET` from an environment variable. This is crucial for security.
4.  **Route (`/wasender-webhook`):** Defines a POST endpoint to receive webhooks.
5.  **Get Headers and Raw Body:** Retrieves all request headers and the raw body (`request.get_data()`) as bytes. This is vital for the SDK's signature verification.
6.  **Call `handle_webhook_event`:** Passes the `headers`, `raw_body`, and `WEBHOOK_SECRET` to the SDK method.
7.  **Event Handling (`match webhook_event.type`):**
    *   Uses a `match` statement (Python 3.10+) to process different event types. For older Python versions, use `if/elif/else` on `webhook_event.type.value`.
    *   Inside each case, it's good practice to check the actual instance type (e.g., `isinstance(webhook_event, MessageCreatedEvent)`) if your `WasenderWebhookEvent` is a broad `Union` and Pydantic has resolved it to a specific type. This gives you type safety when accessing `webhook_event.data`.
    *   The `data` attribute of the event object will be an instance of the specific Pydantic model for that event (e.g., `MessageCreatedData`).
8.  **Acknowledge Receipt:** Responds with a `200 OK` status and a JSON body to acknowledge successful receipt and processing. If an error occurs, it responds with an appropriate HTTP error code (e.g., 400, 401, 500).
9.  **Error Handling:** Catches `WasenderAPIError` (e.g., for signature failures) and generic exceptions.
10. **Running the Flask App:** The `if __name__ == "__main__":` block shows how to run the development server. For production, a proper WSGI server should be used.

**Important Security Note:**

*   **Always verify webhook signatures.** The `handle_webhook_event` method does this for you if you provide the correct secret.
*   **Use HTTPS** for your webhook endpoint.
*   **Keep your webhook secret confidential.** Do not hardcode it; use environment variables or a secrets management system.
*   **Process asynchronously:** If your webhook processing involves lengthy tasks, perform them asynchronously (e.g., using a task queue like Celery or RQ) to ensure you respond to Wasender quickly (within a few seconds) to prevent timeouts and retries from Wasender.

This detailed example should help you integrate Wasender webhooks into your Python applications using Flask. Remember to adapt the specific event types and data models based on the exact definitions in your `wasenderapi.models.webhook` module.
