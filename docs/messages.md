# Wasender SDK: Message Sending Examples

This document provides detailed examples for sending various types of messages using the Wasender Python SDK.

## SDK Version: X.Y.Z (Update with your Python SDK version)

## Prerequisites

1.  **Install Python:** Version 3.8 or higher is recommended.
2.  **Obtain a Wasender API Key:** You'll need an API key from [https://www.wasenderapi.com](https://www.wasenderapi.com).
3.  **SDK Installation:** Ensure the Wasender Python SDK is correctly installed (`pip install wasenderapi`).

## Initializing the SDK

All examples assume you have initialized the SDK. Choose the appropriate client (Sync or Async) for your needs.

```python
# main_setup.py (or directly in your example scripts)
import asyncio
import os
from datetime import datetime, timezone

# Import clients and configuration
from wasenderapi import (
    create_sync_wasender,
    create_async_wasender,
    WasenderSyncClient, # For type hinting if needed
    WasenderAsyncClient # For type hinting if needed
)
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    RetryConfig,
    # Specific Pydantic models for generic send() (if shown as advanced examples)
    BaseMessage, # Generic payload type for client.send()
    TextOnlyMessage,
    ImageMessage, 
    VideoMessage,
    DocumentMessage,
    AudioMessage,
    StickerMessage,
    ContactMessage,
    LocationMessage
)

# --- Credentials & Configuration ---
api_key = os.getenv("WASENDER_API_KEY")
personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN") 
webhook_secret = os.getenv("WASENDER_WEBHOOK_SECRET")     

if not api_key:
    print("Error: WASENDER_API_KEY environment variable not set.")
    api_key = "YOUR_API_KEY_PLACEHOLDER" # Use a placeholder for docs if not set

# --- Client Instances ---
# Synchronous Client
sync_client = create_sync_wasender(api_key=api_key, personal_access_token=personal_access_token)

# Asynchronous Client (recommended to be used with async with)
# async_client = create_async_wasender(api_key=api_key, personal_access_token=personal_access_token)

# Optional: Configure retry behavior for a client instance
retry_config = RetryConfig(
    enabled=True, 
    max_retries=2, 
    # initial_delay=1.0, # Assuming RetryConfig has these if needed
    # backoff_factor=2.0,
    # http_status_codes_to_retry=[429, 500, 502, 503, 504]
)
sync_client_with_retries = create_sync_wasender(
    api_key=api_key, 
    personal_access_token=personal_access_token, 
    retry_options=retry_config
)
# async_client_with_retries = create_async_wasender(
#     api_key=api_key, 
#     personal_access_token=personal_access_token, 
#     retry_options=retry_config
# )

print(f"SDK Clients initialized for examples (API Key: {api_key[:4]}...)")

# --- Shared Helper Function for Generic Send (Advanced) ---
async def send_generic_message_advanced_helper(
    description: str,
    async_client_instance: WasenderAsyncClient, # Example for async generic send
    payload: BaseMessage,
):
    print(f"\n--- {description} (Generic Send - Advanced) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print(f"Skipping API call for '{description}': API key is a placeholder.")
        return
    try:
        result = await async_client_instance.send(payload) # Using generic send
        print(f"Message Sent Successfully via generic send()!")
        if result.response:
            print(f"  Response Message ID: {result.response.data.message_id}")
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

# Example for sync generic send (if needed for an example)
# def send_generic_sync_message_advanced_helper(
#     description: str,
#     sync_client_instance: WasenderSyncClient,
#     payload: BaseMessage,
# ):
#     print(f"\n--- {description} (Generic Send - Advanced Sync) ---")
#     # ... similar logic for sync client ...
#     result = sync_client_instance.send(payload)
#     # ... print results ...

# --- Example Recipient Identifiers (Replace with actual test data) ---
recipient_phone_number = "12345678900" # Use phone number directly for helpers
# recipient_phone_number_jid = "12345678900@s.whatsapp.net" # For generic send if it requires JID
# recipient_group_jid = "1234567890-1234567890@g.us" 

print("Finished main_setup block for examples.")
# --- Individual Message Type Examples Follow ---
```

**Note:** Ensure the `WASENDER_API_KEY` is set. The above setup block can be copied or adapted.

## Sending Different Message Types

