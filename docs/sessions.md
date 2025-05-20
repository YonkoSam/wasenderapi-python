# Wasender Python SDK: Session Management Examples

This document provides comprehensive examples for managing WhatsApp sessions using the Wasender Python SDK. It covers creating, retrieving, updating, deleting sessions, handling connections (QR codes), and checking session status.

## SDK Version: [Specify Python SDK Version Here, e.g., 0.1.0]

## Prerequisites

1.  **Install Python:** Ensure Python (3.8+) is installed on your system.
2.  **Obtain a Wasender API Key & Personal Token:** 
    *   You'll need your main Wasender API key from [https://www.wasenderapi.com](https://www.wasenderapi.com).
    *   For session management, a **Personal Access Token** is typically required.
3.  **SDK Installation:** Install the Wasender Python SDK using pip:
    ```bash
    pip install wasenderapi
    ```

## Initializing the SDK

All examples assume SDK initialization as shown below. Session management operations primarily use the `personal_access_token`.

```python
# session_examples_setup.py
import asyncio
import os
import logging
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

# Corrected imports for client and RetryConfig
from wasenderapi import create_async_wasender, WasenderAsyncClient # For type hinting
from wasenderapi.errors import WasenderAPIError
from wasenderapi.models import (
    RetryConfig, # RetryConfig is now from models
    RateLimitInfo
)
# Import specific *Result and Payload models from wasenderapi.sessions
from wasenderapi.sessions import (
    WhatsAppSession,      # Core WhatsAppSession model
    CreateWhatsAppSessionPayload,
    UpdateWhatsAppSessionPayload,
    WhatsAppSessionStatus,  # Enum for session states
    # Result types for client methods
    GetAllWhatsAppSessionsResult,
    GetWhatsAppSessionDetailsResult,
    CreateWhatsAppSessionResult,
    UpdateWhatsAppSessionResult,
    DeleteWhatsAppSessionResult,
    ConnectSessionResult, # Contains SessionConnectionStatus or QRCodeData
    GetQRCodeResult,      # Contains QRCodeData
    DisconnectSessionResult, # Contains SessionConnectionStatus
    RegenerateApiKeyResult,  # Contains RegenerateApiKeyResponse
    GetSessionStatusResult    # Contains GetSessionStatusResponse (which has status field)
)

# Configure basic logging for examples
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SDK Initialization ---
api_key = os.getenv("WASENDER_API_KEY") # Your main account API Key (may not be used if PAT is primary)
personal_access_token = os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN")

if not personal_access_token: # PAT is crucial for session management
    logger.error("Error: WASENDER_PERSONAL_ACCESS_TOKEN environment variable must be set for session management.")
    # For document generation, use a placeholder, but real operations will fail.
    personal_access_token = "YOUR_PAT_PLACEHOLDER"
if not api_key: # API key might still be needed by the base client or for some operations
    api_key = "YOUR_API_KEY_PLACEHOLDER"

# Initialize async client with Personal Access Token for session operations
async_client = create_async_wasender(api_key=api_key, personal_access_token=personal_access_token)
logger.info(f"WasenderAsyncClient initialized for Session Management examples (PAT: {personal_access_token[:4]}...)")

# Example of initializing with retry options (if desired)
# retry_config_sessions = RetryConfig(enabled=True, max_retries=2)
# async_client_with_retries_sessions = create_async_wasender(
#     api_key=api_key, 
#     personal_access_token=personal_access_token,
#     retry_options=retry_config_sessions
# )

# Placeholder for a session ID created/used during tests
# Session IDs from the API are typically integers.
active_test_session_id: Optional[int] = None 

# --- Generic Error Handler for Session Examples ---
def handle_session_api_error(error: Exception, operation: str):
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

# --- Helper to log rate limits ---
def log_rate_limit_info(rate_limit: Optional[RateLimitInfo]):
    if rate_limit:
        reset_time_str = datetime.fromtimestamp(rate_limit.reset_timestamp).strftime('%Y-%m-%d %H:%M:%S') if rate_limit.reset_timestamp else "N/A"
        logger.info(
            f"Rate Limit Info: Remaining = {rate_limit.remaining}, Limit = {rate_limit.limit}, Resets at = {reset_time_str}"
        )
    else:
        logger.info("Rate limit information not available for this request.")

# --- Example Execution Orchestrator ---
async def run_all_session_examples():
    global active_test_session_id
    logger.info("\n--- Starting All Session Examples Orchestration ---")

    # 1. Get all sessions (and maybe pick one if none is active)
    await get_all_sessions_example()
    if not active_test_session_id:
        sessions_response = await async_client.get_all_whatsapp_sessions() # Assuming client.get_all_whatsapp_sessions() is the Python method
        if sessions_response.response.data:
            active_test_session_id = sessions_response.response.data[0].id
            logger.info(f"Picked an existing session for some read-only tests: {active_test_session_id}")

    # 2. Create a new session
    # This will update active_test_session_id with the newly created one
    await create_session_example()

    if active_test_session_id:
        logger.info(f"\n--- Performing operations on Session ID: {active_test_session_id} ---")
        # 3. Get details of the new/active session
        await get_session_details_example(active_test_session_id)
        
        # 4. Update the session
        await update_session_example(active_test_session_id, f"SDK Updated Name {datetime.now().strftime('%H%M%S')}")
        
        # 5. Get QR Code (Connect Session)
        # This might be called multiple times until connection or timeout
        logger.info("Attempting to get QR code for connection. Please scan if presented.")
        await get_session_qr_code_example(active_test_session_id)
        logger.info("Pausing for 30 seconds to allow QR code scanning...")
        await asyncio.sleep(30) # Simulate time for scanning QR code
        
        # 6. Check session status
        await get_session_connection_status_example(active_test_session_id)
        
        # 7. Disconnect session (if connected)
        # Check status first, only disconnect if actually connected to avoid errors
        status_res = await async_client.get_whatsapp_session_details(session_id=active_test_session_id)
        if status_res.response.data.status == WhatsAppSessionStatus.CONNECTED:
            await disconnect_session_example(active_test_session_id)
        else:
            logger.info(f"Session {active_test_session_id} is not connected, skipping disconnect example.")

        # 8. Regenerate API Key (use with extreme caution)
        # logger.info("Skipping Regenerate API Key example due to its disruptive nature.")
        # await regenerate_session_api_key_example(active_test_session_id)

        # 9. Delete session (use with caution)
        logger.info("Finally, deleting the test session.")
        await delete_session_example(active_test_session_id)
        active_test_session_id = None # Clear it after deletion
    else:
        logger.warning("No active session ID available to run detailed examples.")

    logger.info("\n--- All Session Examples Orchestration Completed ---")

if __name__ == "__main__":
    # Ensure environment variables are set before running.
    if not (os.getenv("WASENDER_API_KEY") and os.getenv("WASENDER_PERSONAL_ACCESS_TOKEN")):
        logger.error("WASENDER_API_KEY and WASENDER_PERSONAL_ACCESS_TOKEN must be set in environment variables.")
    else:
        # logger.info("Starting session management examples. Orchestrator will run.")
        # asyncio.run(run_all_session_examples())
        logger.info("To run the session examples orchestrator, uncomment 'asyncio.run(run_all_session_examples())' in __main__.")
        logger.info("Ensure a dedicated test persona and understand that sessions will be created and deleted.")

## Session Management Operations

Below are examples of common session management tasks. These assume `async_client`, `logger`, relevant Pydantic models, etc., are available from a setup similar to the one shown above.

### 1. Get All WhatsApp Sessions

Retrieves a list of all WhatsApp sessions linked to your Personal Access Token.

```python
# Example: Get All WhatsApp Sessions
async def get_all_sessions_example():
    global active_test_session_id
    logger.info("\n--- Fetching All WhatsApp Sessions ---")
    if async_client.personal_access_token == "YOUR_PAT_PLACEHOLDER":
        logger.warning("Skipping get_all_sessions: PAT is a placeholder.")
        return
    try:
        result: GetAllWhatsAppSessionsResult = await async_client.get_all_whatsapp_sessions()
        sessions: List[WhatsAppSession] = result.response.data
        
        logger.info(f"Successfully retrieved {len(sessions)} sessions.")
        if sessions:
            logger.info("First session (details):")
            logger.info(sessions[0].model_dump_json(indent=2))
            # If no specific session is being tested, pick the first one for some read-only ops
            if not active_test_session_id and sessions[0].id:
                # active_test_session_id = sessions[0].id # Orchestrator handles this better
                pass
        else:
            logger.info("No sessions found for this persona token.")
        
        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, "fetching all sessions")

