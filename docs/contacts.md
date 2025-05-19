# Wasender Python SDK: Contact Management Examples

This document provides examples for managing contacts using the Wasender Python SDK, including retrieving contacts, getting specific contact details, fetching profile pictures, and blocking/unblocking contacts.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Prerequisites

1.  **Install Python:** Ensure Python (3.7+) is installed on your system.
2.  **Obtain a Wasender API Key:** You'll need an API key from [https://www.wasenderapi.com](https://www.wasenderapi.com).
3.  **SDK Installation:** Install the Wasender Python SDK using pip:
    ```bash
    pip install wasenderapi
    ```

## Initializing the SDK

All examples assume you have initialized the `WasenderClient` as follows. You can place this in a central part of your application or at the beginning of your script.

```python
# contact_examples_setup.py
import asyncio
import os
import logging
import json
from datetime import datetime
from typing import Optional, List

from wasenderapi import WasenderClient, RetryConfig
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    Contact,
    ContactInfo,
    ContactProfilePicture,
    ContactActionResult,
    RateLimitInfo,
    # Import other necessary models as you define more examples
    # Assuming GetAllContactsResponse, GetContactInfoResponse, etc. are defined
    # and client methods return instances of WasenderResponse[SpecificResultDataModel]
)

# Configure basic logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SDK Initialization ---
api_key = os.getenv("WASENDER_API_KEY") # API Key for the session whose contacts are being managed.
# The personal_access_token is primarily for account-level session management (create/list/delete sessions).
# It's not typically required for contact operations within an existing session if the api_key is for that session.
personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN") # Optional, uncomment if needed for specific auth models or session selection.

if not api_key:
    logger.error("Error: WASENDER_API_KEY environment variable is not set.")
    exit(1)

# Initialize the client (choose one method)
# 1. With API Key only (most common for operating on an existing session's contacts)
client = WasenderClient(api_key=api_key)

# 2. With API Key (main account) and Personal Access Token 
# (less common for contact operations, more for session management or if PAT is the primary auth for the session itself)
# # client = WasenderClient(api_key=api_key, personal_access_token=personal_access_token)

# 3. With custom retry configuration
# retry_config = RetryConfig(total_retries=5, backoff_factor=0.5)
# client = WasenderClient(api_key=api_key, retry_config=retry_config)

logger.info("WasenderClient initialized for Contact Management examples.")

# Placeholder for a contact's phone number - replace with a valid E.164 number
# (international format without '+', e.g., "12345678901")
TARGET_CONTACT_JID = "12345678901" # Replace with a real number for testing

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
    # await get_specific_contact_info_example(TARGET_CONTACT_JID)
    # await get_contact_profile_picture_example(TARGET_CONTACT_JID)
    # await block_contact_example(TARGET_CONTACT_JID) # CAUTION: Blocks the contact
    # await unblock_contact_example(TARGET_CONTACT_JID)

    logger.info("Contact Management examples finished.")

if __name__ == "__main__":
    # Note: For simplicity, examples might be run directly by uncommenting in main().
    # In a real application, you'd integrate these into your async workflow.
    asyncio.run(main())

## Contact Management Operations

Below are examples of common contact management tasks. These functions assume `client`, `logger`, `handle_api_error`, `TARGET_CONTACT_JID`, relevant Pydantic models, `json`, and `datetime` are available from a setup similar to the one shown above.

### 1. Get All Contacts

Retrieves a list of all contacts synced with the WhatsApp session.

```python
# Example: Get All Contacts
async def get_all_contacts_example():
    logger.info("\n--- Fetching All Contacts ---")
    try:
        result = await client.get_contacts() # Assuming this returns WasenderResponse[List[Contact]]
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
async def get_specific_contact_info_example(contact_jid: str):
    logger.info(f"\n--- Fetching Info for Contact: {contact_jid} ---")
    if not contact_jid:
        logger.error("Error: No target contact JID provided for fetching info.")
        return
    try:
        result = await client.get_contact_info(contact_jid) # Assuming WasenderResponse[ContactInfo]
        contact_info: ContactInfo = result.response.data
        
        logger.info(f"Contact info retrieved for {contact_jid}:")
        logger.info(contact_info.model_dump_json(indent=2)) # Pretty print JSON

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")
            
    except Exception as e:
        handle_api_error(e, f"fetching info for contact {contact_jid}")