The SDK provides specific helper methods (e.g., `sync_client.send_text(...)`, `await async_client.send_image(...)`) as the **easiest and recommended way** to send common messages. These methods accept direct parameters like `to`, `text_body`, `url`, `caption`, etc., and handle payload construction internally.

For advanced scenarios, or for message types that may not have dedicated helper methods, you can use the generic `client.send(payload: BaseMessage)` method. This requires you to manually construct a Pydantic model instance (e.g., `TextOnlyMessage`, `ImageMessage` from `wasenderapi.models`) and pass it as the `payload`.

All examples below will primarily showcase the helper methods for both synchronous and asynchronous clients. Examples using the generic `send()` will be marked as advanced or alternative.

### 1. Text Message

Sends a simple plain text message.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client and async_client are initialized as shown in the setup block.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"

# --- Synchronous Example --- 
def send_sync_text():
    print("\n--- Sending Text Message (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync text: API key is placeholder.")
        return
    try:
        response = sync_client.send_text(
            to=recipient_phone_number,
            text_body="Hello from Wasender Python SDK (Sync Text Helper)!"
        )
        print(f"  Sync text sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending sync text: {e.message}")

# --- Asynchronous Example --- 
async def send_async_text(async_client_instance):
    print("\n--- Sending Text Message (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async text: API key is placeholder.")
        return
    try:
        response = await async_client_instance.send_text(
            to=recipient_phone_number, 
            text_body="Hello from Wasender Python SDK (Async Text Helper)!"
        )
        print(f"  Async text sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending async text: {e.message}")

# --- Running the examples ---
# send_sync_text() 

# async def main_text_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_async_text(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_text_examples())
```

**Using Generic `send()` Method (Advanced)**

```python
# Ensure async_client and send_generic_message_advanced_helper are available from setup.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"

async def send_text_generic_advanced(async_client_instance):
    from wasenderapi.models import TextOnlyMessage # Import specific model
    text_payload = TextOnlyMessage(
        to=recipient_phone_number, # Assuming model takes direct phone for 'to'
        text={"body": "Hello from generic send (Async Text)!"}
    )
    await send_generic_message_advanced_helper(
        "Sending Text via Generic send()", 
        async_client_instance, 
        text_payload
    )

# async def main_generic_text_example():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_text_generic_advanced(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_generic_text_example())
```

### 2. Image Message

Sends an image from a URL. Optional caption can be included.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client, async_client are initialized. 
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# image_url_example = "https://picsum.photos/seed/wasenderdocs/400/300" # Replace with your image URL

# --- Synchronous Example --- 
def send_sync_image():
    print("\n--- Sending Image Message (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync image: API key is placeholder.")
        return
    try:
        response = sync_client.send_image(
            to=recipient_phone_number,
            url=image_url_example, 
            caption="Awesome Pic! (Sync Helper)"
        )
        print(f"  Sync image sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending sync image: {e.message}")

# --- Asynchronous Example --- 
async def send_async_image(async_client_instance):
    print("\n--- Sending Image Message (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async image: API key is placeholder.")
        return
    try:
        response = await async_client_instance.send_image(
            to=recipient_phone_number, 
            url=image_url_example,
            caption="Awesome Pic! (Async Helper)"
        )
        print(f"  Async image sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending async image: {e.message}")

# --- Running the examples ---
# send_sync_image()

# async def main_image_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         # For client with retries, initialize it: 
#         # async_client_instance_retries = create_async_wasender(api_key=api_key, retry_options=retry_config)
#         # async with async_client_instance_retries:
#         #    await send_async_image(async_client_instance_retries)
#         await send_async_image(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_image_examples())
```

**Using Generic `send()` Method (Advanced)**

This example also shows using a client instance configured with retry logic.

```python
# Ensure async_client_with_retries (or a similarly named async client) and 
# send_generic_message_advanced_helper are available from setup.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# image_url_example = "https://picsum.photos/seed/wasenderdocs_generic/400/300"

async def send_image_generic_advanced(async_client_instance_retries):
    from wasenderapi.models import ImageMessage # Import specific model
    image_payload = ImageMessage(
        to=recipient_phone_number,
        image={"url": image_url_example, "caption": "Generic Image (Async Advanced)"}
    )
    await send_generic_message_advanced_helper(
        "Sending Image via Generic send() with Retries", 
        async_client_instance_retries, 
        image_payload
    )

# async def main_generic_image_example():
#     # Example with a client that has retries configured in setup
#     async_client_retries = create_async_wasender(api_key=api_key, retry_options=retry_config) 
#     async with async_client_retries as client_for_generic_image:
#         await send_image_generic_advanced(client_for_generic_image)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_generic_image_example())
```