# In main orchestrator: await get_all_sessions_example()
```

### 2. Create WhatsApp Session

Creates a new WhatsApp session associated with your Personal Access Token.

```python
# Example: Create WhatsApp Session
async def create_session_example():
    global active_test_session_id # To store the ID of the created session
    logger.info("\n--- Creating New WhatsApp Session ---")
    
    unique_name = f"SDK Test Session {datetime.now().strftime('%Y%m%d-%H%M%S')}"
    # IMPORTANT: phone_number is often NOT required if the session is just a placeholder
    # for a multi-device WhatsApp Web instance. If it's for a dedicated number, provide it.
    # Check your specific API provider's requirements for session creation.
    payload = CreateWhatsAppSessionPayload(
        name=unique_name,
        # phone_number="+12345000001", # Optional, consult provider docs. Example placeholder.
        description="Test session created by Python SDK example", # Optional
        # webhook_url="https://my.webhook.receiver/unique-path", # Optional
        # webhook_events=["message.created", "session.status"], # Optional, event names vary
    )
    
    logger.info(f"Creating session with payload: {payload.model_dump_json(indent=2)}")
    try:
        result: CreateWhatsAppSessionResult = await async_client.create_whatsapp_session(payload=payload)
        created_session: WhatsAppSession = result.response.data
        
        logger.info("Session created successfully:")
        logger.info(created_session.model_dump_json(indent=2))
        
        active_test_session_id = created_session.id # Store for subsequent examples
        logger.info(f"Stored new session ID for tests: {active_test_session_id}")
        
        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, f"creating new session ('{unique_name}')")

