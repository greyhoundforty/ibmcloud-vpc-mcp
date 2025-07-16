#!/usr/bin/env python3
"""
Check available methods in IBM Cloud VPC SDK
"""
import os
import ibm_vpc
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def check_vpc_methods():
    """Check what methods are available in VpcV1"""
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    if not api_key:
        print("Error: IBMCLOUD_API_KEY environment variable not set")
        return
    
    authenticator = IAMAuthenticator(apikey=api_key)
    service = ibm_vpc.VpcV1(version='2025-04-08', authenticator=authenticator)
    
    # Get all methods
    all_methods = [method for method in dir(service) if not method.startswith('_')]
    
    print("All VpcV1 methods:")
    print("=" * 50)
    
    # Look for routing-related methods
    routing_methods = [m for m in all_methods if 'routing' in m.lower() or 'route' in m.lower()]
    print(f"\nRouting-related methods ({len(routing_methods)}):")
    for method in sorted(routing_methods):
        print(f"  - {method}")
    
    # Look for table-related methods
    table_methods = [m for m in all_methods if 'table' in m.lower()]
    print(f"\nTable-related methods ({len(table_methods)}):")
    for method in sorted(table_methods):
        print(f"  - {method}")
    
    # Look for snapshot-related methods
    snapshot_methods = [m for m in all_methods if 'snapshot' in m.lower()]
    print(f"\nSnapshot-related methods ({len(snapshot_methods)}):")
    for method in sorted(snapshot_methods):
        print(f"  - {method}")
    
    # Look for backup-related methods
    backup_methods = [m for m in all_methods if 'backup' in m.lower()]
    print(f"\nBackup-related methods ({len(backup_methods)}):")
    for method in sorted(backup_methods):
        print(f"  - {method}")

if __name__ == "__main__":
    check_vpc_methods()