### 3. Video Message

Sends a video from a URL. Optional caption can be included.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client, async_client are initialized.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# video_url_example = "YOUR_VIDEO_URL_HERE" # Replace with your .mp4, .3gpp video URL (max 16MB)

# --- Synchronous Example --- 
def send_sync_video():
    print("\n--- Sending Video Message (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync video: API key is placeholder.")
        return
    try:
        response = sync_client.send_video(
            to=recipient_phone_number,
            url=video_url_example, 
            caption="Cool Video! (Sync Helper)"
        )
        print(f"  Sync video sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending sync video: {e.message}")

# --- Asynchronous Example --- 
async def send_async_video(async_client_instance):
    print("\n--- Sending Video Message (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async video: API key is placeholder.")
        return
    try:
        response = await async_client_instance.send_video(
            to=recipient_phone_number, 
            url=video_url_example,
            caption="Cool Video! (Async Helper)"
        )
        print(f"  Async video sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending async video: {e.message}")

# --- Running the examples ---
# send_sync_video()

# async def main_video_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_async_video(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and video_url_example != "YOUR_VIDEO_URL_HERE":
#    asyncio.run(main_video_examples())
```

**Using Generic `send()` Method (Advanced)**

```python
# Ensure async_client and send_generic_message_advanced_helper are available.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# video_url_example = "YOUR_VIDEO_URL_HERE"

async def send_video_generic_advanced(async_client_instance):
    from wasenderapi.models import VideoMessage # Import specific model
    video_payload = VideoMessage(
        to=recipient_phone_number,
        video={"url": video_url_example, "caption": "Generic Video (Async Advanced)"}
    )
    await send_generic_message_advanced_helper(
        "Sending Video via Generic send()", 
        async_client_instance, 
        video_payload
    )

# async def main_generic_video_example():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_video_generic_advanced(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and video_url_example != "YOUR_VIDEO_URL_HERE":
#    asyncio.run(main_generic_video_example())
```

### 4. Document Message

Sends a document from a URL. Optional caption and filename can be provided.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client, async_client are initialized.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# document_url_example = "YOUR_DOCUMENT_URL_HERE" # Replace with your .pdf, .docx, etc. URL
# document_filename_example = "MyReport.pdf"

# --- Synchronous Example --- 
def send_sync_document():
    print("\n--- Sending Document Message (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync document: API key is placeholder.")
        return
    try:
        response = sync_client.send_document(
            to=recipient_phone_number,
            url=document_url_example,
            filename=document_filename_example,
            caption="Check this doc (Sync Helper)"
        )
        print(f"  Sync document sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending sync document: {e.message}")

# --- Asynchronous Example --- 
async def send_async_document(async_client_instance):
    print("\n--- Sending Document Message (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async document: API key is placeholder.")
        return
    try:
        response = await async_client_instance.send_document(
            to=recipient_phone_number, 
            url=document_url_example,
            filename=document_filename_example,
            caption="Check this doc (Async Helper)"
        )
        print(f"  Async document sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending async document: {e.message}")

# --- Running the examples ---
# send_sync_document()

# async def main_document_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_async_document(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and document_url_example != "YOUR_DOCUMENT_URL_HERE":
#    asyncio.run(main_document_examples())
```

**Using Generic `send()` Method (Advanced)**

```python
# Ensure async_client and send_generic_message_advanced_helper are available.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# document_url_example = "YOUR_DOCUMENT_URL_HERE"
# document_filename_example = "MyReportGeneric.pdf"

async def send_document_generic_advanced(async_client_instance):
    from wasenderapi.models import DocumentMessage # Import specific model
    document_payload = DocumentMessage(
        to=recipient_phone_number,
        document={
            "url": document_url_example, 
            "filename": document_filename_example,
            "caption": "Generic Document (Async Advanced)"
        }
    )
    await send_generic_message_advanced_helper(
        "Sending Document via Generic send()", 
        async_client_instance, 
        document_payload
    )

# async def main_generic_document_example():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_document_generic_advanced(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and document_url_example != "YOUR_DOCUMENT_URL_HERE":
#    asyncio.run(main_generic_document_example())
```

### 5. Audio Message

