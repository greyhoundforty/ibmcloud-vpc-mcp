# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an IBM Cloud VPC MCP (Model Context Protocol) Server that provides comprehensive IBM Cloud VPC resource management and security analysis capabilities. The server enables interaction with IBM Cloud VPC infrastructure through a standardized MCP protocol interface.

## Key Architecture Components

### Core Files
- **`vpc_mcp_server.py`**: Main MCP server implementation and protocol handler
- **`utils.py`**: VPCManager class with core IBM Cloud VPC management logic
- **`storage.py`**: StorageManager class for block storage and file share operations
- **`requirements.txt`**: Python dependencies including IBM Cloud SDK and MCP libraries

### Main Classes
- **`VPCMCPServer`**: Handles MCP protocol communication and tool routing
- **`VPCManager`**: Core class for IBM Cloud VPC API interactions and operations
- **`StorageManager`**: Manages block storage volumes and file shares

## Common Development Commands

### Environment Setup
```bash
# Install dependencies
mise run uv:reqs

# Set up development environment
mise run dev

# Set required environment variable
export IBMCLOUD_API_KEY="your-api-key-here"
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest test_utils.py

# Run integration tests (requires valid API key)
python -m pytest test_integration.py -m integration

# Run with verbose output
python -m pytest -v
```

### Docker Operations
```bash
# Build Docker image
mise run docker:build

# Run in production mode
mise run docker:run

# Run in development mode with volume mounts
mise run docker:dev

# Test container functionality
mise run docker:test

# View container logs
mise run docker:logs

# Clean up Docker resources
mise run docker:clean
```

### Security Analysis
```bash
# Check for SSH exposure across regions
mise run security:check-ssh

# Check for RDP exposure across regions
mise run security:check-rdp
```

### Running Locally
```bash
# Run MCP server locally
python vpc_mcp_server.py

# Run with debug logging
LOG_LEVEL=DEBUG python vpc_mcp_server.py
```

## Development Architecture

### MCP Protocol Integration
The server implements the Model Context Protocol (MCP) for standardized tool communication:
- MCP tools are registered in `vpc_mcp_server.py` with JSON schemas
- Tool handlers route requests to appropriate VPCManager or StorageManager methods
- All communication uses stdio for MCP client integration

### IBM Cloud SDK Integration
- Uses `ibm-vpc` SDK for VPC operations
- Implements IAM authentication with API key
- Maintains regional VPC client caching for performance
- Handles multi-region operations with proper error handling

### Core Tool Categories
1. **VPC Management**: List regions, VPCs, subnets, instances
2. **Security Analysis**: SSH/RDP exposure detection, protocol analysis
3. **Resource Management**: Security groups, floating IPs, public gateways
4. **Backup Operations**: Backup policies, jobs, plans, health analysis
5. **Storage Operations**: Block volumes, profiles, usage analysis, file shares
6. **Routing Tables**: List routing tables, get routing table details, lookup by name
7. **Snapshots**: List snapshots, get snapshot details, usage analysis
8. **VPN Gateway Management**: List gateways, get gateway details, IKE/IPsec policies
9. **VPN Server Management**: List servers, get server details with authentication, client configuration, client management, routing

## Configuration Requirements

### Environment Variables
- `IBMCLOUD_API_KEY`: Required IBM Cloud API key with VPC permissions
- `LOG_LEVEL`: Optional logging level (INFO, DEBUG, ERROR)
- `PYTHONUNBUFFERED`: Optional unbuffered output for containers

### IBM Cloud Permissions
The API key must have:
- VPC Reader or Administrator permissions
- Access to all regions being analyzed
- Resource Group access for filtered operations

## Error Handling Patterns

### API Error Handling
- All VPC operations wrapped in try/catch blocks
- Regional operations continue on single-region failures
- Detailed error logging with context information
- Graceful degradation for missing permissions

### MCP Error Responses
- Tool errors return structured error messages
- Client-safe error formatting without sensitive data
- Logging separation between client and server errors

## Testing Strategy

### Unit Tests (`test_utils.py`)
- Mock-based testing for all VPCManager methods
- Security analysis function testing
- Backup policy health analysis validation
- Authentication and client creation testing

### Integration Tests (`test_integration.py`)
- Real API testing with live IBM Cloud account
- Multi-region operation validation
- End-to-end tool workflow testing
- Performance and reliability testing

### Test Configuration (`conftest.py`)
- Pytest markers for integration and slow tests
- Environment-based test configuration
- Shared fixtures for consistent testing
- Logging configuration for test runs

