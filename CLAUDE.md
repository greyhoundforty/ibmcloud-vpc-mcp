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