Sends an audio file from a URL. Can be rendered as a voice note (PTT - Push To Talk) or regular audio.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client, async_client are initialized.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# audio_url_example = "YOUR_AUDIO_URL_HERE" # Replace with your .mp3, .ogg, etc. URL

# --- Synchronous Example --- 
def send_sync_audio():
    print("\n--- Sending Audio Message (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync audio: API key is placeholder.")
        return
    try:
        # Send as regular audio
        response_regular = sync_client.send_audio(
            to=recipient_phone_number,
            url=audio_url_example,
            ptt=False 
        )
        print(f"  Sync regular audio sent: ID {response_regular.response.data.message_id}, Status: {response_regular.response.message}")
        if response_regular.rate_limit: print(f"  Rate limit: {response_regular.rate_limit.remaining}")

        # Send as voice note (PTT)
        response_ptt = sync_client.send_audio(
            to=recipient_phone_number,
            url=audio_url_example, # Typically same URL, or could be a different one if needed
            ptt=True
        )
        print(f"  Sync PTT audio sent: ID {response_ptt.response.data.message_id}, Status: {response_ptt.response.message}")
        if response_ptt.rate_limit: print(f"  Rate limit: {response_ptt.rate_limit.remaining}")

    except WasenderAPIError as e:
        print(f"  Error sending sync audio: {e.message}")

# --- Asynchronous Example --- 
async def send_async_audio(async_client_instance):
    print("\n--- Sending Audio Message (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async audio: API key is placeholder.")
        return
    try:
        # Send as regular audio
        response_regular = await async_client_instance.send_audio(
            to=recipient_phone_number, 
            url=audio_url_example,
            ptt=False
        )
        print(f"  Async regular audio sent: ID {response_regular.response.data.message_id}, Status: {response_regular.response.message}")
        if response_regular.rate_limit: print(f"  Rate limit: {response_regular.rate_limit.remaining}")

        # Send as voice note (PTT)
        response_ptt = await async_client_instance.send_audio(
            to=recipient_phone_number, 
            url=audio_url_example, # Typically same URL
            ptt=True
        )
        print(f"  Async PTT audio sent: ID {response_ptt.response.data.message_id}, Status: {response_ptt.response.message}")
        if response_ptt.rate_limit: print(f"  Rate limit: {response_ptt.rate_limit.remaining}")

    except WasenderAPIError as e:
        print(f"  Error sending async audio: {e.message}")

# --- Running the examples ---
# send_sync_audio()

# async def main_audio_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_async_audio(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and audio_url_example != "YOUR_AUDIO_URL_HERE":
#    asyncio.run(main_audio_examples())
```

**Using Generic `send()` Method (Advanced)**

```python
# Ensure async_client and send_generic_message_advanced_helper are available.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# audio_url_example = "YOUR_AUDIO_URL_HERE"

async def send_audio_generic_advanced(async_client_instance):
    from wasenderapi.models import AudioMessage # Import specific model
    audio_payload = AudioMessage(
        to=recipient_phone_number,
        audio={"url": audio_url_example} # Example: send as voice note
    )
    await send_generic_message_advanced_helper(
        "Sending Audio via Generic send() (as PTT)", 
        async_client_instance, 
        audio_payload
    )

# async def main_generic_audio_example():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_audio_generic_advanced(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and audio_url_example != "YOUR_AUDIO_URL_HERE":
#    asyncio.run(main_generic_audio_example())
```

### 6. Sticker Message

Sends a sticker from a URL. Stickers must be in `.webp` format.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client, async_client are initialized.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# sticker_url_example = "YOUR_STICKER_URL_HERE" # Replace with your .webp sticker URL

# --- Synchronous Example --- 
def send_sync_sticker():
    print("\n--- Sending Sticker Message (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync sticker: API key is placeholder.")
        return
    try:
        response = sync_client.send_sticker(
            to=recipient_phone_number,
            url=sticker_url_example
        )
        print(f"  Sync sticker sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending sync sticker: {e.message}")

# --- Asynchronous Example --- 
async def send_async_sticker(async_client_instance):
    print("\n--- Sending Sticker Message (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async sticker: API key is placeholder.")
        return
    try:
        response = await async_client_instance.send_sticker(
            to=recipient_phone_number, 
            url=sticker_url_example
        )
        print(f"  Async sticker sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending async sticker: {e.message}")

# --- Running the examples ---
# send_sync_sticker()

# async def main_sticker_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_async_sticker(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and sticker_url_example != "YOUR_STICKER_URL_HERE":
#    asyncio.run(main_sticker_examples())
```