# In main orchestrator: await create_session_example()
```

### 3. Get WhatsApp Session Details

Retrieves details for a specific session by its ID.

```python
# Example: Get WhatsApp Session Details
async def get_session_details_example(session_id: int):
    logger.info(f"\n--- Fetching Details for Session ID: {session_id} ---")
    if not session_id:
        logger.error("Session ID is required.")
        return
    try:
        result: GetWhatsAppSessionDetailsResult = await async_client.get_whatsapp_session_details(session_id=session_id)
        session_details: WhatsAppSession = result.response.data
        
        logger.info(f"Session details for {session_id}:")
        logger.info(session_details.model_dump_json(indent=2))
        
        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, f"fetching details for session {session_id}")

# In main orchestrator: await get_session_details_example(active_test_session_id)
```

### 4. Update WhatsApp Session

Updates details (like name, webhook configuration) for an existing session.

```python
# Example: Update WhatsApp Session
async def update_session_example(session_id: int, new_name: str):
    logger.info(f"\n--- Updating Session ID: {session_id} ---")
    if not session_id:
        logger.error("Session ID is required.")
        return

    payload = UpdateWhatsAppSessionPayload(
        name=new_name,
        description=f"Updated by SDK example at {datetime.now()}", # Optional
        # webhook_url="https://my.updated.webhook.receiver/another-path", # Optional
        # webhook_events=["message.updated", "session.status", "group.participants.changed"], # Optional
    )
    logger.info(f"Updating session with payload: {payload.model_dump_json(exclude_none=True, indent=2)}")
    try:
        result: UpdateWhatsAppSessionResult = await async_client.update_whatsapp_session(session_id=session_id, payload=payload)
        updated_session: WhatsAppSession = result.response.data
        
        logger.info(f"Session {session_id} updated successfully:")
        logger.info(updated_session.model_dump_json(indent=2))
        
        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, f"updating session {session_id}")

