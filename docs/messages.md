# Wasender SDK: Message Sending Examples

This document provides detailed examples for sending various types of messages using the Wasender Python SDK.

## SDK Version: X.Y.Z (Update with your Python SDK version)

## Prerequisites

1.  **Install Python:** Version 3.8 or higher is recommended.
2.  **Obtain a Wasender API Key:** You'll need an API key from [https://www.wasenderapi.com](https://www.wasenderapi.com).
3.  **SDK Installation:** Ensure the Wasender Python SDK is correctly installed (`pip install wasenderapi`).

## Initializing the SDK

All examples assume you have initialized the SDK as follows. You can place this in a central part of your application or at the beginning of your script.

```python
# main_setup.py (or directly in your example scripts)
import asyncio
import os
from datetime import datetime, timezone

from wasenderapi import WasenderClient, DEFAULT_BASE_URL
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    RetryConfig,
    TextOnlyMessage,
    ImageUrlMessage,
    VideoUrlMessage,
    DocumentUrlMessage,
    AudioUrlMessage,
    StickerUrlMessage,
    ContactCardMessage,
    LocationPinMessage,
    WasenderMessagePayload # The Union type for generic send
)

# --- Credentials & Configuration ---
apikey = os.getenv("WASENDER_API_KEY")
persona_token = os.getenv("WASENDER_PERSONA_ACCESS_TOKEN") 
webhook_secret = os.getenv("WASENDER_WEBHOOK_SECRET") 

if not apikey:
    print("Error: WASENDER_API_KEY environment variable is not set.")
    apikey = "YOUR_API_KEY_HERE" 

# --- Client Instances ---
client = WasenderClient(api_key=apikey, persona_token=persona_token)

retry_options = RetryConfig(
    enabled=True, max_retries=2, initial_delay=1.0, backoff_factor=2.0,
    http_status_codes_to_retry=[429, 500, 502, 503, 504]
)
client_with_retries = WasenderClient(
    api_key=apikey, persona_token=persona_token, retry_config=retry_options
)

print(f"WasenderClient initialized for examples (API Key: {apikey[:4]}...)")

# --- Shared Helper Function for Sending Messages ---
async def send_message_example_helper(
    description: str,
    wasender_instance: WasenderClient, 
    payload: WasenderMessagePayload,
):
    print(f"\n--- {description} ---")
    if wasender_instance.api_key == "YOUR_API_KEY_HERE":
        print(f"Skipping API call for '{description}': API key is a placeholder.")
        return
    try:
        result = await wasender_instance.send(payload)
        print(f"Message Sent Successfully via generic send()!")
        if result.response:
            print(f"  Response Message ID: {result.response.message_id}")
            print(f"  Response Status: {result.response.message}")
        if result.rate_limit:
            reset_time_str = "N/A"
            if result.rate_limit.reset_timestamp:
                reset_dt = datetime.fromtimestamp(result.rate_limit.reset_timestamp, tz=timezone.utc).astimezone()
                reset_time_str = reset_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(
                f"  Rate Limit Info: {result.rate_limit.remaining}/{result.rate_limit.limit} "
                f"(Resets at: {reset_time_str})"
            )
        else:
            print("  Rate limit information not available for this response.")
    except WasenderAPIError as e:
        print(f"API Error during '{description}':")
        print(f"  Status Code: {e.status_code or 'N/A'}")
        print(f"  API Message: {e.api_message or 'No specific API message.'}")
        if e.error_details:
            print(f"  Error Details Code: {e.error_details.code}")
            print(f"  Error Details Message: {e.error_details.message}")
        if e.rate_limit:
            reset_time_str = "N/A"
            if e.rate_limit.reset_timestamp:
                reset_dt = datetime.fromtimestamp(e.rate_limit.reset_timestamp, tz=timezone.utc).astimezone()
                reset_time_str = reset_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(
                f"  Rate Limit at Error: {e.rate_limit.remaining}/{e.rate_limit.limit} "
                f"(Resets at: {reset_time_str})"
            )
        if hasattr(e, 'retry_after') and e.retry_after:
             print(f"  Retry After: {e.retry_after} seconds")
    except Exception as e:
        print(f"An unexpected error occurred during '{description}': {type(e).__name__} - {e}")

# --- Example Recipient Identifiers (Replace with actual test data) ---
recipient_phone_number_jid = "12345678900@s.whatsapp.net" 
recipient_group_jid = "1234567890-1234567890@g.us" 

# --- Individual Message Type Examples Follow (main_setup.py content ends here for copy-pasting) ---
```

