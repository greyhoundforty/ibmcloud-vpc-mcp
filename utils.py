"""
IBM Cloud VPC Utilities
Provides VPC resource management functionality for IBM Cloud
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import ibm_vpc
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

logger = logging.getLogger(__name__)


class VPCManager:
    """Manages IBM Cloud VPC operations"""
    
    def __init__(self, authenticator: IAMAuthenticator):
        self.authenticator = authenticator
        self.vpc_clients = {}  # Cache VPC clients by region
        self.regions = []
        
    def _get_vpc_client(self, region: str) -> ibm_vpc.VpcV1:
        """Get or create VPC client for a specific region"""
        if region not in self.vpc_clients:
            service = ibm_vpc.VpcV1(
                version='2025-04-08',
                authenticator=self.authenticator
            )
            service.set_service_url(f'https://{region}.iaas.cloud.ibm.com/v1')
            self.vpc_clients[region] = service
        return self.vpc_clients[region]

    async def list_regions(self) -> Dict[str, Any]:
        """List all available regions"""
        # Use us-south to get region list
        service = self._get_vpc_client('us-south')
        response = service.list_regions().get_result()
        
        self.regions = [region['name'] for region in response['regions']]
        
        return {
            'regions': response['regions'],
            'count': len(response['regions'])
        }
    
    async def list_vpcs(self, region: Optional[str] = None) -> Dict[str, Any]:
        """List VPCs in specified region or all regions"""
        all_vpcs = []
        
        if region:
            regions_to_check = [region]
        else:
            # Get all regions if not cached
            if not self.regions:
                await self.list_regions()
            regions_to_check = self.regions
        
        for region_name in regions_to_check:
            try:
                service = self._get_vpc_client(region_name)
                response = service.list_vpcs().get_result()
                
                for vpc in response['vpcs']:
                    vpc['region'] = region_name
                    all_vpcs.append(vpc)
                    
            except ApiException as e:
                logger.warning(f"Error listing VPCs in region {region_name}: {e}")
        
        return {
            'vpcs': all_vpcs,
            'count': len(all_vpcs),
            'regions_checked': regions_to_check
        }
    
    async def get_vpc(self, vpc_id: str, region: str) -> Dict[str, Any]:
        """Get details of a specific VPC"""
        service = self._get_vpc_client(region)
        vpc = service.get_vpc(id=vpc_id).get_result()
        vpc['region'] = region
        return vpc
    
    async def list_subnets(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List subnets in a region, optionally filtered by VPC"""
        service = self._get_vpc_client(region)
        response = service.list_subnets().get_result()
        
        subnets = response['subnets']
        
        # Filter by VPC if specified
        if vpc_id:
            subnets = [s for s in subnets if s['vpc']['id'] == vpc_id]
        
        # Add additional subnet details
        for subnet in subnets:
            subnet['region'] = region
            subnet['available_ipv4_address_count'] = subnet.get('available_ipv4_address_count', 0)
            subnet['total_ipv4_address_count'] = subnet.get('total_ipv4_address_count', 0)
            
        return {
            'subnets': subnets,
            'count': len(subnets),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def list_instances(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List compute instances"""
        service = self._get_vpc_client(region)
        response = service.list_instances().get_result()
        
        instances = response['instances']
        
        # Filter by VPC if specified
        if vpc_id:
            instances = [i for i in instances if i['vpc']['id'] == vpc_id]
        
        # Summarize instance data
        instance_summary = []
        for instance in instances:
            instance_summary.append({
                'id': instance['id'],
                'name': instance['name'],
                'status': instance['status'],
                'profile': instance['profile']['name'],
                'vpc': instance['vpc'],
                'zone': instance['zone']['name'],
                'primary_network_interface': {
                    'id': instance['primary_network_interface']['id'],
                    'primary_ipv4_address': instance['primary_network_interface'].get('primary_ipv4_address')
                },
                'created_at': instance['created_at']
            })
        
        return {
            'instances': instance_summary,
            'count': len(instance_summary),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def list_instance_profiles(self, region: str) -> Dict[str, Any]:
        """List available instance profiles"""
        service = self._get_vpc_client(region)
        response = service.list_instance_profiles().get_result()
        
        profiles = []
        for profile in response['profiles']:
            profiles.append({
                'name': profile['name'],
                'family': profile.get('family'),
                'vcpu_count': profile.get('vcpu_count'),
                'memory': profile.get('memory'),
                'network_interface_count': profile.get('network_interface_count'),
                'bandwidth': profile.get('bandwidth')
            })
        
        return {
            'profiles': profiles,
            'count': len(profiles),
            'region': region
        }
    
    async def list_public_gateways(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List public gateways"""
        service = self._get_vpc_client(region)
        response = service.list_public_gateways().get_result()
        
        gateways = response['public_gateways']
        
        # Filter by VPC if specified
        if vpc_id:
            gateways = [g for g in gateways if g['vpc']['id'] == vpc_id]
        
        return {
            'public_gateways': gateways,
            'count': len(gateways),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def list_security_groups(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List security groups"""
        service = self._get_vpc_client(region)
        response = service.list_security_groups().get_result()
        
        security_groups = response['security_groups']
        
        # Filter by VPC if specified
        if vpc_id:
            security_groups = [sg for sg in security_groups if sg['vpc']['id'] == vpc_id]
        
        # Summarize security groups
        sg_summary = []
        for sg in security_groups:
            sg_summary.append({
                'id': sg['id'],
                'name': sg['name'],
                'vpc': sg['vpc'],
                'rules_count': len(sg.get('rules', [])),
                'created_at': sg['created_at']
            })
        
        return {
            'security_groups': sg_summary,
            'count': len(sg_summary),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def get_security_group(self, security_group_id: str, region: str) -> Dict[str, Any]:
        """Get detailed information about a specific security group including rules"""
        service = self._get_vpc_client(region)
        response = service.get_security_group(id=security_group_id).get_result()
        response['region'] = region
        return response
    
    async def list_security_group_rules(self, security_group_id: str, region: str) -> Dict[str, Any]:
        """List all rules for a specific security group"""
        service = self._get_vpc_client(region)
        response = service.list_security_group_rules(security_group_id=security_group_id).get_result()
        
        return {
            'security_group_id': security_group_id,
            'rules': response['rules'],
            'count': len(response['rules']),
            'region': region
        }
    
    async def analyze_ssh_security_groups(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """Find security groups with SSH access open to 0.0.0.0/0"""
        service = self._get_vpc_client(region)
        
        # Get all security groups
        sg_response = service.list_security_groups().get_result()
        security_groups = sg_response['security_groups']
        
        # Filter by VPC if specified
        if vpc_id:
            security_groups = [sg for sg in security_groups if sg['vpc']['id'] == vpc_id]
        
        risky_groups = []
        
        for sg in security_groups:
            try:
                # Get rules for this security group
                rules_response = service.list_security_group_rules(security_group_id=sg['id']).get_result()
                rules = rules_response['rules']
                
                risky_rules = []
                for rule in rules:
                    # Check for SSH access from anywhere
                    if (rule.get('protocol') == 'tcp' and 
                        rule.get('direction') == 'inbound'):
                        
                        # Check if port 22 is included in the rule
                        port_min = rule.get('port_min', 0)
                        port_max = rule.get('port_max', 65535)
                        
                        if port_min <= 22 <= port_max:
                            # Check if source is 0.0.0.0/0
                            remote = rule.get('remote', {})
                            if (isinstance(remote, dict) and 
                                remote.get('cidr_block') == '0.0.0.0/0'):
                                risky_rules.append(rule)
                
                if risky_rules:
                    risky_groups.append({
                        'security_group_id': sg['id'],
                        'security_group_name': sg['name'],
                        'vpc': sg['vpc'],
                        'risky_rules': risky_rules,
                        'rule_count': len(risky_rules)
                    })
                    
            except ApiException as e:
                logger.warning(f"Error analyzing security group {sg['id']}: {e}")
        
        return {
            'risky_security_groups': risky_groups,
            'count': len(risky_groups),
            'region': region,
            'vpc_filter': vpc_id,
            'analysis_type': 'SSH access from 0.0.0.0/0'
        }
    
    async def analyze_security_groups_by_protocol(self, region: str, protocol: str, 
                                                 port: Optional[int] = None, 
                                                 source_cidr: str = '0.0.0.0/0',
                                                 vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze security groups for specific protocol/port combinations from a source CIDR"""
        service = self._get_vpc_client(region)
        
        # Get all security groups
        sg_response = service.list_security_groups().get_result()
        security_groups = sg_response['security_groups']
        
        # Filter by VPC if specified
        if vpc_id:
            security_groups = [sg for sg in security_groups if sg['vpc']['id'] == vpc_id]
        
        matching_groups = []
        
        for sg in security_groups:
            try:
                # Get rules for this security group
                rules_response = service.list_security_group_rules(security_group_id=sg['id']).get_result()
                rules = rules_response['rules']
                
                matching_rules = []
                for rule in rules:
                    # Check protocol and direction
                    if (rule.get('protocol') == protocol and 
                        rule.get('direction') == 'inbound'):
                        
                        # Check port if specified
                        if port is not None:
                            port_min = rule.get('port_min', 0)
                            port_max = rule.get('port_max', 65535)
                            
                            if not (port_min <= port <= port_max):
                                continue
                        
                        # Check source CIDR
                        remote = rule.get('remote', {})
                        if (isinstance(remote, dict) and 
                            remote.get('cidr_block') == source_cidr):
                            matching_rules.append(rule)
                
                if matching_rules:
                    matching_groups.append({
                        'security_group_id': sg['id'],
                        'security_group_name': sg['name'],
                        'vpc': sg['vpc'],
                        'matching_rules': matching_rules,
                        'rule_count': len(matching_rules)
                    })
                    
            except ApiException as e:
                logger.warning(f"Error analyzing security group {sg['id']}: {e}")
        
        analysis_desc = f"{protocol.upper()}"
        if port:
            analysis_desc += f" port {port}"
        analysis_desc += f" from {source_cidr}"
        
        return {
            'matching_security_groups': matching_groups,
            'count': len(matching_groups),
            'region': region,
            'vpc_filter': vpc_id,
            'analysis_type': analysis_desc,
            'criteria': {
                'protocol': protocol,
                'port': port,
                'source_cidr': source_cidr
            }
        }
    
    async def list_floating_ips(self, region: str) -> Dict[str, Any]:
        """List all floating IPs in a region"""
        service = self._get_vpc_client(region)
        response = service.list_floating_ips().get_result()
        
        return {
            'floating_ips': response['floating_ips'],
            'count': len(response['floating_ips']),
            'region': region
        }
    
    async def get_vpc_resources_summary(self, vpc_id: str, region: str) -> Dict[str, Any]:
        """Get a comprehensive summary of all resources in a VPC"""
        summary = {
            'vpc_id': vpc_id,
            'region': region,
            'timestamp': datetime.now().isoformat(),
            'resources': {}
        }
        
        # Get VPC details
        try:
            vpc = await self.get_vpc(vpc_id, region)
            summary['vpc_details'] = {
                'name': vpc['name'],
                'status': vpc['status'],
                'created_at': vpc['created_at']
            }
        except Exception as e:
            summary['vpc_details'] = {'error': str(e)}
        
        # Count subnets
        try:
            subnets_data = await self.list_subnets(region, vpc_id)
            summary['resources']['subnets'] = {
                'count': subnets_data['count'],
                'zones': list(set(s['zone']['name'] for s in subnets_data['subnets']))
            }
        except Exception as e:
            summary['resources']['subnets'] = {'error': str(e)}
        
        # Count instances
        try:
            instances_data = await self.list_instances(region, vpc_id)
            summary['resources']['instances'] = {
                'count': instances_data['count'],
                'by_status': {}
            }
            for instance in instances_data['instances']:
                status = instance['status']
                summary['resources']['instances']['by_status'][status] = \
                    summary['resources']['instances']['by_status'].get(status, 0) + 1
        except Exception as e:
            summary['resources']['instances'] = {'error': str(e)}
        
        # Count security groups
        try:
            sg_data = await self.list_security_groups(region, vpc_id)
            summary['resources']['security_groups'] = {
                'count': sg_data['count']
            }
        except Exception as e:
            summary['resources']['security_groups'] = {'error': str(e)}
        
        # Count public gateways
        try:
            pg_data = await self.list_public_gateways(region, vpc_id)
            summary['resources']['public_gateways'] = {
                'count': pg_data['count']
            }
        except Exception as e:
            summary['resources']['public_gateways'] = {'error': str(e)}
        
        # Analyze SSH security
        try:
            ssh_analysis = await self.analyze_ssh_security_groups(region, vpc_id)
            summary['security_analysis'] = {
                'ssh_open_to_internet': {
                    'risky_groups_count': ssh_analysis['count'],
                    'risky_groups': [
                        {
                            'name': group['security_group_name'],
                            'id': group['security_group_id']
                        } for group in ssh_analysis['risky_security_groups']
                    ]
                }
            }
        except Exception as e:
            summary['security_analysis'] = {'error': str(e)}
        
        return summary


# Convenience functions for backward compatibility and ease of use
async def create_vpc_manager(api_key: str) -> VPCManager:
    """Create a VPC manager instance with API key authentication"""
    authenticator = IAMAuthenticator(apikey=api_key)
    return VPCManager(authenticator)


def analyze_security_rule_risk(rule: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single security group rule for potential risks"""
    risk_factors = []
    risk_level = "low"
    
    if rule.get('direction') == 'inbound':
        # Check for overly permissive source
        remote = rule.get('remote', {})
        if isinstance(remote, dict) and remote.get('cidr_block') == '0.0.0.0/0':
            risk_factors.append("Source allows traffic from anywhere (0.0.0.0/0)")
            risk_level = "high"
        
        # Check for commonly attacked ports
        protocol = rule.get('protocol')
        port_min = rule.get('port_min', 0)
        port_max = rule.get('port_max', 65535)
        
        risky_ports = {
            22: "SSH",
            23: "Telnet",
            3389: "RDP",
            1433: "SQL Server",
            3306: "MySQL",
            5432: "PostgreSQL",
            21: "FTP",
            25: "SMTP"
        }
        
        for port, service in risky_ports.items():
            if port_min <= port <= port_max and protocol == 'tcp':
                risk_factors.append(f"Exposes {service} (port {port})")
                if port in [22, 23, 3389] and risk_level != "high":
                    risk_level = "medium"
        
        # Check for wide port ranges
        if port_max - port_min > 1000:
            risk_factors.append(f"Very wide port range ({port_min}-{port_max})")
            if risk_level == "low":
                risk_level = "medium"
    
    return {
        'rule_id': rule.get('id'),
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'protocol': rule.get('protocol'),
        'direction': rule.get('direction'),
        'port_range': f"{rule.get('port_min', 'any')}-{rule.get('port_max', 'any')}" if rule.get('port_min') else "all"
    }