# IBM Cloud VPC MCP Server

An MCP server for IBM Cloud VPC resource management. Exposes VPC infrastructure — instances, networking, storage, VPN, flow logs, transit gateways, and more — as tools consumable by Claude Desktop or Claude Code.

## Prerequisites

- Docker
- IBM Cloud API key with VPC permissions

## Build

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
docker build -t ibmcloud-vpc-mcp:latest .
```

Or with mise:

```bash
mise run build-container
```

## Configuration

The server requires one environment variable:

| Variable | Description | Required |
|----------|-------------|----------|
| `IBMCLOUD_API_KEY` | IBM Cloud API key | Yes |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | No |

## Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ibmcloud-vpc": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "IBMCLOUD_API_KEY",
        "ibmcloud-vpc-mcp:latest"
      ],
      "env": {
        "IBMCLOUD_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Claude Code

```bash
claude mcp add ibmcloud-vpc -- docker run --rm -i -e IBMCLOUD_API_KEY=your_api_key_here ibmcloud-vpc-mcp:latest
```

## Local Development

```bash
pip install -r requirements.txt
export IBMCLOUD_API_KEY="your_api_key_here"
python vpc_mcp_server.py
```

## License

MIT
