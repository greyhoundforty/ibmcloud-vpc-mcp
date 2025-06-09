#!/usr/bin/env python3
# Author: Ryan Tiffany
# Copyright (c) 2023
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Storage module for IBM Cloud VPC MCP Server
Provides block storage and file storage management capabilities
"""

import logging
from typing import Dict, List, Any, Optional
import ibm_vpc
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Manages IBM Cloud VPC storage resources including block volumes and file shares
    """
    
    def __init__(self, vpc_service, authenticator):
        """Initialize with VPC service client and authenticator"""
        self.authenticator = authenticator
        self.vpc_clients = {}  # Cache VPC clients by region
    
    def _get_vpc_client(self, region: str):
        """Get or create VPC client for a specific region"""
        if region not in self.vpc_clients:
            import ibm_vpc
            service = ibm_vpc.VpcV1(version='2025-04-08',authenticator=self.authenticator)
            service.set_service_url(f'https://{region}.iaas.cloud.ibm.com/v1')
            self.vpc_clients[region] = service
        return self.vpc_clients[region]
    
    async def list_volumes(self, region: str, 
                          limit: Optional[int] = None,
                          attachment_state: Optional[str] = None,
                          encryption: Optional[str] = None,
                          name: Optional[str] = None,
                          operating_system_family: Optional[str] = None,
                          operating_system_architecture: Optional[str] = None,
                          tag: Optional[str] = None,
                          zone_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List block storage volumes in a region with optional filtering
        
        Parameters:
            region (str): Region name
            limit (int, optional): Maximum number of volumes to return
            attachment_state (str, optional): Filter by attachment state
            encryption (str, optional): Filter by encryption type
            name (str, optional): Filter by volume name
            operating_system_family (str, optional): Filter by OS family
            operating_system_architecture (str, optional): Filter by OS architecture
            tag (str, optional): Filter by tag
            zone_name (str, optional): Filter by zone name
            
        Returns:
            Dict with volumes list and metadata
        """
        try:
            service = self._get_vpc_client(region)
            
            # Build parameters dict, excluding None values
            params = {
                'limit': limit,
                'attachment_state': attachment_state,
                'encryption': encryption,
                'name': name,
                'operating_system.family': operating_system_family,
                'operating_system.architecture': operating_system_architecture,
                'tag': tag,
                'zone.name': zone_name
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            response = service.list_volumes(**params).get_result()
            
            # Extract and enhance volume information
            volumes = []
            for volume in response['volumes']:
                volume_info = {
                    'id': volume['id'],
                    'name': volume['name'],
                    'status': volume['status'],
                    'capacity': volume['capacity'],
                    'iops': volume['iops'],
                    'profile': {
                        'name': volume['profile']['name']
                    },
                    'encryption': volume.get('encryption'),
                    'zone': {
                        'name': volume['zone']['name']
                    },
                    'created_at': volume['created_at'],
                    'attachment_state': volume.get('attachment_state', 'unattached')
                }
                
                # Add attachment info if present
                if 'volume_attachments' in volume and volume['volume_attachments']:
                    attachments = []
                    for attachment in volume['volume_attachments']:
                        attachments.append({
                            'id': attachment['id'],
                            'instance': {
                                'id': attachment['instance']['id'],
                                'name': attachment.get('instance', {}).get('name', 'Unknown')
                            },
                            'type': attachment['type'],
                            'status': attachment['status']
                        })
                    volume_info['attachments'] = attachments
                
                volumes.append(volume_info)
            
            return {
                'volumes': volumes,
                'count': len(volumes),
                'region': region,
                'filters': {
                    'attachment_state': attachment_state,
                    'encryption': encryption,
                    'name': name,
                    'tag': tag,
                    'zone_name': zone_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing volumes in region {region}: {str(e)}")
            return {
                'error': str(e),
                'region': region,
                'volumes': [],
                'count': 0
            }
    
    async def list_volume_profiles(self, region: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        List available volume profiles in a region
        
        Parameters:
            region (str): Region name
            limit (int, optional): Maximum number of profiles to return
            
        Returns:
            Dict with volume profiles and metadata
        """
        try:
            service = self._get_vpc_client(region)
            
            params = {}
            if limit:
                params['limit'] = limit
                
            response = service.list_volume_profiles(**params).get_result()
            
            profiles = []
            for profile in response['profiles']:
                profile_info = {
                    'name': profile['name'],
                    'family': profile.get('family'),
                    'href': profile['href']
                }
                
                # Add performance details if available
                if 'performance' in profile:
                    profile_info['performance'] = {
                        'max_iops': profile['performance'].get('max_iops'),
                        'max_throughput': profile['performance'].get('max_throughput'),
                        'max_volume_size': profile['performance'].get('max_volume_size')
                    }
                
                profiles.append(profile_info)
            
            return {
                'profiles': profiles,
                'count': len(profiles),
                'region': region
            }
            
        except Exception as e:
            logger.error(f"Error listing volume profiles in region {region}: {str(e)}")
            return {
                'error': str(e),
                'region': region,
                'profiles': [],
                'count': 0
            }
    
    async def get_volume(self, volume_id: str, region: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific volume
        
        Parameters:
            volume_id (str): Volume ID
            region (str): Region name
            
        Returns:
            Dict with volume details
        """
        try:
            service = self._get_vpc_client(region)
            response = service.get_volume(id=volume_id).get_result()
            
            # Extract and enhance volume information
            volume_info = {
                'id': response['id'],
                'name': response['name'],
                'status': response['status'],
                'capacity': response['capacity'],
                'iops': response['iops'],
                'profile': {
                    'name': response['profile']['name']
                },
                'encryption': response.get('encryption'),
                'zone': {
                    'name': response['zone']['name']
                },
                'created_at': response['created_at'],
                'attachment_state': response.get('attachment_state', 'unattached'),
                'crn': response['crn'],
                'resource_group': response.get('resource_group', {}),
                'bootable': response.get('bootable', False),
                'bandwidth': response.get('bandwidth')
            }
            
            # Add attachment info if present
            if 'volume_attachments' in response and response['volume_attachments']:
                attachments = []
                for attachment in response['volume_attachments']:
                    attachments.append({
                        'id': attachment['id'],
                        'instance': {
                            'id': attachment['instance']['id'],
                            'name': attachment.get('instance', {}).get('name', 'Unknown')
                        },
                        'type': attachment['type'],
                        'status': attachment['status'],
                        'device': attachment.get('device', {})
                    })
                volume_info['attachments'] = attachments
            
            # Add tags if present
            if 'user_tags' in response:
                volume_info['user_tags'] = response['user_tags']
            
            return volume_info
            
        except Exception as e:
            logger.error(f"Error getting volume {volume_id} in region {region}: {str(e)}")
            return {
                'error': str(e),
                'volume_id': volume_id,
                'region': region
            }
    
    async def analyze_storage_usage(self, region: str) -> Dict[str, Any]:
        """
        Analyze storage usage in a region
        
        Parameters:
            region (str): Region name
            
        Returns:
            Dict with storage usage analysis
        """
        try:
            # Get all volumes in the region
            volumes_data = await self.list_volumes(region)
            
            if 'error' in volumes_data:
                return {
                    'error': volumes_data['error'],
                    'region': region
                }
            
            volumes = volumes_data['volumes']
            
            # Calculate storage usage statistics
            total_volumes = len(volumes)
            total_capacity_gb = sum(v['capacity'] for v in volumes)
            attached_volumes = sum(1 for v in volumes if v.get('attachment_state') == 'attached')
            unattached_volumes = total_volumes - attached_volumes
            
            # Group by profile
            profiles = {}
            for volume in volumes:
                profile_name = volume['profile']['name']
                if profile_name not in profiles:
                    profiles[profile_name] = {
                        'count': 0,
                        'total_capacity_gb': 0,
                        'total_iops': 0
                    }
                
                profiles[profile_name]['count'] += 1
                profiles[profile_name]['total_capacity_gb'] += volume['capacity']
                profiles[profile_name]['total_iops'] += volume['iops']
            
            # Group by zone
            zones = {}
            for volume in volumes:
                zone_name = volume['zone']['name']
                if zone_name not in zones:
                    zones[zone_name] = {
                        'count': 0,
                        'total_capacity_gb': 0
                    }
                
                zones[zone_name]['count'] += 1
                zones[zone_name]['total_capacity_gb'] += volume['capacity']
            
            return {
                'region': region,
                'timestamp': import_datetime_and_return_now_iso(),
                'summary': {
                    'total_volumes': total_volumes,
                    'total_capacity_gb': total_capacity_gb,
                    'attached_volumes': attached_volumes,
                    'unattached_volumes': unattached_volumes,
                    'attachment_percentage': round((attached_volumes / total_volumes) * 100, 2) if total_volumes > 0 else 0
                },
                'by_profile': profiles,
                'by_zone': zones
            }
            
        except Exception as e:
            logger.error(f"Error analyzing storage usage in region {region}: {str(e)}")
            return {
                'error': str(e),
                'region': region
            }

# Helper function to get current datetime in ISO format
def import_datetime_and_return_now_iso():
    from datetime import datetime
    return datetime.now().isoformat()
