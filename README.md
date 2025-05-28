# IBM Cloud VPC MCP Server

A Model Context Protocol (MCP) server that provides comprehensive IBM Cloud VPC resource management and security analysis capabilities. This server enables seamless interaction with IBM Cloud VPC infrastructure through a standardized protocol interface.

## 🚀 Features

### Core VPC Management
- **Multi-region Support**: List and manage VPCs across all IBM Cloud regions
- **Resource Discovery**: Comprehensive listing of VPCs, subnets, instances, and security groups
- **Instance Management**: View instance profiles, status, and network configurations
- **Network Infrastructure**: Manage public gateways, floating IPs, and network interfaces

### Security Analysis
- **SSH Exposure Detection**: Identify security groups with SSH access open to the internet (`0.0.0.0/0`)
- **Protocol-specific Analysis**: Analyze security groups for any protocol/port combination
- **Risk Assessment**: Built-in security rule risk analysis with threat categorization
- **Comprehensive Reporting**: Detailed security summaries for entire VPCs

### Enhanced Capabilities
- **Real-time Data**: Live data from IBM Cloud APIs with intelligent caching
- **Filtering Support**: Filter resources by VPC, region, or other criteria
- **Detailed Summaries**: Complete resource summaries with security analysis
- **Error Handling**: Robust error handling and logging

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

## 🎯 Usage Examples

### Security Analysis

**Find SSH exposure across all VPCs:**
```bash
# Check for SSH open to internet in us-south region
analyze_ssh_security_groups --region us-south

# Check specific VPC
analyze_ssh_security_groups --region us-south --vpc_id vpc-12345
```

**Custom protocol analysis:**
```bash
# Find RDP exposure
analyze_security_groups_by_protocol --region us-south --protocol tcp --port 3389

# Find database exposure  
analyze_security_groups_by_protocol --region us-south --protocol tcp --port 3306
```

### Resource Management

**List VPCs:**
```bash
# All regions
list_vpcs

# Specific region
list_vpcs --region us-south
```

**Get VPC summary:**
```bash
get_vpc_resources_summary --vpc_id vpc-12345 --region us-south
```

## 🐳 Docker Commands

### Using mise tasks:
```bash
# Build Docker image
mise run docker:build

# Run container
mise run docker:run

# Run in development mode
mise run docker:dev

# Stop and clean up
mise run docker:stop
mise run docker:clean
```

### Manual Docker commands:
```bash
# Build
docker build -t ibm-vpc-mcp:latest .

# Run
docker run -d --name vpc-mcp-server \
  -e IBMCLOUD_API_KEY="${IBMCLOUD_API_KEY}" \
  ibm-vpc-mcp:latest

# With docker-compose
docker-compose up -d
```

## 📊 MCP Tools Available

| Tool Name | Description |
|-----------|-------------|
| `list_regions` | List all IBM Cloud VPC regions |
| `list_vpcs` | List VPCs (all regions or specific) |
| `get_vpc` | Get detailed VPC information |
| `list_subnets` | List subnets with filtering |
| `list_instances` | List compute instances |
| `list_security_groups` | List security groups |
| `get_security_group` | Get detailed security group info |
| `list_security_group_rules` | List rules for specific security group |
| `analyze_ssh_security_groups` | Find SSH exposure to internet |
| `analyze_security_groups_by_protocol` | Custom protocol analysis |
| `list_floating_ips` | List floating IPs |
| `get_vpc_resources_summary` | Complete VPC resource summary |

## 🔒 Security Features

### Risk Detection
- **SSH Exposure**: Automatically detects SSH access from `0.0.0.0/0`
- **Wide Port Ranges**: Identifies overly permissive port ranges
- **Protocol Analysis**: Supports TCP, UDP, and ICMP analysis
- **Custom CIDR Matching**: Check exposure from specific IP ranges

### Security Levels
- **🔴 Critical**: All ports open to internet
- **🔴 High**: SSH, RDP, or databases exposed to internet  
- **🟡 Medium**: Wide port ranges or risky services
- **🟢 Low**: Properly restricted access

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │    │   MCP Server     │    │  IBM Cloud API  │
│                 │    │                  │    │                 │
│  - Claude       │◄──►│  - Tool Router   │◄──►│  - VPC Service  │
│  - Other Tools  │    │  - VPCManager    │    │  - Multi-region │
│                 │    │  - Utils         │    │  - Authentication│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Components
- **`vpc_mcp_server.py`**: MCP protocol handler and tool router
- **`utils.py`**: Core VPC management and security analysis logic
- **`VPCManager`**: Main class handling IBM Cloud API interactions
- **Docker**: Containerized deployment with health checks

## 🧪 Development

### Project Structure
```
├── vpc_mcp_server.py    # Main MCP server
├── utils.py             # VPC management utilities  
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yaml # Multi-service deployment
├── .mise.toml          # Development tasks
└── README.md           # This file
```

### Adding New Features

1. **Add new utilities** to `utils.py` in the `VPCManager` class
2. **Register MCP tools** in `vpc_mcp_server.py` 
3. **Update tests** and documentation
4. **Rebuild Docker image**

### Running Tests
```bash
# Test container
mise run docker:test

# Manual testing
docker run --rm -e IBMCLOUD_API_KEY="${IBMCLOUD_API_KEY}" \
  ibm-vpc-mcp:latest python -c "print('MCP Server Test')"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-analysis`
3. Make your changes in `utils.py` or `vpc_mcp_server.py`
4. Test with: `mise run docker:build && mise run docker:test`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Authentication Errors:**
```bash
# Verify API key
export IBMCLOUD_API_KEY="your-key"
ibmcloud iam api-key-get your-key-name
```

**Docker Issues:**
```bash
# Clean rebuild
mise run docker:clean
mise run docker:build
```

**Permission Errors:**
- Ensure API key has VPC Reader/Administrator permissions
- Check IBM Cloud IAM policies

### Getting Help

- **IBM Cloud VPC Documentation**: [https://cloud.ibm.com/docs/vpc](https://cloud.ibm.com/docs/vpc)
- **MCP Protocol**: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- **Issues**: Create an issue in this repository

## 🏷️ Version History

- **v1.0.0**: Initial release with basic VPC management
- **v1.1.0**: Added security analysis features
- **v1.2.0**: Enhanced Docker support and mise tasks
- **v1.3.0**: Multi-region support and comprehensive summaries

---

**Built with ❤️ for IBM Cloud VPC management and security analysis**