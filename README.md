# IBM Cloud VPC MCP Server

A Model Context Protocol (MCP) server that provides comprehensive IBM Cloud VPC resource management and security analysis capabilities. This server enables seamless interaction with IBM Cloud VPC infrastructure through a standardized protocol interface.

## 🚀 Features

### Core VPC Management
- **Multi-region Support**: List and manage VPCs across all IBM Cloud regions
- **Resource Discovery**: Comprehensive listing of VPCs, subnets, instances, and security groups
- **Instance Management**: View instance profiles, status, and network configurations
- **Network Infrastructure**: Manage public gateways, floating IPs, and network interfaces

### Enhanced Capabilities
- **Real-time Data**: Live data from IBM Cloud APIs with intelligent caching
- **Filtering Support**: Filter resources by VPC, region, or other criteria
- **Detailed Summaries**: Complete resource summaries with security analysis
- **Error Handling**: Robust error handling and logging

### Interactive UI (MCP-UI)
- **Regional VPC Graph**: `show_regional_vpc_graph` renders an interactive SVG world-map directly in MCP-UI-compatible hosts (e.g. Claude Desktop), showing every IBM Cloud region as a clickable node sized and coloured by VPC count
- **Live Data**: Each invocation fetches fresh VPC counts from all regions
- **MCP Apps standard**: Also exposes the graph as a readable MCP resource at `ui://ibm-vpc/regional-graph` for hosts that implement the MCP Apps `_meta.ui.resourceUri` pattern

## 🗺️ Regional VPC Graph