**Note:** Ensure the `WASENDER_API_KEY` is set. The above `main_setup.py` block can be copied to the beginning of each example file or run once if examples are in the same script.

## Sending Different Message Types

The SDK uses a generic `client.send(payload: WasenderMessagePayload)` method that accepts a Pydantic model instance. The `WasenderMessagePayload` is a `Union` of all specific message types. You define the `message_type` (as a field within the specific Pydantic model) and provide the corresponding properties.

Helper methods like `client.send_text(...)`, `client.send_image(...)`, etc., are also available for convenience.

### 1. Text Message

Sends a simple plain text message.

```python
# examples/send_text_example.py
# Ensure content from main_setup.py (client, helper, recipients) is available before this.

async def send_plain_text_message():
    # Using the generic send() with a Pydantic model
    text_payload = TextOnlyMessage(
        to=recipient_phone_number_jid,
        # message_type="text", # Not needed if TextOnlyMessage Pydantic model sets it or if it's inferred
        text="Hello from the Wasender Python SDK! This is a plain text message sent via generic send().",
    )
    await send_message_example_helper(
        "Sending Text Message (Generic Send)", 
        client, 
        text_payload
    )

    # Alternatively, using the specific helper method client.send_text()
    print("\n--- Sending Text Message (Helper Method) ---")
    if client.api_key == "YOUR_API_KEY_HERE":
        print("Skipping API call: API key is a placeholder.")
        return
    try:
        result = await client.send_text(
            to_jid=recipient_phone_number_jid, 
            text="Hello from the send_text() helper!"
        )
        print(f"Message sent successfully via helper. Message ID: {result.response.message_id}")
        if result.rate_limit: print(f"  Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit}")
    except WasenderAPIError as e:
        print(f"API Error (helper): {e.api_message or e.status_code}")
    except Exception as e:
        print(f"Unexpected Error (helper): {e}")

async def main():
    # Make sure main_setup.py content is effectively included/run once above this
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run text examples: WASENDER_API_KEY is a placeholder.")
        return
    await send_plain_text_message()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. Image Message (with Retry Logic Example)

Sends an image from a URL. This example also demonstrates enabling retry logic for the Wasender client.

```python
# examples/send_image_example.py
# Ensure content from main_setup.py (client_with_retries, helper, recipients) is available.

async def send_image_message_with_retry_logic():
    # Using generic send() with the client_with_retries instance
    image_payload = ImageUrlMessage(
        to=recipient_phone_number_jid,
        # message_type="image", # Pydantic model might define this
        image_url="https://www.example.com/image.jpg", # Replace with a valid public image URL
        text="Check out this cool image! (Sent with generic send + retry client)", # Optional caption
    )
    await send_message_example_helper(
        "Sending Image Message (Generic Send with Retry Client)", 
        client_with_retries, # Using the client configured with retries
        image_payload
    )

    # Alternatively, using the specific helper method client.send_image()
    # The helper will use the retry config of the client instance it's called on.
    print("\n--- Sending Image Message (Helper Method with Retry Client) ---")
    if client_with_retries.api_key == "YOUR_API_KEY_HERE":
        print("Skipping API call: API key is a placeholder.")
        return
    try:
        result = await client_with_retries.send_image(
            to_jid=recipient_phone_number_jid,
            image_url="https://www.example.com/another_image.png", # Replace URL
            caption="Another image via send_image() helper! (Retry client)"
        )
        print(f"Image sent successfully via helper. Message ID: {result.response.message_id}")
        if result.rate_limit: print(f"  Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit}")
    except WasenderAPIError as e:
        print(f"API Error (helper): {e.api_message or e.status_code}")
    except Exception as e:
        print(f"Unexpected Error (helper): {e}")

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run image examples: WASENDER_API_KEY is a placeholder.")
        return
    await send_image_message_with_retry_logic()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Video Message