# To run this example:
# asyncio.run(get_specific_contact_info_example(TARGET_CONTACT_JID))
```

### 3. Get Contact Profile Picture URL

Retrieves the URL of the profile picture for a specific contact.

```python
# Example: Get Contact Profile Picture URL
async def get_contact_profile_picture_example(contact_jid: str):
    logger.info(f"\n--- Fetching Profile Picture URL for Contact: {contact_jid} ---")
    if not contact_jid:
        logger.error("Error: No target contact JID provided for fetching profile picture.")
        return
    try:
        result = await client.get_contact_profile_picture(contact_jid) # Assuming WasenderResponse[ContactProfilePicture]
        pic_data: ContactProfilePicture = result.response.data

        if pic_data.img_url:
            logger.info(f"Profile picture URL for {contact_jid}: {pic_data.img_url}")
        else:
            logger.info(f"Contact {contact_jid} does not have a profile picture or it is not accessible.")

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")

    except Exception as e:
        handle_api_error(e, f"fetching profile picture for contact {contact_jid}")

# To run this example:
# asyncio.run(get_contact_profile_picture_example(TARGET_CONTACT_JID))
```

### 4. Block a Contact

Blocks a specific contact.

```python
# Example: Block a Contact
async def block_contact_example(contact_jid: str):
    logger.info(f"\n--- Blocking Contact: {contact_jid} ---")
    if not contact_jid:
        logger.error("Error: No target contact JID provided for blocking.")
        return
    try:
        result = await client.block_contact(contact_jid) # Assuming WasenderResponse[ContactActionResult]
        action_result: ContactActionResult = result.response.data
        
        logger.info(f"Block operation for {contact_jid} successful: {action_result.message}")

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")
            
    except Exception as e:
        handle_api_error(e, f"blocking contact {contact_jid}")

# To run this example (CAUTION: this will block the contact!):
# asyncio.run(block_contact_example(TARGET_CONTACT_JID))
```

### 5. Unblock a Contact

Unblocks a specific contact.

```python
# Example: Unblock a Contact
async def unblock_contact_example(contact_jid: str):
    logger.info(f"\n--- Unblocking Contact: {contact_jid} ---")
    if not contact_jid:
        logger.error("Error: No target contact JID provided for unblocking.")
        return
    try:
        result = await client.unblock_contact(contact_jid) # Assuming WasenderResponse[ContactActionResult]
        action_result: ContactActionResult = result.response.data
        
        logger.info(f"Unblock operation for {contact_jid} successful: {action_result.message}")

        if result.rate_limit:
            reset_time_str = datetime.fromtimestamp(result.rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if result.rate_limit.reset_timestamp else "N/A"
            logger.info(
                f"Rate Limit Info: Remaining = {result.rate_limit.remaining}, Limit = {result.rate_limit.limit}, Resets at = {reset_time_str}"
            )
        else:
            logger.info("Rate limit information not available for this request.")
            
    except Exception as e:
        handle_api_error(e, f"unblocking contact {contact_jid}")

# To run this example:
# asyncio.run(unblock_contact_example(TARGET_CONTACT_JID))
```

## Important Notes on Contact JIDs

- The API documentation often refers to `contactPhoneNumber` as the JID (Jabber ID) in E.164 format. However, for some WhatsApp internal JIDs (like groups or channels), the format might differ (e.g., `number@g.us` or `number@newsletter`).
- For individual contacts, ensure you are using the phone number part of their JID, typically without the `+` sign or `@s.whatsapp.net` suffix, as per the API\'s expectation for `contactPhoneNumber` path parameters (e.g., `12345678901`). Always refer to the specific API documentation for the exact format required by each endpoint if issues arise.

This guide provides a solid foundation for using the contact management features of the Wasender Python SDK. Remember to replace placeholder JIDs, handle API keys securely, and consult the SDK's specific model definitions for exact response structures.