**Using Generic `send()` Method (Advanced)**

```python
# Ensure async_client and send_generic_message_advanced_helper are available.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# sticker_url_example = "YOUR_STICKER_URL_HERE"

async def send_sticker_generic_advanced(async_client_instance):
    from wasenderapi.models import StickerMessage # Import specific model
    sticker_payload = StickerMessage(
        to=recipient_phone_number,
        sticker={"url": sticker_url_example}
    )
    await send_generic_message_advanced_helper(
        "Sending Sticker via Generic send()", 
        async_client_instance, 
        sticker_payload
    )

# async def main_generic_sticker_example():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_sticker_generic_advanced(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER" and sticker_url_example != "YOUR_STICKER_URL_HERE":
#    asyncio.run(main_generic_sticker_example())
```

### 7. Contact Card Message

Sends a contact card.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client, async_client are initialized.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# contact_to_send_name = "John Doe"
# contact_to_send_phone = "+19876543210"

# --- Synchronous Example --- 
def send_sync_contact():
    print("\n--- Sending Contact Card (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync contact: API key is placeholder.")
        return
    try:
        response = sync_client.send_contact(
            to=recipient_phone_number,
            contact_name=contact_to_send_name,
            contact_phone_number=contact_to_send_phone
        )
        print(f"  Sync contact card sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending sync contact: {e.message}")

# --- Asynchronous Example --- 
async def send_async_contact(async_client_instance):
    print("\n--- Sending Contact Card (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async contact: API key is placeholder.")
        return
    try:
        response = await async_client_instance.send_contact(
            to=recipient_phone_number, 
            contact_name=contact_to_send_name,
            contact_phone_number=contact_to_send_phone
        )
        print(f"  Async contact card sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending async contact: {e.message}")

# --- Running the examples ---
# send_sync_contact()

# async def main_contact_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         # Can also use client_with_retries here if needed by initializing it and passing it
#         await send_async_contact(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_contact_examples())
```

**Using Generic `send()` Method (Advanced)**

This example also shows using a client configured with retry logic.

```python
# Ensure async_client_with_retries and send_generic_message_advanced_helper are available.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# contact_to_send_name = "Jane Doe (Generic)"
# contact_to_send_phone = "+12223334444"

async def send_contact_generic_advanced(async_client_instance_retries):
    from wasenderapi.models import ContactMessage # Import specific model
    contact_payload = ContactMessage(
        to=recipient_phone_number,
        contact={"name": contact_to_send_name, "phoneNumber": contact_to_send_phone} 
        # caption="Optional: Here is Jane Doe's contact. (Generic Send)" # If model supports caption here
    )
    await send_generic_message_advanced_helper(
        "Sending Contact Card via Generic send() with Retries", 
        async_client_instance_retries, 
        contact_payload
    )

# async def main_generic_contact_example():
#     async_client_retries = create_async_wasender(api_key=api_key, retry_options=retry_config)
#     async with async_client_retries as client_for_generic_contact:
#         await send_contact_generic_advanced(client_for_generic_contact)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_generic_contact_example())
```

### 8. Location Pin Message

Sends a location pin with latitude and longitude. Optional name and address for the location can be included.

**Using Helper Methods (Recommended)**

```python
# Ensure sync_client, async_client are initialized.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# latitude_example = 37.7749  # Example: San Francisco
# longitude_example = -122.4194 # Example: San Francisco
# location_name_example = "OpenAI HQ"
# location_address_example = "Pioneer Building, San Francisco, CA"

# --- Synchronous Example --- 
def send_sync_location():
    print("\n--- Sending Location Pin (Sync Helper) ---")
    if sync_client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping sync location: API key is placeholder.")
        return
    try:
        response = sync_client.send_location(
            to=recipient_phone_number,
            latitude=latitude_example,
            longitude=longitude_example,
            name=location_name_example,
            address=location_address_example
        )
        print(f"  Sync location sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending sync location: {e.message}")