## Common Patterns

### Multi-Region Operations
```python
# Check all regions if none specified
if not self.regions:
    await self.list_regions()
regions_to_check = self.regions

# Handle per-region failures gracefully
for region_name in regions_to_check:
    try:
        # region operations
    except ApiException as e:
        logger.warning(f"Error in region {region_name}: {e}")
```

### VPC Client Caching
```python
def _get_vpc_client(self, region: str) -> ibm_vpc.VpcV1:
    if region not in self.vpc_clients:
        service = ibm_vpc.VpcV1(version='2025-04-08', authenticator=self.authenticator)
        service.set_service_url(f'https://{region}.iaas.cloud.ibm.com/v1')
        self.vpc_clients[region] = service
    return self.vpc_clients[region]
```

### Security Analysis Pattern
```python
# Get security groups -> Get rules -> Analyze rules -> Return structured results
sg_response = service.list_security_groups().get_result()
for sg in security_groups:
    rules_response = service.list_security_group_rules(security_group_id=sg['id']).get_result()
    # Analyze rules for specific risks
    # Return structured analysis with risk levels
```

### Routing Table Name Lookup
```python
# Find routing table by name - returns UUID and details
result = await vpc_manager.find_routing_table_by_name(region, vpc_id, "table-name")

# Handle different response cases
if 'error' in result:
    # No matching table found
    print(f"Error: {result['error']}")
elif 'warning' in result:
    # Multiple matches or partial matches
    print(f"Warning: {result['warning']}")
    matches = result.get('matches', [])
else:
    # Single exact match (ideal case)
    table_id = result['id']  # Convenience field
    full_details = result['match']  # Complete table info
    
# Use the ID with get_routing_table for full details
table_details = await vpc_manager.get_routing_table(vpc_id, table_id, region)
```

## Security Considerations

### API Key Handling
- API keys passed via environment variables only
- No API key logging or storage in code
- Docker containers use environment variable passing
- Key validation before MCP server startup

### Data Privacy
- No sensitive data in error messages sent to clients
- Minimal data retention in memory caches
- Regional data isolation in client caching
- Proper cleanup of authentication objects

## Performance Optimization

### Caching Strategy
- Regional VPC client caching to avoid re-authentication
- Region list caching to minimize API calls
- No persistent caching of resource data (always fresh)

### Concurrent Operations
- Multi-region operations run sequentially with error isolation
- Individual tool calls are synchronous for deterministic results
- Docker containers can run multiple instances for scaling

## VPN Management Features

### VPN Gateway Operations
The server supports comprehensive VPN Gateway management for site-to-site connectivity:

#### Available Methods (utils.py:920-949, utils.py:1031-1059)
- **`list_vpn_gateways`**: Lists VPN gateways with optional VPC filtering and pagination
- **`get_vpn_gateway`**: Gets detailed gateway information 
- **`get_ike_policy`**: Retrieves IKE policy details for gateway configuration
- **`get_ipsec_policy`**: Retrieves IPsec policy details for gateway configuration

#### Usage Pattern
```python
# List all VPN gateways in region
gateways = await vpc_manager.list_vpn_gateways('us-south')

# Filter by VPC
vpc_gateways = await vpc_manager.list_vpn_gateways('us-south', vpc_id='vpc-12345')

# Get detailed gateway information
gateway_details = await vpc_manager.get_vpn_gateway('vpn-gateway-id', 'us-south')

# Get associated policies
ike_policy = await vpc_manager.get_ike_policy('ike-policy-id', 'us-south')
ipsec_policy = await vpc_manager.get_ipsec_policy('ipsec-policy-id', 'us-south')
```

### VPN Server Operations
The server supports comprehensive VPN Server management for client access connectivity:

#### Available Methods (utils.py:966-1137)
- **`list_vpn_servers`**: Lists VPN servers with optional name filtering and pagination
- **`get_vpn_server`**: Gets detailed server information including authentication methods
- **`get_vpn_server_client_configuration`**: Retrieves OpenVPN client configuration files
- **`list_vpn_server_clients`**: Lists clients connected to a VPN server with pagination and sorting
- **`list_vpn_server_routes`**: Lists routing configuration for VPN servers

#### Enhanced Authentication Support
The `get_vpn_server` method now includes automatic extraction of authentication information:
```python
# Response includes authentication_summary section
{
    "authentication_summary": {
        "certificate_based": {
            "enabled": True,
            "certificate_instance": { ... }
        },
        "client_authentication": [
            {"method": "certificate"},
            {"method": "username"}
        ]
    }
}
```

