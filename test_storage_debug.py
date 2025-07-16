#!/usr/bin/env python3
"""
Debug script for storage tools
"""
import os
import json
import asyncio
import logging
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from storage import StorageManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_storage_tools():
    """Test storage tools with debug output"""
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    if not api_key:
        print("Error: IBMCLOUD_API_KEY environment variable not set")
        return
    
    authenticator = IAMAuthenticator(apikey=api_key)
    storage_manager = StorageManager(None, authenticator)
    
    # Test regions
    test_regions = ['us-south', 'us-east']
    
    for region in test_regions:
        print(f"\n{'='*50}")
        print(f"Testing region: {region}")
        print('='*50)
        
        # Test list_volumes
        print("\n--- Testing list_volumes ---")
        try:
            volumes_result = await storage_manager.list_volumes(region, limit=5)
            print(f"Volumes result type: {type(volumes_result)}")
            print(f"Volumes result keys: {list(volumes_result.keys())}")
            
            if 'error' in volumes_result:
                print(f"Error in volumes: {volumes_result['error']}")
            else:
                print(f"Found {volumes_result['count']} volumes")
                if volumes_result['count'] > 0:
                    print(f"First volume keys: {list(volumes_result['volumes'][0].keys())}")
                    
        except Exception as e:
            print(f"Exception in list_volumes: {e}")
            logger.exception("Full traceback:")
        
        # Test list_shares
        print("\n--- Testing list_shares ---")
        try:
            shares_result = await storage_manager.list_shares(region, limit=5)
            print(f"Shares result type: {type(shares_result)}")
            print(f"Shares result keys: {list(shares_result.keys())}")
            
            if 'error' in shares_result:
                print(f"Error in shares: {shares_result['error']}")
            else:
                print(f"Found {shares_result['count']} shares")
                if shares_result['count'] > 0:
                    print(f"First share keys: {list(shares_result['shares'][0].keys())}")
                    
        except Exception as e:
            print(f"Exception in list_shares: {e}")
            logger.exception("Full traceback:")
        
        # Test volume profiles
        print("\n--- Testing list_volume_profiles ---")
        try:
            profiles_result = await storage_manager.list_volume_profiles(region, limit=5)
            print(f"Volume profiles result: {profiles_result['count']} profiles")
            
        except Exception as e:
            print(f"Exception in list_volume_profiles: {e}")
            logger.exception("Full traceback:")
            
        # Test share profiles
        print("\n--- Testing list_share_profiles ---")
        try:
            share_profiles_result = await storage_manager.list_share_profiles(region, limit=5)
            print(f"Share profiles result: {share_profiles_result['count']} profiles")
            
        except Exception as e:
            print(f"Exception in list_share_profiles: {e}")
            logger.exception("Full traceback:")

if __name__ == "__main__":
    asyncio.run(test_storage_tools())