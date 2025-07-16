#!/usr/bin/env python3
"""
Test script for routing table name lookup functionality
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

async def test_routing_table_lookup():
    """Test routing table name lookup functionality"""
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    if not api_key:
        print("Error: IBMCLOUD_API_KEY environment variable not set")
        return
    
    authenticator = IAMAuthenticator(apikey=api_key)
    vpc_manager = VPCManager(authenticator)
    
    # Test regions
    test_regions = ['us-south', 'ca-tor']
    
    for region in test_regions:
        print(f"\n{'='*60}")
        print(f"Testing Routing Table Lookup in region: {region}")
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
            # First, list all routing tables to get their names
            print("\n--- Listing all routing tables to get names ---")
            try:
                all_tables = await vpc_manager.list_routing_tables(region, vpc_test_id)
                if 'error' in all_tables:
                    print(f"Error listing tables: {all_tables['error']}")
                    continue
                
                routing_tables = all_tables.get('routing_tables', [])
                print(f"Found {len(routing_tables)} routing tables:")
                for table in routing_tables:
                    print(f"  - Name: '{table['name']}', ID: {table['id']}, Default: {table['is_default']}")
                
                if not routing_tables:
                    print("No routing tables found to test lookup")
                    continue
                
                # Test lookup with different routing table names
                test_cases = []
                
                # Test case 1: Exact match with first table
                first_table = routing_tables[0]
                test_cases.append({
                    'name': first_table['name'],
                    'expected_id': first_table['id'],
                    'description': f"Exact match for '{first_table['name']}'"
                })
                
                # Test case 2: Non-existent table
                test_cases.append({
                    'name': 'non-existent-table-name',
                    'expected_id': None,
                    'description': "Non-existent table name"
                })
                
                # Test case 3: Partial match (if available)
                if len(routing_tables) > 1:
                    second_table = routing_tables[1]
                    test_cases.append({
                        'name': second_table['name'],
                        'expected_id': second_table['id'],
                        'description': f"Exact match for '{second_table['name']}'"
                    })
                
                # Test case 4: Case sensitivity test
                if routing_tables:
                    upper_name = first_table['name'].upper()
                    test_cases.append({
                        'name': upper_name,
                        'expected_id': first_table['id'] if upper_name.lower() == first_table['name'].lower() else None,
                        'description': f"Case test with '{upper_name}'"
                    })
                
                # Run all test cases
                for i, test_case in enumerate(test_cases, 1):
                    print(f"\n--- Test Case {i}: {test_case['description']} ---")
                    
                    try:
                        result = await vpc_manager.find_routing_table_by_name(
                            region, vpc_test_id, test_case['name']
                        )
                        
                        print(f"Lookup result for '{test_case['name']}':")
                        print(f"  Status: {'✅ SUCCESS' if 'error' not in result else '❌ ERROR'}")
                        
                        if 'error' in result:
                            print(f"  Error: {result['error']}")
                        elif 'warning' in result:
                            print(f"  Warning: {result['warning']}")
                            print(f"  Found Count: {result.get('found_count', 0)}")
                            if 'matches' in result:
                                print(f"  Partial matches: {len(result['matches'])}")
                        else:
                            print(f"  Found Count: {result.get('found_count', 0)}")
                            if 'match' in result:
                                print(f"  Found ID: {result['match']['id']}")
                                print(f"  Found Name: {result['match']['name']}")
                                print(f"  Convenience ID: {result.get('id', 'N/A')}")
                                
                                # Verify the ID matches expectation
                                if test_case['expected_id'] == result['match']['id']:
                                    print(f"  Verification: ✅ ID matches expected")
                                else:
                                    print(f"  Verification: ❌ ID mismatch (expected: {test_case['expected_id']})")
                            
                            if 'matches' in result:
                                print(f"  Multiple matches: {len(result['matches'])}")
                        
                    except Exception as e:
                        print(f"  Exception: {e}")
                        logger.exception("Full traceback:")
                
            except Exception as e:
                print(f"Exception during testing: {e}")
                logger.exception("Full traceback:")
        else:
            print("\\n--- Skipping routing table lookup tests (no VPC ID available) ---")

async def main():
    """Run all tests"""
    print("🔍 Testing Routing Table Name Lookup Functionality")
    print("=" * 80)
    
    await test_routing_table_lookup()
    
    print("\\n" + "=" * 80)
    print("✅ Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main())