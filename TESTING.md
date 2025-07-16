# Testing Guide for IBM Cloud VPC MCP Server

This guide shows how to test the MCP server and storage tools **without restarting Claude Desktop**.

## Prerequisites

```bash
export IBMCLOUD_API_KEY="your-api-key-here"
```

## Testing Methods (Order by Speed)

### 1. Direct Python Testing (Fastest)

Test storage functions directly without MCP protocol:

```bash
# Install dependencies
mise run uv:reqs

# Run storage debug script
python test_storage_debug.py
```

This will test:
- `list_volumes()` in multiple regions
- `list_shares()` in multiple regions  
- `list_volume_profiles()` and `list_share_profiles()`
- Show detailed error messages and API responses

**Test new routing table and snapshot tools:**
```bash
# Test new tools specifically
python test_new_tools.py
```

This will test:
- `list_routing_tables()` and `get_routing_table()`
- `list_snapshots()` and `get_snapshot()`
- `analyze_snapshot_usage()`

### 2. MCP Protocol Testing (Recommended)

Test the full MCP protocol stack:

```bash
# Test MCP server with protocol
python test_mcp_client.py
```

This will:
- Start the MCP server process
- Initialize MCP protocol
- List available tools
- Test routing table and snapshot tools via MCP calls
- Show exact responses Claude Desktop would receive

### 3. Docker Testing (Most Realistic)

Test in the same environment as production:

```bash
# Build updated image
mise run docker:build

# Test container functionality
mise run docker:test

# Run storage debug in Docker
docker run --rm -e IBMCLOUD_API_KEY="$IBMCLOUD_API_KEY" \
  ibm-vpc-mcp:latest python test_storage_debug.py

# Interactive Docker testing
mise run docker:dev
```

### 4. Unit Testing

Run existing unit tests:

```bash
# Run all tests
python -m pytest

# Run storage-specific tests
python -m pytest test_utils.py::TestStorageManager -v

# Run integration tests (requires API key)
python -m pytest test_integration.py -m integration
```

## Quick Verification Commands

### Check Syntax
```bash
python -m py_compile vpc_mcp_server.py
python -m py_compile storage.py
```

### Test Imports
```bash
python -c "from storage import StorageManager; print('✅ Storage import OK')"
python -c "from vpc_mcp_server import VPCMCPServer; print('✅ MCP Server import OK')"
```

### Test Authentication
```bash
python -c "
import os
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from storage import StorageManager
auth = IAMAuthenticator(apikey=os.environ.get('IBMCLOUD_API_KEY'))
sm = StorageManager(None, auth)
print('✅ Authentication setup OK')
"
```

## Debugging Tips

### Enable Debug Logging
```bash
export LOG_LEVEL=DEBUG
python test_storage_debug.py
```

### Check API Response Structure
The debug script will show:
- API response keys
- Field availability
- Error details
- Response structure

### Common Issues & Solutions

**Import Errors**: Install dependencies
```bash
mise run uv:reqs
```

**API Key Issues**: 
```bash
echo $IBMCLOUD_API_KEY  # Should show your key
```

**Docker Issues**:
```bash
mise run docker:clean
mise run docker:build
```

## Testing Workflow

1. **Quick Check**: Run `python test_storage_debug.py`
2. **MCP Protocol**: Run `python test_mcp_client.py`  
3. **Docker Build**: Run `mise run docker:test`
4. **Update Claude Desktop**: Only after all tests pass

## Expected Output

### Successful Test
```
Testing region: us-south
==========================================
--- Testing list_volumes ---
Volumes result type: <class 'dict'>
Found 3 volumes
✅ list_volumes succeeded

--- Testing list_shares ---
Found 1 shares
✅ list_shares succeeded
```

### Error Output
```
--- Testing list_volumes ---
Error in volumes: 'status'
Exception in list_volumes: KeyError: 'status'
❌ Need to fix field access
```

## Integration with Claude Desktop

Once tests pass locally:

1. **Build Docker**: `mise run docker:build`
2. **Update Claude Desktop**: Restart the app
3. **Test in Claude**: Use the storage tools

The MCP protocol testing (`test_mcp_client.py`) shows exactly what Claude Desktop will receive, so if that works, Claude Desktop should work too.