Sends a video from a URL.

```python
# examples/send_video_example.py
# Ensure content from main_setup.py (client, helper, recipients) is available.

async def send_video_message_example():
    video_payload = VideoUrlMessage(
        to=recipient_phone_number_jid,
        # message_type="video", # Pydantic model may define this
        video_url="https://www.example.com/video.mp4", # Replace with a valid public video URL (MP4, 3GPP, max 16MB)
        text="Watch this exciting video! (Sent via generic send)", # Optional caption
    )
    await send_message_example_helper(
        "Sending Video Message (Generic Send)", 
        client, 
        video_payload
    )

    # You can also use client.send_video() helper if available and preferred.
    # Example (if client.send_video exists):
    # print("\n--- Sending Video Message (Helper Method) ---")
    # try:
    #     result = await client.send_video(
    #         to_jid=recipient_phone_number_jid,
    #         video_url="https://www.example.com/another_video.mp4",
    #         caption="Another video via send_video() helper!"
    #     )
    #     print(f"Video sent successfully via helper. Message ID: {result.response.message_id}")
    # except Exception as e:
    #     print(f"Error sending video via helper: {e}")

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run video example: WASENDER_API_KEY is a placeholder.")
        return
    await send_video_message_example()

if __name__ == "__main__":
    asyncio.run(main())
```

### 4. Document Message

Sends a document from a URL.

```python
# examples/send_document_example.py
# Ensure content from main_setup.py (client, helper, recipients) is available.

async def send_document_message_example():
    document_payload = DocumentUrlMessage(
        to=recipient_phone_number_jid,
        # message_type="document",
        document_url="https://www.example.com/document.pdf", # Replace with valid URL (PDF, DOCX, etc., max 100MB)
        text="Here is the document you requested. (Sent via generic send)", # Optional caption
        # filename="custom_filename.pdf" # Optional: custom filename for the document
    )
    await send_message_example_helper(
        "Sending Document Message (Generic Send)",
        client,
        document_payload
    )
    # Helper: await client.send_document(...)

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run document example: WASENDER_API_KEY is a placeholder.")
        return
    await send_document_message_example()

if __name__ == "__main__":
    asyncio.run(main())
```

### 5. Audio Message (as Voice Note)

Sends an audio file from a URL, typically rendered as a voice note.

```python
# examples/send_audio_example.py
# Ensure content from main_setup.py (client, helper, recipients) is available.

async def send_audio_message_example():
    audio_payload = AudioUrlMessage(
        to=recipient_phone_number_jid,
        # message_type="audio",
        audio_url="https://www.example.com/audio.mp3", # Replace with valid URL (AAC, MP3, OGG, AMR, max 16MB)
        # text: "Listen to this audio." # Optional, but typically not used for voice notes
        # ptt: True # Optional: True to send as a push-to-talk voice note, False for regular audio file.
                  # The Pydantic model AudioUrlMessage should have a field for this if supported.
    )
    await send_message_example_helper(
        "Sending Audio Message (Voice Note via Generic Send)", 
        client, 
        audio_payload
    )
    # Helper: await client.send_audio(...)

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run audio example: WASENDER_API_KEY is a placeholder.")
        return
    await send_audio_message_example()

if __name__ == "__main__":
    asyncio.run(main())
```

### 6. Sticker Message

Sends a sticker from a URL. Stickers must be in `.webp` format.