#### Client Configuration Handling
The `get_vpn_server_client_configuration` method handles various data formats:
- **String Content**: OpenVPN configuration returned as UTF-8 string
- **Binary Data**: Automatically base64-encoded if UTF-8 decoding fails
- **Encoding Metadata**: Includes encoding information for client processing

```python
# Robust client configuration retrieval
config = await vpc_manager.get_vpn_server_client_configuration('vpn-server-id', 'us-south')

# Response format:
{
    "vpn_server_id": "vpn-server-id",
    "region": "us-south", 
    "client_configuration_content": "client\ndev tun\nproto udp\n...",
    "metadata": {
        "content_type": "openvpn_configuration",
        "encoding": "utf-8",
        "description": "OpenVPN client configuration file content"
    }
}
```

#### Client Management
```python
# List connected clients with sorting and pagination
clients = await vpc_manager.list_vpn_server_clients(
    'vpn-server-id', 
    'us-south',
    limit=25,
    sort='created_at'
)

# Response includes comprehensive client information
{
    "clients": [
        {
            "id": "client-1",
            "common_name": "user1.example.com",
            "username": "user1", 
            "status": "connected",
            "client_ip": "10.240.0.4",
            "created_at": "2023-01-01T00:00:00Z",
            "connected_at": "2023-01-01T10:00:00Z",
            "region": "us-south",
            "vpn_server_id": "vpn-server-id"
        }
    ],
    "count": 1,
    "total_count": 15,
    "limit": 25
}
```

### MCP Tools Integration
All VPN functionality is exposed through MCP tools with comprehensive JSON schemas:

#### VPN Gateway Tools (vpc_mcp_server.py:760-926)
- `list_vpn_gateways`: With vpc_id filtering and pagination support
- `get_vpn_gateway`: Detailed gateway information retrieval
- `get_ike_policy`: IKE policy configuration details  
- `get_ipsec_policy`: IPsec policy configuration details

#### VPN Server Tools (vpc_mcp_server.py:803-956)
- `list_vpn_servers`: With name filtering and pagination support
- `get_vpn_server`: Enhanced with authentication method extraction
- `get_vpn_server_client_configuration`: Robust client config with encoding handling
- `list_vpn_server_clients`: Client management with sorting (created_at, common_name, etc.)
- `list_vpn_server_routes`: Routing configuration management

### Testing Coverage
Comprehensive unit tests added (test_utils.py:527-1047):
- **22 VPN-related tests** covering all methods and error conditions
- **Mock-based testing** following established patterns
- **Binary data handling** tests for client configurations
- **Authentication method** extraction validation
- **Pagination and sorting** functionality testing
- **API exception handling** for all VPN operations

### Error Handling and Serialization
- **Robust JSON serialization** for client configurations containing certificates
- **Binary data support** with automatic base64 encoding when needed
- **UTF-8 encoding validation** with graceful fallback to character replacement
- **Structured error responses** with client-safe messaging
- **Regional context preservation** across all VPN operations

## Recent Session Changes Summary

### Major Features Added
1. **Complete VPN Gateway Support**: List, get details, and policy management
2. **Comprehensive VPN Server Management**: Server details, client configuration, client listing, routing
3. **Enhanced Authentication Detection**: Automatic extraction and summarization of VPN server authentication methods
4. **Robust Configuration Handling**: Proper serialization of OpenVPN client configurations with certificate data
5. **Client Management**: Full CRUD operations for VPN server clients with advanced filtering

### Files Modified
- **`utils.py`**: Added 9 new VPN-related methods (lines 920-1137)
- **`vpc_mcp_server.py`**: Added 9 new MCP tools and handlers (lines 760-1189)
- **`test_utils.py`**: Added 22 comprehensive unit tests (lines 527-1047) 
- **`README.md`**: Updated with VPN tool documentation and usage examples
- **`CLAUDE.md`**: Enhanced with complete VPN development patterns and usage

### Key Technical Improvements
- **Serialization Fix**: Resolved 'Response' object attribute errors in client configuration
- **Authentication Enhancement**: Added automatic authentication method detection and summarization
- **Data Format Handling**: Proper handling of string vs binary responses from IBM Cloud API
- **Error Recovery**: Graceful handling of encoding issues and API exceptions
- **Performance**: Efficient pagination and filtering for large VPN client lists