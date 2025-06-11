"""
Unit tests for IBM Cloud VPC utilities
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from utils import (
    VPCManager, 
    create_vpc_manager, 
    analyze_security_rule_risk, 
    analyze_backup_policy_health
)
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException


class TestVPCManager:
    """Test cases for VPCManager class"""
    
    @pytest.fixture
    def mock_authenticator(self):
        """Create a mock IAM authenticator"""
        return Mock(spec=IAMAuthenticator)
    
    @pytest.fixture
    def vpc_manager(self, mock_authenticator):
        """Create a VPCManager instance with mocked authenticator"""
        return VPCManager(mock_authenticator)
    
    @pytest.fixture
    def mock_vpc_service(self):
        """Create a mock VPC service"""
        service = Mock()
        service.set_service_url = Mock()
        return service
    
    def test_init(self, mock_authenticator):
        """Test VPCManager initialization"""
        manager = VPCManager(mock_authenticator)
        assert manager.authenticator == mock_authenticator
        assert manager.vpc_clients == {}
        assert manager.regions == []
    
    @patch('utils.ibm_vpc.VpcV1')
    def test_get_vpc_client_new_region(self, mock_vpc_class, vpc_manager):
        """Test creating a new VPC client for a region"""
        mock_service = Mock()
        mock_vpc_class.return_value = mock_service
        
        client = vpc_manager._get_vpc_client('us-south')
        
        mock_vpc_class.assert_called_once_with(
            version='2025-04-08',
            authenticator=vpc_manager.authenticator
        )
        mock_service.set_service_url.assert_called_once_with(
            'https://us-south.iaas.cloud.ibm.com/v1'
        )
        assert vpc_manager.vpc_clients['us-south'] == mock_service
        assert client == mock_service
    
    @patch('utils.ibm_vpc.VpcV1')
    def test_get_vpc_client_cached_region(self, mock_vpc_class, vpc_manager):
        """Test retrieving cached VPC client"""
        mock_service = Mock()
        vpc_manager.vpc_clients['us-south'] = mock_service
        
        client = vpc_manager._get_vpc_client('us-south')
        
        mock_vpc_class.assert_not_called()
        assert client == mock_service
    
    @pytest.mark.asyncio
    async def test_list_regions_success(self, vpc_manager):
        """Test successful region listing"""
        mock_service = Mock()
        mock_response = {
            'regions': [
                {'name': 'us-south', 'status': 'available'},
                {'name': 'us-east', 'status': 'available'}
            ]
        }
        mock_service.list_regions.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_regions()
        
        assert result['count'] == 2
        assert len(result['regions']) == 2
        assert vpc_manager.regions == ['us-south', 'us-east']
    
    @pytest.mark.asyncio
    async def test_list_vpcs_single_region(self, vpc_manager):
        """Test listing VPCs in a single region"""
        mock_service = Mock()
        mock_response = {
            'vpcs': [
                {'id': 'vpc-1', 'name': 'test-vpc-1'},
                {'id': 'vpc-2', 'name': 'test-vpc-2'}
            ]
        }
        mock_service.list_vpcs.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_vpcs('us-south')
        
        assert result['count'] == 2
        assert len(result['vpcs']) == 2
        assert all(vpc['region'] == 'us-south' for vpc in result['vpcs'])
        assert result['regions_checked'] == ['us-south']
    
    @pytest.mark.asyncio
    async def test_list_vpcs_all_regions(self, vpc_manager):
        """Test listing VPCs across all regions"""
        vpc_manager.regions = ['us-south', 'us-east']
        
        mock_service = Mock()
        mock_response = {
            'vpcs': [{'id': 'vpc-1', 'name': 'test-vpc'}]
        }
        mock_service.list_vpcs.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_vpcs()
        
        assert result['count'] == 2  # One VPC per region
        assert result['regions_checked'] == ['us-south', 'us-east']
    
    @pytest.mark.asyncio
    async def test_list_vpcs_with_api_exception(self, vpc_manager):
        """Test handling API exceptions when listing VPCs"""
        vpc_manager.regions = ['us-south', 'us-east']
        
        def mock_get_client(region):
            service = Mock()
            if region == 'us-south':
                service.list_vpcs.return_value.get_result.return_value = {
                    'vpcs': [{'id': 'vpc-1', 'name': 'test-vpc'}]
                }
            else:
                service.list_vpcs.side_effect = ApiException(
                    message="Region not available", code=404
                )
            return service
        
        with patch.object(vpc_manager, '_get_vpc_client', side_effect=mock_get_client):
            result = await vpc_manager.list_vpcs()
        
        assert result['count'] == 1  # Only successful region
        assert result['vpcs'][0]['region'] == 'us-south'
    
    @pytest.mark.asyncio
    async def test_get_vpc_success(self, vpc_manager):
        """Test getting a specific VPC"""
        mock_service = Mock()
        mock_vpc = {'id': 'vpc-1', 'name': 'test-vpc', 'status': 'available'}
        mock_service.get_vpc.return_value.get_result.return_value = mock_vpc
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.get_vpc('vpc-1', 'us-south')
        
        mock_service.get_vpc.assert_called_once_with(id='vpc-1')
        assert result['region'] == 'us-south'
        assert result['id'] == 'vpc-1'
    
    @pytest.mark.asyncio
    async def test_list_subnets_with_vpc_filter(self, vpc_manager):
        """Test listing subnets filtered by VPC"""
        mock_service = Mock()
        mock_response = {
            'subnets': [
                {'id': 'subnet-1', 'vpc': {'id': 'vpc-1'}, 'available_ipv4_address_count': 250},
                {'id': 'subnet-2', 'vpc': {'id': 'vpc-2'}, 'available_ipv4_address_count': 100},
                {'id': 'subnet-3', 'vpc': {'id': 'vpc-1'}, 'available_ipv4_address_count': 200}
            ]
        }
        mock_service.list_subnets.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_subnets('us-south', vpc_id='vpc-1')
        
        assert result['count'] == 2  # Only subnets in vpc-1
        assert all(subnet['vpc']['id'] == 'vpc-1' for subnet in result['subnets'])
        assert result['vpc_filter'] == 'vpc-1'
    
    @pytest.mark.asyncio
    async def test_analyze_ssh_security_groups(self, vpc_manager):
        """Test SSH security group analysis"""
        mock_service = Mock()
        
        # Mock security groups response
        sg_response = {
            'security_groups': [
                {'id': 'sg-1', 'name': 'risky-sg', 'vpc': {'id': 'vpc-1'}},
                {'id': 'sg-2', 'name': 'safe-sg', 'vpc': {'id': 'vpc-1'}}
            ]
        }
        mock_service.list_security_groups.return_value.get_result.return_value = sg_response
        
        # Mock rules responses
        def mock_list_rules(security_group_id):
            if security_group_id == 'sg-1':
                # Risky rule: SSH from anywhere
                return Mock(get_result=lambda: {
                    'rules': [{
                        'id': 'rule-1',
                        'protocol': 'tcp',
                        'direction': 'inbound',
                        'port_min': 22,
                        'port_max': 22,
                        'remote': {'cidr_block': '0.0.0.0/0'}
                    }]
                })
            else:
                # Safe rule: SSH from specific IP
                return Mock(get_result=lambda: {
                    'rules': [{
                        'id': 'rule-2',
                        'protocol': 'tcp',
                        'direction': 'inbound',
                        'port_min': 22,
                        'port_max': 22,
                        'remote': {'cidr_block': '10.0.0.0/8'}
                    }]
                })
        
        mock_service.list_security_group_rules = mock_list_rules
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.analyze_ssh_security_groups('us-south', 'vpc-1')
        
        assert result['count'] == 1
        assert len(result['risky_security_groups']) == 1
        assert result['risky_security_groups'][0]['security_group_name'] == 'risky-sg'
        assert result['analysis_type'] == 'SSH access from 0.0.0.0/0'
    
    @pytest.mark.asyncio
    async def test_list_backup_policies_success(self, vpc_manager):
        """Test successful backup policy listing"""
        mock_service = Mock()
        mock_response = {
            'backup_policies': [
                {'id': 'policy-1', 'name': 'daily-backup'},
                {'id': 'policy-2', 'name': 'weekly-backup'}
            ]
        }
        mock_service.list_backup_policies.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_backup_policies('us-south', name='daily')
        
        mock_service.list_backup_policies.assert_called_once_with(
            start=None,
            limit=None,
            resource_group_id=None,
            name='daily',
            tag=None
        )
        assert result['count'] == 2
        assert all(policy['region'] == 'us-south' for policy in result['backup_policies'])
    
    @pytest.mark.asyncio
    async def test_get_vpc_resources_summary(self, vpc_manager):
        """Test VPC resources summary generation"""
        # Mock all the individual method calls
        with patch.object(vpc_manager, 'get_vpc') as mock_get_vpc, \
             patch.object(vpc_manager, 'list_subnets') as mock_list_subnets, \
             patch.object(vpc_manager, 'list_instances') as mock_list_instances, \
             patch.object(vpc_manager, 'list_security_groups') as mock_list_sg, \
             patch.object(vpc_manager, 'list_public_gateways') as mock_list_pg, \
             patch.object(vpc_manager, 'analyze_ssh_security_groups') as mock_analyze_ssh:
            
            # Setup mock returns
            mock_get_vpc.return_value = {
                'name': 'test-vpc', 'status': 'available', 'created_at': '2023-01-01T00:00:00Z'
            }
            mock_list_subnets.return_value = {
                'count': 2, 'subnets': [
                    {'zone': {'name': 'us-south-1'}},
                    {'zone': {'name': 'us-south-2'}}
                ]
            }
            mock_list_instances.return_value = {
                'count': 3, 'instances': [
                    {'status': 'running'},
                    {'status': 'running'},
                    {'status': 'stopped'}
                ]
            }
            mock_list_sg.return_value = {'count': 2}
            mock_list_pg.return_value = {'count': 1}
            mock_analyze_ssh.return_value = {
                'count': 1, 'risky_security_groups': [
                    {'security_group_name': 'risky-sg', 'security_group_id': 'sg-1'}
                ]
            }
            
            result = await vpc_manager.get_vpc_resources_summary('vpc-1', 'us-south')
        
        assert result['vpc_id'] == 'vpc-1'
        assert result['region'] == 'us-south'
        assert result['vpc_details']['name'] == 'test-vpc'
        assert result['resources']['subnets']['count'] == 2
        assert result['resources']['instances']['count'] == 3
        assert result['resources']['instances']['by_status']['running'] == 2
        assert result['resources']['instances']['by_status']['stopped'] == 1
        assert result['security_analysis']['ssh_open_to_internet']['risky_groups_count'] == 1


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    @pytest.mark.asyncio
    async def test_create_vpc_manager(self):
        """Test VPC manager creation with API key"""
        with patch('utils.IAMAuthenticator') as mock_auth_class:
            mock_authenticator = Mock()
            mock_auth_class.return_value = mock_authenticator
            
            manager = await create_vpc_manager('test-api-key')
            
            mock_auth_class.assert_called_once_with(apikey='test-api-key')
            assert isinstance(manager, VPCManager)
            assert manager.authenticator == mock_authenticator
    
    def test_analyze_security_rule_risk_high_risk(self):
        """Test security rule risk analysis for high-risk rule"""
        rule = {
            'id': 'rule-1',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 22,
            'port_max': 22,
            'remote': {'cidr_block': '0.0.0.0/0'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'high'
        assert 'Source allows traffic from anywhere (0.0.0.0/0)' in result['risk_factors']
        assert 'Exposes SSH (port 22)' in result['risk_factors']
        assert result['protocol'] == 'tcp'
        assert result['port_range'] == '22-22'
    
    def test_analyze_security_rule_risk_medium_risk(self):
        """Test security rule risk analysis for medium-risk rule"""
        rule = {
            'id': 'rule-2',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 3389,
            'port_max': 3389,
            'remote': {'cidr_block': '10.0.0.0/8'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'medium'
        assert 'Exposes RDP (port 3389)' in result['risk_factors']
        assert len(result['risk_factors']) == 1  # No 0.0.0.0/0 risk
    
    def test_analyze_security_rule_risk_low_risk(self):
        """Test security rule risk analysis for low-risk rule"""
        rule = {
            'id': 'rule-3',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 80,
            'port_max': 80,
            'remote': {'cidr_block': '10.0.0.0/8'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'low'
        assert len(result['risk_factors']) == 0
    
    def test_analyze_security_rule_risk_wide_port_range(self):
        """Test security rule risk analysis for wide port range"""
        rule = {
            'id': 'rule-4',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 1000,
            'port_max': 5000,
            'remote': {'cidr_block': '10.0.0.0/8'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'medium'
        assert 'Very wide port range (1000-5000)' in result['risk_factors']
    
    def test_analyze_backup_policy_health_healthy(self):
        """Test backup policy health analysis for healthy policy"""
        policy = {
            'id': 'policy-1',
            'lifecycle_state': 'stable'
        }
        
        jobs = [
            {'status': 'completed', 'created_at': '2023-12-01T00:00:00Z'},
            {'status': 'completed', 'created_at': '2023-11-30T00:00:00Z'},
            {'status': 'completed', 'created_at': '2023-11-29T00:00:00Z'}
        ]
        
        result = analyze_backup_policy_health(policy, jobs)
        
        assert result['status'] == 'healthy'
        assert result['health_score'] >= 80
        assert len(result['issues']) == 0
    
    def test_analyze_backup_policy_health_critical(self):
        """Test backup policy health analysis for critical policy"""
        policy = {
            'id': 'policy-2',
            'lifecycle_state': 'failed'
        }
        
        jobs = [
            {'status': 'failed', 'created_at': '2023-12-01T00:00:00Z'},
            {'status': 'failed', 'created_at': '2023-11-30T00:00:00Z'}
        ]
        
        result = analyze_backup_policy_health(policy, jobs)
        
        assert result['status'] == 'critical'
        assert result['health_score'] < 60
        assert any('failed state' in issue for issue in result['issues'])
        assert any('failure rate' in issue for issue in result['issues'])
    
    def test_analyze_backup_policy_health_no_jobs(self):
        """Test backup policy health analysis with no jobs"""
        policy = {
            'id': 'policy-3',
            'lifecycle_state': 'stable'
        }
        
        jobs = []
        
        result = analyze_backup_policy_health(policy, jobs)
        
        assert result['status'] == 'warning'
        assert 'No backup jobs found' in result['issues']
        assert 'Verify that backup schedules are active' in result['recommendations']


@pytest.fixture
def sample_vpc_data():
    """Sample VPC data for testing"""
    return {
        'vpcs': [
            {
                'id': 'vpc-1',
                'name': 'production-vpc',
                'status': 'available',
                'created_at': '2023-01-01T00:00:00Z'
            },
            {
                'id': 'vpc-2', 
                'name': 'development-vpc',
                'status': 'available',
                'created_at': '2023-01-02T00:00:00Z'
            }
        ]
    }


@pytest.fixture
def sample_security_group_data():
    """Sample security group data for testing"""
    return {
        'security_groups': [
            {
                'id': 'sg-1',
                'name': 'web-sg',
                'vpc': {'id': 'vpc-1'},
                'rules': [
                    {
                        'id': 'rule-1',
                        'protocol': 'tcp',
                        'direction': 'inbound',
                        'port_min': 80,
                        'port_max': 80,
                        'remote': {'cidr_block': '0.0.0.0/0'}
                    }
                ]
            }
        ]
    }


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_vpc_analysis_workflow(self, sample_vpc_data):
        """Test a complete VPC analysis workflow"""
        authenticator = Mock(spec=IAMAuthenticator)
        manager = VPCManager(authenticator)
        
        # Mock the service calls
        with patch.object(manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            
            # Setup mock responses
            mock_service.list_vpcs.return_value.get_result.return_value = sample_vpc_data
            mock_service.list_subnets.return_value.get_result.return_value = {'subnets': []}
            mock_service.list_instances.return_value.get_result.return_value = {'instances': []}
            
            # Test the workflow
            vpcs = await manager.list_vpcs('us-south')
            assert vpcs['count'] == 2
            
            for vpc in vpcs['vpcs']:
                subnets = await manager.list_subnets('us-south', vpc['id'])
                instances = await manager.list_instances('us-south', vpc['id'])
                
                assert 'subnets' in subnets
                assert 'instances' in instances
