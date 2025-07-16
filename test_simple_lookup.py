#!/usr/bin/env python3
"""
Simple test for routing table lookup functionality
"""
import os
import json
import asyncio
import logging
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from utils import VPCManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_simple_lookup():
    """Test routing table name lookup functionality"""
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    if not api_key:
        print("Error: IBMCLOUD_API_KEY environment variable not set")
        return
    
    authenticator = IAMAuthenticator(apikey=api_key)
    vpc_manager = VPCManager(authenticator)
    
    region = 'us-south'
    print(f"Testing in region: {region}")
    
    # Get VPC ID
    vpcs_result = await vpc_manager.list_vpcs(region)
    if 'error' in vpcs_result or vpcs_result['count'] == 0:
        print("No VPCs found")
        return
    
    vpc_id = vpcs_result['vpcs'][0]['id']
    print(f"Using VPC: {vpc_id}")
    
    # Get routing table names
    tables_result = await vpc_manager.list_routing_tables(region, vpc_id)
    if 'error' in tables_result or tables_result['count'] == 0:
        print("No routing tables found")
        return
    
    first_table = tables_result['routing_tables'][0]
    table_name = first_table['name']
    expected_id = first_table['id']
    
    print(f"Testing lookup for: '{table_name}'")
    print(f"Expected ID: {expected_id}")
    
    # Test the lookup
    lookup_result = await vpc_manager.find_routing_table_by_name(region, vpc_id, table_name)
    
    print("Lookup result:")
    print(json.dumps(lookup_result, indent=2))
    
    if 'error' in lookup_result:
        print("❌ Lookup failed")
    elif 'match' in lookup_result:
        found_id = lookup_result['match']['id']
        convenience_id = lookup_result.get('id')
        
        print(f"✅ Found table ID: {found_id}")
        print(f"✅ Convenience ID: {convenience_id}")
        
        if found_id == expected_id and convenience_id == expected_id:
            print("✅ All IDs match expected value")
        else:
            print("❌ ID mismatch")
    else:
        print("❌ Unexpected result format")

if __name__ == "__main__":
    asyncio.run(test_simple_lookup())