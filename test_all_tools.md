# Test Commands for All MCP Tools

Run these commands in Claude Desktop to verify all tools are working correctly after container restart.

## 1. Basic VPC Operations

### List regions
```
Use the list_regions tool to show all available IBM Cloud VPC regions
```

### List VPCs
```
Use the list_vpcs tool to list VPCs in the us-south region with a limit of 3
```

### Get VPC details
```
Use the get_vpc tool to get details for the first VPC from the previous list
```

## 2. Network Resources

### List subnets
```
Use the list_subnets tool to list subnets in us-south region
```

### List instances
```
Use the list_instances tool to list compute instances in us-south region with limit 3
```

### List security groups
```
Use the list_security_groups tool to list security groups in us-south region
```

### Get security group details
```
Use the get_security_group tool to get details for the first security group from the previous list
```

## 3. Security Analysis

### SSH security analysis
```
Use the analyze_ssh_security_groups tool to find security groups with SSH access open to 0.0.0.0/0 in us-south region
```

### Protocol analysis
```
Use the analyze_security_groups_by_protocol tool to analyze security groups for TCP protocol on port 22 from 0.0.0.0/0 in us-south region
```

## 4. Storage Operations

### List volumes
```
Use the list_volumes tool to list block storage volumes in us-south region with limit 5
```

### List volume profiles
```
Use the list_volume_profiles tool to list available volume profiles in us-south region
```

### Analyze storage usage
```
Use the analyze_storage_usage tool to analyze block storage usage in us-south region
```

### List file shares
```
Use the list_shares tool to list file shares in us-south region with limit 5
```

## 5. Routing Tables (NEW)

### List routing tables
```
Use the list_routing_tables tool to list routing tables for the first VPC from step 1 in us-south region
```

### Get routing table details
```
Use the get_routing_table tool to get details for the first routing table from the previous list
```

### Find routing table by name (NEW)
```
Use the find_routing_table_by_name tool to find a routing table by name using the first VPC and the name from the routing table list
```

## 6. Snapshots (NEW)

### List snapshots
```
Use the list_snapshots tool to list block storage snapshots in us-south region with limit 5
```

### Get snapshot details
```
Use the get_snapshot tool to get details for the first snapshot from the previous list (if any exist)
```

### Analyze snapshot usage
```
Use the analyze_snapshot_usage tool to analyze snapshot usage in us-south region
```

## 7. Backup Operations

### List backup policies
```
Use the list_backup_policies tool to list backup policies in us-south region with limit 5
```

### Get backup policy summary
```
Use the get_backup_policy_summary tool to get comprehensive information about the first backup policy from the previous list (if any exist)
```

### Analyze backup policies
```
Use the analyze_backup_policies tool to analyze backup policies for health and compliance in us-south region
```

## 8. Comprehensive Analysis

### VPC resource summary
```
Use the get_vpc_resources_summary tool to get a complete summary of all resources in the first VPC from step 1 in us-south region
```

## Expected Results

- **All tools should return structured JSON responses**
- **Error responses should be graceful with clear error messages**
- **Empty results should show count: 0 rather than errors**
- **All tools should complete within reasonable time (< 30 seconds)**

## Quick Verification Commands

If you want to test everything quickly, use these essential commands:

1. `list_regions` - Basic connectivity test
2. `list_vpcs` with region us-south - Core VPC functionality
3. `list_routing_tables` with vpc_id from step 2 - New routing functionality
4. `find_routing_table_by_name` with vpc_id and name from step 3 - New lookup functionality
5. `list_snapshots` with region us-south - New snapshot functionality
6. `analyze_snapshot_usage` with region us-south - New analysis functionality

## Troubleshooting

If any tool fails:
1. Check the error message for specific details
2. Verify the container is running the latest image
3. Ensure IBMCLOUD_API_KEY environment variable is set
4. Check that you have the required IBM Cloud permissions
5. Try the tool with a different region if regional issues are suspected