```python
# examples/send_sticker_example.py
# Ensure content from main_setup.py (client, helper, recipients) is available.

async def send_sticker_message_example():
    sticker_payload = StickerUrlMessage(
        to=recipient_phone_number_jid,
        # message_type="sticker",
        sticker_url="https://www.example.com/sticker.webp" # Replace with valid .webp URL (max 100KB)
        # `text` is not applicable for stickers
    )
    await send_message_example_helper(
        "Sending Sticker Message (Generic Send)", 
        client, 
        sticker_payload
    )
    # Helper: await client.send_sticker(...)

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run sticker example: WASENDER_API_KEY is a placeholder.")
        return
    await send_sticker_message_example()

if __name__ == "__main__":
    asyncio.run(main())
```

### 7. Contact Card Message

Sends a contact card. This example also demonstrates enabling retry logic for the Wasender client, showing it can be applied to any message type.

```python
# examples/send_contact_card_example.py
# Ensure content from main_setup.py (client_with_retries, helper, recipients) is available.

async def send_contact_card_example():
    # The `contact` field in ContactCardMessage should be a dictionary or a Pydantic model 
    # representing the contact's details. Common fields are name and phone.
    # Assuming the SDK expects a dict like: {"name": "Test Name", "phone": "+12345..."}
    # or a specific Pydantic model for the contact card itself.
    contact_card_payload = ContactCardMessage(
        to=recipient_phone_number_jid,
        # message_type="contact", # Pydantic model may define this
        contact={"name": "John Doe", "phone": "+19876543210"}, # The contact to send
        text="Here is John Doe's contact information. (Sent with generic send + retry client)" # Optional caption
    )
    # Using the client_with_retries instance for this example
    await send_message_example_helper(
        "Sending Contact Card Message (Generic Send with Retry Client)",
        client_with_retries, 
        contact_card_payload
    )
    # Helper: await client_with_retries.send_contact(...)

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run contact card example: WASENDER_API_KEY is a placeholder.")
        return
    await send_contact_card_example()

if __name__ == "__main__":
    asyncio.run(main())
```

### 8. Location Pin Message

Sends a location pin with latitude and longitude.

```python
# examples/send_location_pin_example.py
# Ensure content from main_setup.py (client, helper, recipients) is available.

async def send_location_pin_example():
    # The `location` field in LocationPinMessage should be a dictionary or a Pydantic model.
    location_data = {
        "latitude": 37.7749,  # Example: San Francisco
        "longitude": -122.4194, # Example: San Francisco
        "name": "OpenAI HQ",       # Optional name for the location
        "address": "Pioneer Building, San Francisco, CA" # Optional address
    }
    location_pin_payload = LocationPinMessage(
        to=recipient_phone_number_jid,
        # message_type="location",
        location=location_data,
        text="Meet me at this location! (Sent via generic send)" # Optional caption
    )
    await send_message_example_helper(
        "Sending Location Pin Message (Generic Send)", 
        client, 
        location_pin_payload
    )
    # Helper: await client.send_location(...)

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run location pin example: WASENDER_API_KEY is a placeholder.")
        return
    await send_location_pin_example()

if __name__ == "__main__":
    asyncio.run(main())
```

## Using Specific Helper Methods

The Python SDK also provides specific helper methods for convenience (e.g., `client.send_text(...)`, `client.send_image(...)`). These are wrappers around the generic `client.send(...)` method and automatically construct the appropriate Pydantic model and set the `message_type` for you. When using these helpers, you typically pass the content directly (like `text`, `image_url`, `caption`, etc.) rather than a full Pydantic model payload.

### Example: Sending Text using `client.send_text()`

