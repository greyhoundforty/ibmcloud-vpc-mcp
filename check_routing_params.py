#!/usr/bin/env python3
"""
Check parameters for VPC routing table methods
"""
import os
import ibm_vpc
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import inspect

def check_routing_params():
    """Check parameters for routing table methods"""
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    if not api_key:
        print("Error: IBMCLOUD_API_KEY environment variable not set")
        return
    
    authenticator = IAMAuthenticator(apikey=api_key)
    service = ibm_vpc.VpcV1(version='2025-04-08', authenticator=authenticator)
    
    # Check list_vpc_routing_tables parameters
    print("list_vpc_routing_tables parameters:")
    print("=" * 40)
    try:
        sig = inspect.signature(service.list_vpc_routing_tables)
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                print(f"  {param_name}: {param.annotation} = {param.default}")
    except Exception as e:
        print(f"Error getting signature: {e}")
    
    # Check get_vpc_routing_table parameters
    print("\nget_vpc_routing_table parameters:")
    print("=" * 40)
    try:
        sig = inspect.signature(service.get_vpc_routing_table)
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                print(f"  {param_name}: {param.annotation} = {param.default}")
    except Exception as e:
        print(f"Error getting signature: {e}")

if __name__ == "__main__":
    check_routing_params()