# In main orchestrator: await update_session_example(active_test_session_id, f"SDK Updated Name {datetime.now().strftime('%H%M%S')}")
```

### 5. Get Session QR Code (Connect Session)

Initiates the connection process for a session or retrieves an existing QR code if the session is in a `NEED_SCAN` state.

```python
# Example: Get Session QR Code
async def get_session_qr_code_example(session_id: int):
    logger.info(f"\n--- Getting QR Code for Session ID: {session_id} ---")
    if not session_id:
        logger.error("Session ID is required.")
        return

    try:
        # Example: Request QR as a string (default)
        result: GetQRCodeResult = await async_client.get_whatsapp_session_qr_code(session_id=session_id)
        qr_code_data = result.response.data # This is QRCodeData model
        
        if qr_code_data and qr_code_data.qr_code:
            logger.info(f"QR Code string received for session {session_id} (first 50 chars): {qr_code_data.qr_code[:50]}...")
        else:
            logger.warning(f"No QR code data received for session {session_id}.")
        
        # Example: Request QR as an image (if supported and needed)
        # result_img: ConnectSessionResult = await client.connect_whatsapp_session(session_id=session_id, qr_as_image=True)
        # if result_img.response.data.qr_code_image_url:
        #     logger.info(f"QR Code Image URL: {result_img.response.data.qr_code_image_url}")

        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        # This might fail if the session is already connected or in a state not providing QR codes
        handle_session_api_error(e, f"getting QR code for session {session_id}")

# In main orchestrator: await get_session_qr_code_example(active_test_session_id)
```

### 6. Get Session Connection Status

Retrieves the current connection status of a specific WhatsApp session (e.g., `CONNECTED`, `NEED_SCAN`, `DISCONNECTED`).

```python
# Example: Get Session Connection Status
async def get_session_connection_status_example(session_id: int):
    logger.info(f"\n--- Checking Connection Status for Session ID: {session_id} ---")
    if not session_id:
        logger.error("Session ID is required.")
        return
        
    try:
        # More robust: get details which include status
        details_result: GetWhatsAppSessionDetailsResult = await async_client.get_whatsapp_session_details(session_id=session_id)
        current_status = details_result.response.data.status
        logger.info(f"Status for session {session_id}: {current_status.value if isinstance(current_status, WhatsAppSessionStatus) else current_status}")

        # If there was a specific get_session_status(session_id: str) method for string IDs:
        # result: GetSessionStatusResult = await client.get_session_status(session_id=str(session_id)) # Example cast
        # logger.info(f"Connection status for session {session_id}: {result.response.status.value}") # Access .value for Enum
        
        # Example of using the WhatsAppSessionStatus enum
        if current_status == WhatsAppSessionStatus.CONNECTED:
            logger.info("  Interpretation: Session is actively connected.")
        elif current_status == WhatsAppSessionStatus.NEED_SCAN:
            logger.info("  Interpretation: Session requires QR code scanning to connect.")
        
        log_rate_limit_info(details_result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, f"checking connection status for session {session_id}")