# --- Asynchronous Example --- 
async def send_async_location(async_client_instance):
    print("\n--- Sending Location Pin (Async Helper) ---")
    if async_client_instance.api_key == "YOUR_API_KEY_PLACEHOLDER":
        print("Skipping async location: API key is placeholder.")
        return
    try:
        response = await async_client_instance.send_location(
            to=recipient_phone_number, 
            latitude=latitude_example,
            longitude=longitude_example,
            name=location_name_example,
            address=location_address_example
        )
        print(f"  Async location sent: ID {response.response.data.message_id}, Status: {response.response.message}")
        if response.rate_limit: print(f"  Rate limit: {response.rate_limit.remaining}")
    except WasenderAPIError as e:
        print(f"  Error sending async location: {e.message}")

# --- Running the examples ---
# send_sync_location()

# async def main_location_examples():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_async_location(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_location_examples())
```

**Using Generic `send()` Method (Advanced)**

```python
# Ensure async_client and send_generic_message_advanced_helper are available.
# recipient_phone_number = "YOUR_PHONE_NUMBER_HERE"
# latitude_example = 37.7749
# longitude_example = -122.4194

async def send_location_generic_advanced(async_client_instance):
    from wasenderapi.models import LocationMessage # Import specific model
    location_payload = LocationMessage(
        to=recipient_phone_number,
        location={
            "latitude": latitude_example,
            "longitude": longitude_example,
            "name": "Exploratorium (Generic)",
            "address": "Pier 15, San Francisco, CA"
        }
        # caption="Optional: Meet me here. (Generic Send)" # If model supports caption here
    )
    await send_generic_message_advanced_helper(
        "Sending Location Pin via Generic send()", 
        async_client_instance, 
        location_payload
    )

# async def main_generic_location_example():
#     async with create_async_wasender(api_key=api_key) as async_client_instance:
#         await send_location_generic_advanced(async_client_instance)
# if __name__ == "__main__" and api_key != "YOUR_API_KEY_PLACEHOLDER":
#    asyncio.run(main_generic_location_example())
```

## Using Specific Helper Methods (Recap)

The Wasender Python SDK provides specific helper methods for most common message types, offering a more straightforward way to send messages compared to manually constructing payload objects. These methods are available on both `WasenderSyncClient` and `WasenderAsyncClient` instances.

When using these helpers, you pass parameters directly, such as `to`, `text_body`, `url`, `caption`, etc., depending on the message type.

Below is a summary of the new helper method signatures. (Note: `**kwargs` allows for any other standard message parameters like `quoted_message_id`, `mentions`, etc., to be passed through if supported by the API for that message type).

**Synchronous Client (`WasenderSyncClient`):**

- `send_text(self, to: str, text_body: str, **kwargs: Any) -> WasenderSendResult`
- `send_image(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`
- `send_video(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`
- `send_document(self, to: str, url: str, filename: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`
- `send_audio(self, to: str, url: str, ptt: Optional[bool] = False, **kwargs: Any) -> WasenderSendResult`
- `send_sticker(self, to: str, url: str, **kwargs: Any) -> WasenderSendResult`
- `send_contact(self, to: str, contact_name: str, contact_phone_number: str, **kwargs: Any) -> WasenderSendResult`
- `send_location(self, to: str, latitude: float, longitude: float, name: Optional[str] = None, address: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`

**Asynchronous Client (`WasenderAsyncClient`):**

(These have the same parameters but are `async` methods and return `Awaitable[WasenderSendResult]`)

- `async send_text(self, to: str, text_body: str, **kwargs: Any) -> WasenderSendResult`
- `async send_image(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`
- `async send_video(self, to: str, url: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`
- `async send_document(self, to: str, url: str, filename: str, caption: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`
- `async send_audio(self, to: str, url: str, ptt: Optional[bool] = False, **kwargs: Any) -> WasenderSendResult`
- `async send_sticker(self, to: str, url: str, **kwargs: Any) -> WasenderSendResult`
- `async send_contact(self, to: str, contact_name: str, contact_phone_number: str, **kwargs: Any) -> WasenderSendResult`
- `async send_location(self, to: str, latitude: float, longitude: float, name: Optional[str] = None, address: Optional[str] = None, **kwargs: Any) -> WasenderSendResult`

Always refer to the client method definitions in `sync_client.py` and `async_client.py` for the most precise signatures and available `**kwargs` options.

## Error Handling and Rate Limiting

API interactions can result in errors, or you might hit rate limits. The Python SDK handles this by raising a `WasenderAPIError` (from `wasenderapi.errors`) for API-specific issues.

Key attributes of `