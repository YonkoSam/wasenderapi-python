#!/usr/bin/env python3
"""
Example usage of the Wasender API SDK

This example demonstrates:
1. Sending a text message
2. Getting all contacts

Set the following environment variables before running:
- WASENDER_API_KEY: Your Wasender API key
- WASENDER_ACCESS_TOKEN: Your personal access token (optional)

Usage:
    python example.py
"""

import os
import asyncio
from wasenderapi import create_sync_wasender, create_async_wasender
from wasenderapi.models import RetryConfig
from wasenderapi.errors import WasenderAPIError


def get_api_credentials():
    """Get API credentials from environment variables."""
    api_key = os.getenv('WASENDER_API_KEY')
    access_token = os.getenv('WASENDER_ACCESS_TOKEN')
    
    if not api_key:
        raise ValueError(
            "WASENDER_API_KEY environment variable is required. "
            "Please set it to your Wasender API key."
        )
    
    return api_key, access_token


def sync_example():
    """Example using the synchronous client."""
    print("=== Synchronous Client Example ===")
    
    try:
        # Get credentials from environment
        api_key, access_token = get_api_credentials()
        
        # Create sync client with retry configuration
        retry_config = RetryConfig(enabled=True, max_retries=3)
        client = create_sync_wasender(
            api_key=api_key,
            personal_access_token=access_token,
            retry_options=retry_config
        )
        
        # Example 1: Send a text message
        print("\n1. Sending text message...")
        try:
            # Replace with an actual phone number for testing
            phone_number = "+1234567890"  # Update this with a real number
            message_text = "Hello from Wasender API SDK! 🚀"
            
            result = client.send_text(
                to=phone_number,
                text_body=message_text
            )
            
            print(f"✅ Message sent successfully!")
            print(f"   Status: {result.response.message}")
            
            # Show rate limit info
            if result.rate_limit:
                print(f"   Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit} remaining")
                
        except WasenderAPIError as e:
            print(f"❌ Failed to send message: {e.message}")
            if e.status_code == 429:
                print(f"   Rate limited. Retry after: {e.retry_after} seconds")
            elif e.error_details:
                print(f"   Error details: {e.error_details}")
          # Example 2: Get all contacts
        print("\n2. Getting contacts...")
        try:
            contacts_result = client.get_contacts()
            
            print(f"✅ Retrieved contacts successfully!")
            print(f"   Total contacts: {len(contacts_result.response.data)}")
            
            # Show first few contacts
            for i, contact in enumerate(contacts_result.response.data[:3]):
                contact_name = contact.name or "Unknown"
                contact_id = contact.id or "No ID"
                print(f"   Contact {i+1}: {contact_name} ({contact_id})")
            
            if len(contacts_result.response.data) > 3:
                print(f"   ... and {len(contacts_result.response.data) - 3} more")
                
        except WasenderAPIError as e:
            print(f"❌ Failed to get contacts: {e.message}")
            if e.status_code == 401:
                print("   Check your API key and access token")
            elif e.error_details:
                print(f"   Error details: {e.error_details}")
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def async_example():
    """Example using the asynchronous client."""
    print("\n=== Asynchronous Client Example ===")
    
    try:
        # Get credentials from environment
        api_key, access_token = get_api_credentials()
        
        # Create async client with retry configuration
        retry_config = RetryConfig(enabled=True, max_retries=3)
        
        async with create_async_wasender(
            api_key=api_key,
            personal_access_token=access_token,
            retry_options=retry_config
        ) as client:
            
            # Example 1: Send a text message
            print("\n1. Sending text message (async)...")
            try:
                # Replace with an actual phone number for testing
                phone_number = "+1234567890"  # Update this with a real number
                message_text = "Hello from Wasender API SDK (async)! 🚀"
                
                result = await client.send_text(
                    to=phone_number,
                    text_body=message_text
                )
                
                print(f"✅ Message sent successfully!")
                print(f"   Status: {result.response.message}")
                
                # Show rate limit info
                if result.rate_limit:
                    print(f"   Rate limit: {result.rate_limit.remaining}/{result.rate_limit.limit} remaining")
                    
            except WasenderAPIError as e:
                print(f"❌ Failed to send message: {e.message}")
                if e.status_code == 429:
                    print(f"   Rate limited. Retry after: {e.retry_after} seconds")
                elif e.error_details:
                    print(f"   Error details: {e.error_details}")
              # Example 2: Get all contacts
            print("\n2. Getting contacts (async)...")
            try:
                contacts_result = await client.get_contacts()
                
                print(f"✅ Retrieved contacts successfully!")
                print(f"   Total contacts: {len(contacts_result.response.data)}")
                
                # Show first few contacts
                for i, contact in enumerate(contacts_result.response.data[:3]):
                    contact_name = contact.name or "Unknown"
                    contact_id = contact.id or "No ID"
                    print(f"   Contact {i+1}: {contact_name} ({contact_id})")
                
                if len(contacts_result.response.data) > 3:
                    print(f"   ... and {len(contacts_result.response.data) - 3} more")
                    
            except WasenderAPIError as e:
                print(f"❌ Failed to get contacts: {e.message}")
                if e.status_code == 401:
                    print("   Check your API key and access token")
                elif e.error_details:
                    print(f"   Error details: {e.error_details}")
    
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Main function to run both sync and async examples."""
    print("Wasender API SDK Example")
    print("=" * 40)
    
    # Check if environment variables are set
    api_key = os.getenv('WASENDER_API_KEY')
    if not api_key:
        print("❌ Environment variable WASENDER_API_KEY is not set!")
        print("\nTo run this example, please set the required environment variables:")
        print("  WASENDER_API_KEY=your_api_key_here")
        print("  WASENDER_ACCESS_TOKEN=your_access_token_here  # Optional")
        print("\nExample:")
        print("  export WASENDER_API_KEY=wsk_...")
        print("  export WASENDER_ACCESS_TOKEN=pat_...")
        print("  python example.py")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    access_token = os.getenv('WASENDER_ACCESS_TOKEN')
    if access_token:
        print(f"✅ Access Token found: {access_token[:10]}...")
    else:
        print("ℹ️  Access Token not provided (optional)")
    
    # Run synchronous example
    sync_example()
    
    # Run asynchronous example
    asyncio.run(async_example())
    
    print("\n" + "=" * 40)
    print("Examples completed!")


if __name__ == "__main__":
    main()
