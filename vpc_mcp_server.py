"""
IBM Cloud VPC MCP Server
Provides VPC resource management capabilities through MCP protocol
"""

import os
import json
import logging
from typing import Dict, List, Any
import asyncio

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from utils import VPCManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VPCMCPServer:
    def __init__(self):
        self.server = Server("ibm-vpc-mcp")
        self.vpc_manager = None
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Set up MCP server handlers"""
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="list_regions",
                    description="List all available IBM Cloud VPC regions",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_vpcs",
                    description="List VPCs in account or specific region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name (optional, defaults to all regions)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_vpc",
                    description="Get details of a specific VPC",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vpc_id": {
                                "type": "string",
                                "description": "VPC ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region where VPC is located"
                            }
                        },
                        "required": ["vpc_id", "region"]
                    }
                ),
                Tool(
                    name="list_subnets",
                    description="List subnets in a VPC or region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_instances",
                    description="List compute instances",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_instance_profiles",
                    description="List available instance profiles",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_public_gateways",
                    description="List public gateways",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_security_groups",
                    description="List security groups",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="get_security_group",
                    description="Get detailed information about a specific security group including rules",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "security_group_id": {
                                "type": "string",
                                "description": "Security group ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["security_group_id", "region"]
                    }
                ),
                Tool(
                    name="list_security_group_rules",
                    description="List all rules for a specific security group",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "security_group_id": {
                                "type": "string",
                                "description": "Security group ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["security_group_id", "region"]
                    }
                ),
                Tool(
                    name="analyze_ssh_security_groups",
                    description="Find security groups with SSH access open to 0.0.0.0/0",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="analyze_security_groups_by_protocol",
                    description="Analyze security groups for specific protocol/port combinations from a source CIDR",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "protocol": {
                                "type": "string",
                                "description": "Protocol (tcp, udp, icmp)"
                            },
                            "port": {
                                "type": "integer",
                                "description": "Port number (optional)"
                            },
                            "source_cidr": {
                                "type": "string",
                                "description": "Source CIDR block (default: 0.0.0.0/0)",
                                "default": "0.0.0.0/0"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region", "protocol"]
                    }
                ),
                Tool(
                    name="list_floating_ips",
                    description="List all floating IPs in a region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="get_vpc_resources_summary",
                    description="Get a summary of all resources in a VPC including security analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vpc_id": {
                                "type": "string",
                                "description": "VPC ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region where VPC is located"
                            }
                        },
                        "required": ["vpc_id", "region"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                # Initialize VPC manager if not already done
                if not self.vpc_manager:
                    api_key = os.environ.get('IBMCLOUD_API_KEY')
                    if not api_key:
                        raise ValueError("IBMCLOUD_API_KEY environment variable not set")
                    authenticator = IAMAuthenticator(apikey=api_key)
                    self.vpc_manager = VPCManager(authenticator)
                
                # Route to appropriate handler
                if name == "list_regions":
                    result = await self.vpc_manager.list_regions()
                elif name == "list_vpcs":
                    result = await self.vpc_manager.list_vpcs(arguments.get('region'))
                elif name == "get_vpc":
                    result = await self.vpc_manager.get_vpc(arguments['vpc_id'], arguments['region'])
                elif name == "list_subnets":
                    result = await self.vpc_manager.list_subnets(arguments['region'], arguments.get('vpc_id'))
                elif name == "list_instances":
                    result = await self.vpc_manager.list_instances(arguments['region'], arguments.get('vpc_id'))
                elif name == "list_instance_profiles":
                    result = await self.vpc_manager.list_instance_profiles(arguments['region'])
                elif name == "list_public_gateways":
                    result = await self.vpc_manager.list_public_gateways(arguments['region'], arguments.get('vpc_id'))
                elif name == "list_security_groups":
                    result = await self.vpc_manager.list_security_groups(arguments['region'], arguments.get('vpc_id'))
                elif name == "get_security_group":
                    result = await self.vpc_manager.get_security_group(arguments['security_group_id'], arguments['region'])
                elif name == "list_security_group_rules":
                    result = await self.vpc_manager.list_security_group_rules(arguments['security_group_id'], arguments['region'])
                elif name == "analyze_ssh_security_groups":
                    result = await self.vpc_manager.analyze_ssh_security_groups(arguments['region'], arguments.get('vpc_id'))
                elif name == "analyze_security_groups_by_protocol":
                    result = await self.vpc_manager.analyze_security_groups_by_protocol(
                        arguments['region'], 
                        arguments['protocol'],
                        arguments.get('port'),
                        arguments.get('source_cidr', '0.0.0.0/0'),
                        arguments.get('vpc_id')
                    )
                elif name == "list_floating_ips":
                    result = await self.vpc_manager.list_floating_ips(arguments['region'])
                elif name == "get_vpc_resources_summary":
                    result = await self.vpc_manager.get_vpc_resources_summary(arguments['vpc_id'], arguments['region'])
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    server = VPCMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())