The `show_regional_vpc_graph` tool generates a self-contained interactive HTML visualisation, powered by the [`mcp-ui-server`](https://pypi.org/project/mcp-ui-server/) Python package.

### How it works

```
MCP Host (e.g. Claude Desktop)
   │
   │  1. Calls show_regional_vpc_graph
   ▼
IBM Cloud VPC MCP Server
   │  2. Fetches VPC list from every region concurrently via IBM VPC API
   │  3. Builds interactive SVG map HTML via vpc_ui.py
   │  4. Returns EmbeddedResource(mimeType="text/html", …)
   ▼
MCP Host renders the HTML inline
```

### Map features

| Feature | Detail |
|---------|--------|
| **Node colour** | Americas = blue · Europe = purple · Asia Pacific = green |
| **Node size** | Scales with VPC count (min 8 px, max 28 px radius) |
| **VPC count badge** | Shown inside each active region node |
| **Glow ring** | Appears on regions that have at least one VPC |
| **Side panel** | Click any region node to see region ID, geography, VPC count, and VPC names |
| **Legend** | Circle-size legend + geography colour key always visible |

### Supported regions

| Region ID | Location | Geography |
|-----------|----------|-----------|
| `us-south` | Dallas | Americas |
| `us-east` | Washington DC | Americas |
| `ca-tor` | Toronto | Americas |
| `ca-mon` | Montreal | Americas |
| `br-sao` | São Paulo | Americas |
| `eu-de` | Frankfurt | Europe |
| `eu-gb` | London | Europe |
| `eu-es` | Madrid | Europe |
| `eu-fr2` | Paris | Europe |
| `jp-tok` | Tokyo | Asia Pacific |
| `jp-osa` | Osaka | Asia Pacific |
| `au-syd` | Sydney | Asia Pacific |
| `in-che` | Chennai | Asia Pacific |

### MCP resource URI

For hosts that support the MCP Apps standard, the graph is also accessible as a named resource:

```
uri: ui://ibm-vpc/regional-graph
mimeType: text/html
```

Call `resources/read` with that URI to retrieve freshly-generated HTML without calling the tool directly.

### Key files

| File | Purpose |
|------|---------|
| `vpc_ui.py` | HTML generator, Mercator projection, `create_regional_graph_resource()` |
| `utils.py` | `VPCManager.get_regional_vpc_counts()` — fetches per-region VPC data |
| `vpc_mcp_server.py` | Tool definition, `list_resources`, `read_resource`, and `call_tool` handler |

## 📋 Prerequisites

- **IBM Cloud Account**: Active IBM Cloud account with VPC access
- **API Key**: IBM Cloud API key with VPC management permissions
- **Docker**: For containerized deployment
- **Python 3.12+**: For local development

## 🛠️ Installation

### Quick Start with Docker

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up environment:**
   ```bash
   # Create .env file
   echo "IBMCLOUD_API_KEY=your_api_key_here" > .env
   ```

3. **Build and run:**
   ```bash
   mise run docker:build
   mise run docker:run
   ```

### Local Development Setup

1. **Install dependencies:**
   ```bash
   mise install
   mise run uv:reqs
   ```

2. **Set environment variable:**
   ```bash
   export IBMCLOUD_API_KEY="your_api_key_here"
   ```

3. **Run locally:**
   ```bash
   python vpc_mcp_server.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `IBMCLOUD_API_KEY` | IBM Cloud API key with VPC permissions | ✅ |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | ❌ |
| `PYTHONUNBUFFERED` | Unbuffered Python output | ❌ |

### IBM Cloud API Key Setup

1. Go to [IBM Cloud API Keys](https://cloud.ibm.com/iam/apikeys)
2. Click **Create an API key**
3. Provide a name and description
4. Ensure the key has VPC access permissions
5. Copy the API key (save it securely - it won't be shown again)

## 🐳 Docker Commands

### Using mise tasks:
```bash
# Build Docker image with timestamp
mise run build-container

# Build and update Claude Desktop config
mise run build-and-update

# Quick rebuild
mise run rebuild

# Test container
mise run test-container
```

### Manual Docker commands:
```bash
# Build
docker build -t ibmcloud-vpc-mcp:latest .

# Run
docker run -d --name vpc-mcp-server \
  -e IBMCLOUD_API_KEY="${IBMCLOUD_API_KEY}" \
  ibmcloud-vpc-mcp:latest

# With docker-compose
docker-compose up -d
```

## 📊 Available MCP Tools

### Core VPC Operations
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_regions` | List all IBM Cloud VPC regions | None |
| `list_vpcs` | List VPCs (all regions or specific) | `region` (optional) |
| `get_vpc` | Get detailed VPC information | `vpc_id`, `region` |
| `get_vpc_resources_summary` | Complete VPC resource summary with security analysis | `vpc_id`, `region` |

### Network Resources
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_subnets` | List subnets with filtering | `region`, `vpc_id` (optional) |
| `list_instances` | List compute instances | `region`, `vpc_id` (optional) |
| `list_instance_profiles` | List available instance profiles | `region` |
| `list_public_gateways` | List public gateways | `region`, `vpc_id` (optional) |
| `list_floating_ips` | List floating IPs | `region` |

### Security Groups
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_security_groups` | List security groups | `region`, `vpc_id` (optional) |
| `get_security_group` | Get detailed security group info | `security_group_id`, `region` |
| `list_security_group_rules` | List rules for specific security group | `security_group_id`, `region` |

### Security Analysis
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `analyze_ssh_security_groups` | Find SSH exposure to internet (0.0.0.0/0) | `region`, `vpc_id` (optional) |
| `analyze_security_groups_by_protocol` | Custom protocol/port analysis | `region`, `protocol`, `port` (optional), `source_cidr` (optional) |

### Routing Tables
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_routing_tables` | List routing tables in a VPC | `region`, `vpc_id` (required) |
| `get_routing_table` | Get detailed routing table information | `vpc_id`, `routing_table_id`, `region` |
| `find_routing_table_by_name` | Find routing table by name and return UUID | `region`, `vpc_id`, `name` |

### Block Storage
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_volumes` | List block storage volumes | `region`, `attachment_state` (optional), `name` (optional) |
| `list_volume_profiles` | List available volume profiles | `region` |
| `get_volume` | Get detailed volume information | `volume_id`, `region` |
| `analyze_storage_usage` | Analyze block storage usage | `region` |

### File Storage
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_shares` | List file shares | `region`, `name` (optional), `resource_group_id` (optional) |
| `get_share` | Get detailed file share information | `share_id`, `region` |
| `list_share_profiles` | List available file share profiles | `region` |

### Snapshots
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_snapshots` | List block storage snapshots | `region`, `name` (optional), `source_volume_id` (optional) |
| `get_snapshot` | Get detailed snapshot information | `snapshot_id`, `region` |
| `analyze_snapshot_usage` | Analyze snapshot usage and costs | `region` |

### Backup Policies
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_backup_policies` | List backup policies | `region`, `name` (optional), `resource_group_id` (optional) |
| `list_backup_policy_jobs` | List jobs for a backup policy | `backup_policy_id`, `region`, `status` (optional) |
| `list_backup_policy_plans` | List plans for a backup policy | `backup_policy_id`, `region`, `name` (optional) |
| `get_backup_policy_summary` | Get comprehensive backup policy information | `backup_policy_id`, `region` |
| `analyze_backup_policies` | Analyze backup policy health and compliance | `region`, `resource_group_id` (optional) |

### VPN Gateway Management
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_vpn_gateways` | List VPN gateways with optional VPC filtering | `region`, `vpc_id` (optional), `limit` (optional), `start` (optional) |
| `get_vpn_gateway` | Get detailed VPN gateway information | `vpn_gateway_id`, `region` |
| `get_ike_policy` | Get IKE policy details for VPN gateways | `ike_policy_id`, `region` |
| `get_ipsec_policy` | Get IPsec policy details for VPN gateways | `ipsec_policy_id`, `region` |

### VPN Server Management
| Tool Name | Description | Key Parameters |
|-----------|-------------|----------------|
| `list_vpn_servers` | List VPN servers with optional name filtering | `region`, `name` (optional), `limit` (optional), `start` (optional) |
| `get_vpn_server` | Get detailed VPN server info including authentication methods | `vpn_server_id`, `region` |
| `get_vpn_server_client_configuration` | Get OpenVPN client configuration files | `vpn_server_id`, `region` |
| `list_vpn_server_clients` | List clients connected to a VPN server | `vpn_server_id`, `region`, `limit` (optional), `start` (optional), `sort` (optional) |
| `list_vpn_server_routes` | List routing configuration for VPN servers | `vpn_server_id`, `region`, `limit` (optional), `start` (optional) |

## 🎯 Usage Examples

### Basic VPC Discovery
```bash
# List all regions
list_regions

# List VPCs in specific region
list_vpcs --region us-south

# Get complete VPC summary
get_vpc_resources_summary --vpc_id vpc-12345 --region us-south
```

### Security Analysis
```bash
# Find SSH exposure across all VPCs
analyze_ssh_security_groups --region us-south

# Find RDP exposure
analyze_security_groups_by_protocol --region us-south --protocol tcp --port 3389

# Get detailed security group information
get_security_group --security_group_id sg-12345 --region us-south
```

### Routing Table Management
```bash
# List routing tables in a VPC
list_routing_tables --region us-south --vpc_id vpc-12345

# Find routing table by name
find_routing_table_by_name --region us-south --vpc_id vpc-12345 --name "main-routing-table"

# Get detailed routing table information
get_routing_table --vpc_id vpc-12345 --routing_table_id rt-12345 --region us-south
```

### Storage Management
```bash
# List all volumes
list_volumes --region us-south

# List snapshots
list_snapshots --region us-south

# Analyze storage usage
analyze_storage_usage --region us-south

# Analyze snapshot usage
analyze_snapshot_usage --region us-south
```

### Backup Policy Management
```bash
# List backup policies
list_backup_policies --region us-south

# Get backup policy summary
get_backup_policy_summary --backup_policy_id policy-12345 --region us-south

# Analyze backup policies
analyze_backup_policies --region us-south
```

### VPN Management
```bash
# List VPN gateways
list_vpn_gateways --region us-south

# List VPN gateways for specific VPC
list_vpn_gateways --region us-south --vpc_id vpc-12345

# Get VPN gateway details
get_vpn_gateway --vpn_gateway_id vpn-gateway-12345 --region us-south

# Get IKE/IPsec policy details
get_ike_policy --ike_policy_id ike-policy-12345 --region us-south
get_ipsec_policy --ipsec_policy_id ipsec-policy-12345 --region us-south

# List VPN servers
list_vpn_servers --region us-south

# Get VPN server details with authentication info
get_vpn_server --vpn_server_id vpn-server-12345 --region us-south

# Get OpenVPN client configuration
get_vpn_server_client_configuration --vpn_server_id vpn-server-12345 --region us-south

# List connected clients
list_vpn_server_clients --vpn_server_id vpn-server-12345 --region us-south

# List VPN server routes
list_vpn_server_routes --vpn_server_id vpn-server-12345 --region us-south
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-analysis`
3. Make your changes in `utils.py` or `vpc_mcp_server.py`
4. Test with: `mise run build-container && mise run test-container`
5. Submit a pull request

## 📚 Additional Resources

- **[CLAUDE.md](./debug/CLAUDE.md)**: Comprehensive development guide for Claude Code instances
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)**: Detailed troubleshooting guide
- **[test_all_tools.md](./debug/test_all_tools.md)**: Commands to test all tools after deployment

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏷️ Version History

- **v1.0.0**: Initial release with basic VPC management
- **v1.1.0**: Added security analysis features
- **v1.2.0**: Enhanced Docker support and mise tasks
- **v1.3.0**: Multi-region support and comprehensive summaries
- **v1.4.0**: Added backup policy management and analysis features
- **v1.5.0**: Added routing table lookup, snapshots, and improved storage tools
- **v1.6.0**: Comprehensive VPN management (gateways, servers, clients, policies, configuration)

---

**Built with ❤️ for IBM Cloud VPC management and security analysis**