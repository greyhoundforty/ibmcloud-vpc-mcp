#!/usr/bin/env python3
"""
Test script for new routing table and snapshot tools
"""
import os
import json
import asyncio
import logging
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from utils import VPCManager
from storage import StorageManager

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_routing_tables():
    """Test routing table tools"""
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    if not api_key:
        print("Error: IBMCLOUD_API_KEY environment variable not set")
        return
    
    authenticator = IAMAuthenticator(apikey=api_key)
    vpc_manager = VPCManager(authenticator)
    
    # Test regions
    test_regions = ['us-south', 'us-east']
    
    for region in test_regions:
        print(f"\n{'='*60}")
        print(f"Testing Routing Tables in region: {region}")
        print('='*60)
        
        # First, get a VPC ID to test routing tables with
        print("\n--- Getting VPC ID for routing table tests ---")
        vpc_test_id = None
        try:
            vpcs_result = await vpc_manager.list_vpcs(region)
            if 'error' not in vpcs_result and vpcs_result['count'] > 0:
                vpc_test_id = vpcs_result['vpcs'][0]['id']
                print(f"Using VPC ID: {vpc_test_id}")
            else:
                print(f"No VPCs found in {region} for routing table tests")
        except Exception as e:
            print(f"Error getting VPC ID: {e}")
        
        if vpc_test_id:
            # Test list_routing_tables
            print("\n--- Testing list_routing_tables ---")
            try:
                result = await vpc_manager.list_routing_tables(region, vpc_test_id, limit=5)
                print(f"Result type: {type(result)}")
                print(f"Result keys: {list(result.keys())}")
                
                if 'error' in result:
                    print(f"Error: {result['error']}")
                else:
                    print(f"Found {result['count']} routing tables")
                    if result['count'] > 0:
                        print(f"First routing table: {result['routing_tables'][0]['name']}")
                        
                        # Test get_routing_table with first table
                        first_table_id = result['routing_tables'][0]['id']
                        print(f"\n--- Testing get_routing_table for {first_table_id} ---")
                        
                        table_detail = await vpc_manager.get_routing_table(vpc_test_id, first_table_id, region)
                        if 'error' in table_detail:
                            print(f"Error getting table details: {table_detail['error']}")
                        else:
                            print(f"Table details: {table_detail['name']}")
                            print(f"Is default: {table_detail['is_default']}")
                            print(f"Routes count: {table_detail.get('routes_count', 0)}")
                            
            except Exception as e:
                print(f"Exception: {e}")
                logger.exception("Full traceback:")
        else:
            print("\n--- Skipping routing table tests (no VPC ID available) ---")

async def test_snapshots():
    """Test snapshot tools"""
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    if not api_key:
        print("Error: IBMCLOUD_API_KEY environment variable not set")
        return
    
    authenticator = IAMAuthenticator(apikey=api_key)
    storage_manager = StorageManager(None, authenticator)
    
    # Test regions
    test_regions = ['us-south', 'us-east']
    
    for region in test_regions:
        print(f"\n{'='*60}")
        print(f"Testing Snapshots in region: {region}")
        print('='*60)
        
        # Test list_snapshots
        print("\n--- Testing list_snapshots ---")
        try:
            result = await storage_manager.list_snapshots(region, limit=5)
            print(f"Result type: {type(result)}")
            print(f"Result keys: {list(result.keys())}")
            
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Found {result['count']} snapshots")
                if result['count'] > 0:
                    print(f"First snapshot: {result['snapshots'][0]['name']}")
                    
                    # Test get_snapshot with first snapshot
                    first_snapshot_id = result['snapshots'][0]['id']
                    print(f"\n--- Testing get_snapshot for {first_snapshot_id} ---")
                    
                    snapshot_detail = await storage_manager.get_snapshot(first_snapshot_id, region)
                    if 'error' in snapshot_detail:
                        print(f"Error getting snapshot details: {snapshot_detail['error']}")
                    else:
                        print(f"Snapshot details: {snapshot_detail['name']}")
                        print(f"Status: {snapshot_detail['status']}")
                        print(f"Size: {snapshot_detail['size']} GB")
                        print(f"Bootable: {snapshot_detail['bootable']}")
                        
        except Exception as e:
            print(f"Exception: {e}")
            logger.exception("Full traceback:")
        
        # Test analyze_snapshot_usage
        print("\n--- Testing analyze_snapshot_usage ---")
        try:
            usage_result = await storage_manager.analyze_snapshot_usage(region)
            if 'error' in usage_result:
                print(f"Error: {usage_result['error']}")
            else:
                print(f"Usage analysis complete:")
                print(f"  Total snapshots: {usage_result['summary']['total_snapshots']}")
                print(f"  Total size: {usage_result['summary']['total_size_gb']} GB")
                print(f"  Bootable snapshots: {usage_result['summary']['bootable_snapshots']}")
                
        except Exception as e:
            print(f"Exception: {e}")
            logger.exception("Full traceback:")

async def main():
    """Run all tests"""
    print("🚀 Testing New Tools: Routing Tables and Snapshots")
    print("=" * 80)
    
    await test_routing_tables()
    await test_snapshots()
    
    print("\n" + "=" * 80)
    print("✅ Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main())