# In main orchestrator: await get_session_connection_status_example(active_test_session_id)
```

**Session Statuses Explained (Enum: `WhatsAppSessionStatus`)**

The `status` field in `SessionConnectionStatus` and other session-related responses will typically be one of the values from the `WhatsAppSessionStatus` enum (defined in `wasenderapi.models`):

*   `WhatsAppSessionStatus.CONNECTING`: The session is attempting to establish a connection with WhatsApp servers.
*   `WhatsAppSessionStatus.CONNECTED`: The session is successfully authenticated and actively connected to WhatsApp.
*   `WhatsAppSessionStatus.DISCONNECTED`: This is the initial status before any connection attempt or after a deliberate disconnect.
*   `WhatsAppSessionStatus.NEED_SCAN`: The session requires a QR code to be scanned with a WhatsApp mobile app to authenticate and connect.
*   `WhatsAppSessionStatus.LOGGED_OUT`: The user has logged out of the WhatsApp session (e.g., from the linked mobile device or another linked device).
*   `WhatsAppSessionStatus.EXPIRED`: The session is no longer valid, often due to extended inactivity or other WhatsApp internal reasons.
*   `WhatsAppSessionStatus.ERROR`: An error state, often accompanied by a message explaining the issue.
*   `WhatsAppSessionStatus.DEVICE_OFFLINE`: The phone associated with the session is offline. (This status might be provider-specific)
*   `WhatsAppSessionStatus.PROXY_ERROR`: Issues related to proxy connection if used. (Provider-specific)
*   `WhatsAppSessionStatus.TIMEOUT`: A connection attempt timed out.

*Note: The exact set of statuses and their meaning can sometimes vary slightly between WhatsApp API providers. Always refer to your specific provider's documentation if the SDK's enum doesn't cover a status you encounter.*

### 7. Disconnect WhatsApp Session

Disconnects an active session by its ID. This logs the session out.

```python
# Example: Disconnect WhatsApp Session
async def disconnect_session_example(session_id: int):
    logger.info(f"\n--- Disconnecting Session ID: {session_id} ---")
    if not session_id:
        logger.error("Session ID is required.")
        return
        
    try:
        result: DisconnectSessionResult = await async_client.disconnect_whatsapp_session(session_id=session_id)
        # DisconnectSessionResult.response.data is SessionConnectionStatus
        logger.info(f"Disconnect operation for session {session_id} - Status: {result.response.data.status.value}, Message: {result.response.data.message}")

        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, f"disconnecting session {session_id}")

# In main orchestrator: await disconnect_session_example(active_test_session_id) (conditionally)
```

### 8. Regenerate Session API Key

Regenerates the API key for a specific session. **Use with extreme caution, as this invalidates the previous API key for that session.** The regenerated key might be specific to this session instance and different from your main account or persona API keys. If a session-specific API key is generated, future direct operations on this session might require re-initializing the client with this new key.

```python
# Example: Regenerate Session API Key
async def regenerate_session_api_key_example(session_id: int):
    logger.warning(f"\n--- REGENERATING API KEY for Session ID: {session_id} (CAUTION!) ---")
    if not session_id:
        logger.error("Session ID is required.")
        return
        
    logger.warning(f"CAUTION: Regenerating the API key for session {session_id} will invalidate its current API key.")
    logger.warning("This operation is highly disruptive and usually not needed for standard workflows.")
    
    # Add a small delay and confirmation for safety in examples
    logger.info("This is a destructive operation. Pausing for 5 seconds...")
    await asyncio.sleep(5)
    logger.info("Proceeding with API key regeneration...")
    try:
        result: RegenerateApiKeyResult = await async_client.regenerate_api_key(session_id=session_id)
        # RegenerateApiKeyResult.response is RegenerateApiKeyResponse model
        logger.info(f"API Key regenerated for session {session_id}. New Key: {result.response.api_key}")
        
        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, f"regenerating API key for session {session_id}")