```python
# examples/send_text_with_helper_example.py
# Ensure content from main_setup.py (client, recipients) is available.

async def send_text_message_via_helper():
    print("\n--- Sending Text Message via client.send_text() Helper ---")
    if client.api_key == "YOUR_API_KEY_HERE":
        print("Skipping API call for send_text_message_via_helper: API key is a placeholder.")
        return

    try:
        # Notice we pass parameters like `to_jid` and `text` directly.
        result = await client.send_text(
            to_jid=recipient_phone_number_jid,
            text="Hello from the client.send_text() helper method! Easy and direct."
        )
        print(f"Text Sent Successfully via helper. Message ID: {result.response.message_id}")
        print(f"  Status: {result.response.message}")
        if result.rate_limit:
            reset_time_str = "N/A"
            if result.rate_limit.reset_timestamp:
                reset_dt = datetime.fromtimestamp(result.rate_limit.reset_timestamp, tz=timezone.utc).astimezone()
                reset_time_str = reset_dt.strftime('%Y-%m-%d %H:%M:%S %Z')
            print(f"  Rate Limit: {result.rate_limit.remaining}/{result.rate_limit.limit} (Resets: {reset_time_str})")
        else:
            print("  Rate limit info not available.")

    except WasenderAPIError as e:
        print(f"API Error (send_text helper): Status {e.status_code}, Msg: {e.api_message or 'N/A'}")
        if e.error_details: print(f"  Details: Code {e.error_details.code}, Msg: {e.error_details.message}")
    except Exception as e:
        print(f"An unexpected error occurred (send_text helper): {type(e).__name__} - {e}")

async def main():
    if apikey == "YOUR_API_KEY_HERE":
        print("Cannot run send_text_message_via_helper: WASENDER_API_KEY is a placeholder.")
        return
    await send_text_message_via_helper()

if __name__ == "__main__":
    asyncio.run(main())
```

You can use similar helper methods for other common message types. Refer to the SDK's client method documentation for the exact signatures (parameters like `to_jid`, `image_url`, `caption`, `contact_name`, `contact_phone`, `latitude`, `longitude`, etc.):

- `client.send_image(to_jid: str, image_url: str, caption: Optional[str] = None, ...)`
- `client.send_video(to_jid: str, video_url: str, caption: Optional[str] = None, ...)`
- `client.send_document(to_jid: str, document_url: str, caption: Optional[str] = None, filename: Optional[str] = None, ...)`
- `client.send_audio(to_jid: str, audio_url: str, ptt: bool = False, ...)`
- `client.send_sticker(to_jid: str, sticker_url: str, ...)`
- `client.send_contact(to_jid: str, contact_name: str, contact_phone: str, ...)`
- `client.send_location(to_jid: str, latitude: float, longitude: float, name: Optional[str] = None, address: Optional[str] = None, ...)`

(Note: The exact parameters for helper methods should be verified against the actual Python SDK implementation. The list above is illustrative.)

## Error Handling and Rate Limiting

API interactions can result in errors, or you might hit rate limits. The Python SDK handles this by raising a `WasenderAPIError` (from `wasenderapi.errors`) for API-specific issues.

Key attributes of `WasenderAPIError` include:

- `status_code` (Optional[int]): The HTTP status code of the error response (e.g., 400, 401, 429, 500).
- `api_message` (Optional[str]): The primary error message string from the Wasender API response body (e.g., from a `{"message": "..."}` field).
- `error_details` (Optional[WasenderErrorDetail]): Structured error details if provided by the API (e.g., `{"code": "some_code", "message": "detailed info"}`). `WasenderErrorDetail` is a Pydantic model.
- `rate_limit` (Optional[RateLimitInfo]): If the error included rate limit information (especially for 429 errors), this attribute will contain a `RateLimitInfo` Pydantic model instance.
- `retry_after` (Optional[int]): If the error was a 429 (Too Many Requests) and the API provided a `Retry-After` header, this attribute stores the suggested delay in seconds.

The `RateLimitInfo` Pydantic model (from `wasenderapi.models`) is also available on successful response objects (e.g., `result.rate_limit`) and on `WasenderAPIError` instances (`error.rate_limit`). It provides:

- `limit` (Optional[int]): The rate limit cap for the current window.
- `remaining` (Optional[int]): The number of requests remaining in the current window.
- `reset_timestamp` (Optional[int]): A Unix timestamp (in seconds) indicating when the rate limit window resets.

Refer to the `send_message_example_helper` function in the "Initializing the SDK" section and the specific error handling in the `send_text_message_via_helper` example for patterns on how to catch and inspect these errors and their attributes.

This comprehensive set of examples should help you effectively use the Wasender Python SDK to send various message types and manage API interactions robustly.
