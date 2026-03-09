# IBM Cloud VPC MCP Server

An MCP server for IBM Cloud VPC resource management. Exposes VPC infrastructure — instances, networking, storage, VPN, flow logs, transit gateways, and more — as tools consumable by Claude Desktop or Claude Code.

## Prerequisites

- Docker
- IBM Cloud API key with VPC permissions

## Build

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