# In main orchestrator: (typically commented out or heavily guarded)
# await regenerate_session_api_key_example(active_test_session_id)
```

### 9. Delete WhatsApp Session

Deletes a specific session by its ID. **This action is irreversible and will remove the session and its associated data from the provider's system.**

```python
# Example: Delete WhatsApp Session
async def delete_session_example(session_id: int):
    logger.warning(f"\n--- DELETING Session ID: {session_id} (CAUTION!) ---")
    if not session_id:
        logger.error("Session ID is required.")
        return
        
    logger.warning(f"CAUTION: Deleting session {session_id} is irreversible!")
    # Add a small delay and confirmation for safety in examples
    logger.info("This is a destructive operation. Pausing for 5 seconds...")
    await asyncio.sleep(5)
    logger.info("Proceeding with session deletion...")
    try:
        result: DeleteWhatsAppSessionResult = await async_client.delete_whatsapp_session(session_id=session_id)
        # DeleteWhatsAppSessionResult.response is WasenderSuccessResponse (data is None)
        logger.info(f"Delete operation for session {session_id} - Success: {result.response.success}, Message: {result.response.message}")

        log_rate_limit_info(result.rate_limit)
            
    except Exception as e:
        handle_session_api_error(e, f"deleting session {session_id}")

# In main orchestrator: await delete_session_example(active_test_session_id)
```

## Running the Examples

1.  **Setup Environment Variables:**
    *   `WASENDER_API_KEY`: Your main Wasender account API key.
    *   `WASENDER_PERSONAL_ACCESS_TOKEN`: The Personal Access Token required for most session management operations demonstrated here (listing, creating, deleting, etc.).
    *   These are critical for authentication and authorization of session operations.

2.  **Review `session_examples_setup.py` Block:**
    *   Ensure the `WasenderAsyncClient` is initialized correctly. For the general session management examples shown, this uses both `api_key` and `personal_access_token`.
    *   Verify that the Pydantic models listed (e.g., `WhatsAppSession`, `CreateWhatsAppSessionPayload`, `QRCodeData`, `SessionConnectionStatus`) match those in your `wasenderapi/models.py`.

3.  **Understand the Orchestrator (`run_all_session_examples`)**:
    *   This function in the setup block tries to demonstrate a typical lifecycle: list, create, get details, update, connect (QR scan), check status, disconnect, and delete.
    *   **Use with extreme caution, especially against a production persona.** It actively creates and deletes sessions. It's best to use a dedicated test persona.
    *   It includes a simulated delay for QR code scanning (`asyncio.sleep(30)`). You might need to adjust this or manually pause the script if you're actually scanning.
    *   Destructive operations like regenerating API keys and deleting sessions are commented out or guarded in the orchestrator by default for safety.

4.  **Execute the Script:**
    *   Uncomment the `asyncio.run(run_all_session_examples())` line within the `if __name__ == "__main__":` block in the `session_examples_setup.py` section.
    *   Run the Python file (e.g., `python your_session_doc_file.py`).

5.  **Testing Individual Examples:**
    *   Each example function (e.g., `create_session_example()`, `get_session_details_example(session_id)`) can also be called individually.
    *   To do this, you would typically initialize the `async_client` (as in the setup block) and then use `asyncio.run(your_example_function_call())`. Make sure any required `session_id` is valid.

**Best Practices for Testing Session Management:**

*   **Start with a Test Persona:** Always use a dedicated persona for testing session creation, connection, and deletion to avoid impacting live services. Ensure the `WASENDER_PERSONAL_ACCESS_TOKEN` environment variable points to a token for this test persona.
*   **Read-Only First:** Begin by testing read-only operations like `get_all_sessions_example()` and `get_session_connection_status_example(existing_session_id)` to ensure your setup and authentication are correct.
*   **QR Code Handling:** When testing QR code generation (`get_session_qr_code_example`), be prepared to scan the QR code with a WhatsApp mobile app that is **not already linked to many sessions** and is suitable for testing. The QR code is usually time-sensitive.
*   **Monitor API Provider Dashboard:** If your API provider has a dashboard, monitor session creation and status there during your tests.
*   **Clean Up Test Sessions:** If you create sessions for testing, ensure you have a way to delete them afterwards (e.g., using `delete_session_example`) to keep your test environment clean. The orchestrator example attempts this.

This guide provides a comprehensive overview of session management with the Wasender Python SDK. Adapt these examples to your specific application needs and always handle session credentials and operations securely.
