#!/usr/bin/env python3
"""
Test the routing table lookup function via MCP protocol
"""
import os
import json
import asyncio
import subprocess
from typing import Dict, Any

class SimpleMCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self):
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process"""
        env = os.environ.copy()
        if 'IBMCLOUD_API_KEY' not in env:
            raise ValueError("IBMCLOUD_API_KEY environment variable not set")
        
        self.process = await asyncio.create_subprocess_exec(
            'python', 'vpc_mcp_server.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        # Initialize MCP protocol
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        await self.send_request(init_request)
        response = await self.read_response()
        print(f"Initialize response: {response}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self.send_request(initialized_notification)
    
    async def send_request(self, request: Dict[str, Any]):
        """Send a request to the MCP server"""
        message = json.dumps(request) + "\\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
    
    async def read_response(self):
        """Read a response from the MCP server"""
        line = await self.process.stdout.readline()
        if line:
            return json.loads(line.decode().strip())
        return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call a specific tool"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self.send_request(request)
        response = await self.read_response()
        return response
    
    async def close(self):
        """Close the MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

async def test_routing_table_lookup_mcp():
    """Test routing table lookup via MCP protocol"""
    client = SimpleMCPClient()
    
    try:
        print("Starting MCP server...")
        await client.start_server()
        
        # First get a VPC ID for routing table tests
        print("\\n" + "="*50)
        print("Getting VPC ID for routing table tests...")
        vpc_response = await client.call_tool("list_vpcs", {
            "region": "us-south",
            "limit": 1
        })
        
        vpc_id = None
        if vpc_response and 'result' in vpc_response:
            content = vpc_response['result']['content'][0]['text']
            vpc_data = json.loads(content)
            if vpc_data.get('count', 0) > 0:
                vpc_id = vpc_data['vpcs'][0]['id']
                print(f"Using VPC ID: {vpc_id}")
        
        if not vpc_id:
            print("❌ No VPC ID available for routing table tests")
            return
        
        # Get a routing table name to test with
        print("\\n" + "="*50)
        print("Getting routing table names...")
        tables_response = await client.call_tool("list_routing_tables", {
            "region": "us-south",
            "vpc_id": vpc_id,
            "limit": 5
        })
        
        routing_table_name = None
        if tables_response and 'result' in tables_response:
            content = tables_response['result']['content'][0]['text']
            tables_data = json.loads(content)
            if tables_data.get('count', 0) > 0:
                routing_table_name = tables_data['routing_tables'][0]['name']
                expected_id = tables_data['routing_tables'][0]['id']
                print(f"Using routing table name: '{routing_table_name}'")
                print(f"Expected ID: {expected_id}")
        
        if not routing_table_name:
            print("❌ No routing table name available for lookup tests")
            return
        
        # Test the lookup function
        print("\\n" + "="*50)
        print("Testing find_routing_table_by_name tool...")
        lookup_response = await client.call_tool("find_routing_table_by_name", {
            "region": "us-south",
            "vpc_id": vpc_id,
            "name": routing_table_name
        })
        
        if lookup_response and 'result' in lookup_response:
            print("✅ find_routing_table_by_name succeeded")
            content = lookup_response['result']['content'][0]['text']
            lookup_data = json.loads(content)
            print(f"Lookup result: {json.dumps(lookup_data, indent=2)}")
            
            # Verify the result
            if 'error' in lookup_data:
                print(f"❌ Error: {lookup_data['error']}")
            elif 'match' in lookup_data:
                found_id = lookup_data['match']['id']
                found_name = lookup_data['match']['name']
                convenience_id = lookup_data.get('id')
                
                print(f"✅ Found routing table:")
                print(f"  Name: {found_name}")
                print(f"  ID: {found_id}")
                print(f"  Convenience ID: {convenience_id}")
                
                if found_id == expected_id:
                    print("✅ ID matches expected value")
                else:
                    print("❌ ID does not match expected value")
            else:
                print("❌ Unexpected result format")
        else:
            print("❌ find_routing_table_by_name failed")
            print(f"Response: {lookup_response}")
        
        # Test with non-existent name
        print("\\n" + "="*50)
        print("Testing with non-existent routing table name...")
        bad_lookup_response = await client.call_tool("find_routing_table_by_name", {
            "region": "us-south",
            "vpc_id": vpc_id,
            "name": "non-existent-table-name"
        })
        
        if bad_lookup_response and 'result' in bad_lookup_response:
            content = bad_lookup_response['result']['content'][0]['text']
            bad_lookup_data = json.loads(content)
            
            if 'error' in bad_lookup_data:
                print("✅ Correctly handled non-existent table name")
                print(f"  Error message: {bad_lookup_data['error']}")
            else:
                print("❌ Expected error for non-existent table name")
        else:
            print("❌ Failed to test non-existent table name")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_routing_table_lookup_mcp())