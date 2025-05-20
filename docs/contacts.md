# Wasender Python SDK: Contact Management Examples

This document provides examples for managing contacts using the Wasender Python SDK, including retrieving contacts, getting specific contact details, fetching profile pictures, and blocking/unblocking contacts.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Prerequisites

1.  **Install Python:** Ensure Python (3.8+) is installed on your system.
2.  **Obtain a Wasender API Key:** You'll need an API key from [https://www.wasenderapi.com](https://www.wasenderapi.com).
3.  **SDK Installation:** Install the Wasender Python SDK using pip:
    ```bash
    pip install wasenderapi
    ```

## Initializing the SDK

All examples assume you have initialized the SDK. The examples in this document primarily use an asynchronous client.

```python
# contact_examples_setup.py
import asyncio
import os
import logging
import json
from datetime import datetime
from typing import Optional, List

# Corrected imports for client and RetryConfig
from wasenderapi import create_async_wasender, WasenderAsyncClient # For type hinting
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    RetryConfig, # RetryConfig is now from models
    Contact,     # Core Contact model
    RateLimitInfo
)
# Import specific *Result models from wasenderapi.contacts
from wasenderapi.contacts import (
    GetAllContactsResult,
    GetContactInfoResult,
    GetContactProfilePictureResult,
    ContactActionResult
)

# Configure basic logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SDK Initialization ---
api_key = os.getenv("WASENDER_API_KEY")
personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN")

if not api_key:
    logger.error("Error: WASENDER_API_KEY environment variable is not set.")
    api_key = "YOUR_API_KEY_PLACEHOLDER" # Use a placeholder for docs

# Initialize async client using the factory function
# Contact operations are typically on a specific session (identified by api_key).
async_client = create_async_wasender(api_key=api_key, personal_access_token=personal_access_token)

logger.info(f"WasenderAsyncClient initialized for Contact Management examples (API Key: {api_key[:4]}...)")

# Example of initializing with retry options (if desired)
# retry_config_contacts = RetryConfig(enabled=True, max_retries=2)
# async_client_with_retries_contacts = create_async_wasender(
#     api_key=api_key,
#     personal_access_token=personal_access_token,
#     retry_options=retry_config_contacts
# )

# Placeholder for a contact's phone number - replace with a valid E.164 number or JID
TARGET_CONTACT_PHONE = "12345678901" # Example phone number
# TARGET_CONTACT_JID = "12345678901@s.whatsapp.net" # Example JID

# --- Generic Error Handler ---
def handle_api_error(error: Exception, operation: str):
    if isinstance(error, WasenderAPIError):
        logger.error(f"API Error during {operation}:")
        logger.error(f"  Message: {error.message}")
        logger.error(f"  Status Code: {error.status_code or 'N/A'}")
        if error.api_message:
            logger.error(f"  API Message: {error.api_message}")
        if error.error_details:
            logger.error(f"  Error Details: {error.error_details}")
        if error.rate_limit:
            reset_time_str = datetime.fromtimestamp(error.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if error.rate_limit.reset_timestamp else "N/A"
            logger.error(
                f"  Rate Limit at Error: Remaining = {error.rate_limit.remaining}, Limit = {error.rate_limit.limit}, Resets at = {reset_time_str}"
            )
    else:
        logger.error(f"An unexpected error occurred during {operation}: {error}")

async def main():
    # This is where you'll call your example functions
    logger.info("Starting Contact Management examples...")

    # await get_all_contacts_example()
    # await get_specific_contact_info_example(TARGET_CONTACT_PHONE)
    # await get_contact_profile_picture_example(TARGET_CONTACT_PHONE)
    # await block_contact_example(TARGET_CONTACT_PHONE) # CAUTION: Blocks the contact
    # await unblock_contact_example(TARGET_CONTACT_PHONE)

    logger.info("Contact Management examples finished.")

if __name__ == "__main__":
    # Note: For simplicity, examples might be run directly by uncommenting in main().
    # In a real application, you'd integrate these into your async workflow.
    asyncio.run(main())

## Contact Management Operations

Below are examples of common contact management tasks. These functions assume `async_client`, `logger`, `handle_api_error`, `TARGET_CONTACT_PHONE`, and relevant Pydantic models are available from a setup similar to the one shown above.

### 1. Get All Contacts

Retrieves a list of all contacts synced with the WhatsApp session.

```python
# Example: Get All Contacts
async def get_all_contacts_example(client: WasenderAsyncClient):
    logger.info("\n--- Fetching All Contacts ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning("Skipping API call for get_all_contacts: API key is a placeholder.")
        return
    try:
        result: GetAllContactsResult = await client.get_contacts()
        contacts: List[Contact] = result.response.data
        
        logger.info(f"Successfully retrieved {len(contacts)} contacts.")
        if contacts:
            # Log the first contact as an example (using model_dump for console, model_dump_json for string)
            logger.info(f"First contact (details): {contacts[0].model_dump()}")
            # To get JSON string: json_str = contacts[0].model_dump_json(indent=2)
            # logger.info(f"First contact (JSON): {json_str}")

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")
            
    except Exception as e:
        handle_api_error(e, "fetching all contacts")

# To run this example (assuming client, logger etc. are initialized):
# asyncio.run(get_all_contacts_example())
# Or call it from the main() function in the setup.
```

### 2. Get Specific Contact Information

Retrieves detailed information for a specific contact using their JID (Phone Number).

```python
# Example: Get Specific Contact Information
async def get_specific_contact_info_example(client: WasenderAsyncClient, contact_phone: str):
    logger.info(f"\n--- Fetching Info for Contact: {contact_phone} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for get_contact_info {contact_phone}: API key is a placeholder.")
        return
    if not contact_phone:
        logger.error("Error: No target contact phone number provided for fetching info.")
        return
    try:
        result: GetContactInfoResult = await client.get_contact_info(contact_phone_number=contact_phone)
        contact_info: Contact = result.response.data # The data field in GetContactInfoResult is a Contact model
        
        logger.info(f"Contact info retrieved for {contact_phone}:")
        logger.info(contact_info.model_dump_json(indent=2)) # Pretty print JSON

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")
            
    except Exception as e:
        handle_api_error(e, f"fetching info for contact {contact_phone}")

# To run this example:
# asyncio.run(get_specific_contact_info_example(TARGET_CONTACT_PHONE))
```

### 3. Get Contact Profile Picture URL

Retrieves the URL of the profile picture for a specific contact.

```python
# Example: Get Contact Profile Picture URL
async def get_contact_profile_picture_example(client: WasenderAsyncClient, contact_phone: str):
    logger.info(f"\n--- Fetching Profile Picture URL for Contact: {contact_phone} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for get_contact_profile_picture {contact_phone}: API key is a placeholder.")
        return
    if not contact_phone:
        logger.error("Error: No target contact phone number provided for fetching profile picture.")
        return
    try:
        result: GetContactProfilePictureResult = await client.get_contact_profile_picture(contact_phone_number=contact_phone)
        # The data field in GetContactProfilePictureResult is ProfilePicData, which has img_url
        pic_data = result.response.data 

        if pic_data and pic_data.img_url:
            logger.info(f"Profile picture URL for {contact_phone}: {pic_data.img_url}")
        else:
            logger.info(f"Contact {contact_phone} does not have a profile picture or it is not accessible.")

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")

    except Exception as e:
        handle_api_error(e, f"fetching profile picture for contact {contact_phone}")

# To run this example:
# asyncio.run(get_contact_profile_picture_example(TARGET_CONTACT_PHONE))
```

### 4. Block a Contact

Blocks a specific contact.

```python
# Example: Block a Contact
async def block_contact_example(client: WasenderAsyncClient, contact_phone: str):
    logger.info(f"\n--- Blocking Contact: {contact_phone} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for block_contact {contact_phone}: API key is a placeholder.")
        return
    if not contact_phone:
        logger.error("Error: No target contact phone number provided for blocking.")
        return
    try:
        result: ContactActionResult = await client.block_contact(contact_phone_number=contact_phone)
        # The data field in ContactActionResult is ContactActionData, which has a message
        action_data = result.response.data
        
        logger.info(f"Block operation for {contact_phone} successful: {action_data.message if action_data else 'No specific message'}")

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")
            
    except Exception as e:
        handle_api_error(e, f"blocking contact {contact_phone}")

# To run this example (CAUTION: this will block the contact!):
# asyncio.run(block_contact_example(TARGET_CONTACT_PHONE))
```

### 5. Unblock a Contact

Unblocks a specific contact.

```python
# Example: Unblock a Contact
async def unblock_contact_example(client: WasenderAsyncClient, contact_phone: str):
    logger.info(f"\n--- Unblocking Contact: {contact_phone} ---")
    if client.api_key == "YOUR_API_KEY_PLACEHOLDER":
        logger.warning(f"Skipping API call for unblock_contact {contact_phone}: API key is a placeholder.")
        return
    if not contact_phone:
        logger.error("Error: No target contact phone number provided for unblocking.")
        return
    try:
        result: ContactActionResult = await client.unblock_contact(contact_phone_number=contact_phone)
        action_data = result.response.data
        
        logger.info(f"Unblock operation for {contact_phone} successful: {action_data.message if action_data else 'No specific message'}")

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")
            
    except Exception as e:
        handle_api_error(e, f"unblocking contact {contact_phone}")

# To run this example:
# asyncio.run(unblock_contact_example(TARGET_CONTACT_PHONE))
```

## Important Notes on Contact JIDs

- The API documentation often refers to `contactPhoneNumber` as the JID (Jabber ID) in E.164 format. However, for some WhatsApp internal JIDs (like groups or channels), the format might differ (e.g., `number@g.us` or `number@newsletter`).
- For individual contacts, ensure you are using the phone number part of their JID, typically without the `+` sign or `@s.whatsapp.net` suffix, as per the API\'s expectation for `contactPhoneNumber` path parameters (e.g., `12345678901`). Always refer to the specific API documentation for the exact format required by each endpoint if issues arise.

This guide provides a solid foundation for using the contact management features of the Wasender Python SDK. Remember to replace placeholder JIDs, handle API keys securely, and consult the SDK's specific model definitions for exact response structures.
