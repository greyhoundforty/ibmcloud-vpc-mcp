"""
IBM Cloud VPC UI Server
Provides interactive world map UI for IBM Cloud VPC regions using MCP-UI
"""

import json
import logging
import asyncio
import argparse
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# MCP and UI imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool

# Local imports
from utils import VPCManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import os

logger = logging.getLogger(__name__)

@dataclass
class RegionInfo:
    """IBM Cloud VPC Region information with geographic data"""
    code: str
    name: str
    country: str
    continent: str
    lat: float
    lng: float
    zones: List[str]

class VPCUIServer:
    """Manages IBM Cloud VPC UI resources and interactions"""
    
    # City to coordinates mapping for IBM Cloud regions
    CITY_COORDINATES = {
        # Known IBM Cloud VPC regions
        "Dallas": {"lat": 32.7767, "lng": -96.7970, "country": "United States", "continent": "North America"},
        "Washington DC": {"lat": 38.9072, "lng": -77.0369, "country": "United States", "continent": "North America"},
        "São Paulo": {"lat": -23.5558, "lng": -46.6396, "country": "Brazil", "continent": "South America"},
        "London": {"lat": 51.5074, "lng": -0.1278, "country": "United Kingdom", "continent": "Europe"},
        "Frankfurt": {"lat": 50.1109, "lng": 8.6821, "country": "Germany", "continent": "Europe"},
        "Sydney": {"lat": -33.8688, "lng": 151.2093, "country": "Australia", "continent": "Australia/Oceania"},
        
        # Additional known cities for other IBM Cloud regions
        "Toronto": {"lat": 43.6532, "lng": -79.3832, "country": "Canada", "continent": "North America"},
        "Montreal": {"lat": 45.5017, "lng": -73.5673, "country": "Canada", "continent": "North America"},
        "Tokyo": {"lat": 35.6762, "lng": 139.6503, "country": "Japan", "continent": "Asia"},
        "Osaka": {"lat": 34.6937, "lng": 135.5023, "country": "Japan", "continent": "Asia"},
        "Seoul": {"lat": 37.5665, "lng": 126.9780, "country": "South Korea", "continent": "Asia"},
        "Chennai": {"lat": 13.0827, "lng": 80.2707, "country": "India", "continent": "Asia"},
        "Madrid": {"lat": 40.4168, "lng": -3.7038, "country": "Spain", "continent": "Europe"},
        
        # Default fallback coordinates for common region patterns with display names
        "us-south": {"lat": 32.7767, "lng": -96.7970, "country": "United States", "continent": "North America", "display_name": "Dallas"},
        "us-east": {"lat": 38.9072, "lng": -77.0369, "country": "United States", "continent": "North America", "display_name": "Washington DC"},
        "br-sao": {"lat": -23.5558, "lng": -46.6396, "country": "Brazil", "continent": "South America", "display_name": "São Paulo"},
        "eu-gb": {"lat": 51.5074, "lng": -0.1278, "country": "United Kingdom", "continent": "Europe", "display_name": "London"},
        "eu-de": {"lat": 50.1109, "lng": 8.6821, "country": "Germany", "continent": "Europe", "display_name": "Frankfurt"},
        "au-syd": {"lat": -33.8688, "lng": 151.2093, "country": "Australia", "continent": "Australia/Oceania", "display_name": "Sydney"},
        "ca-tor": {"lat": 43.6532, "lng": -79.3832, "country": "Canada", "continent": "North America", "display_name": "Toronto"},
        "ca-mon": {"lat": 45.5017, "lng": -73.5673, "country": "Canada", "continent": "North America", "display_name": "Montreal"},
        "jp-tok": {"lat": 35.6762, "lng": 139.6503, "country": "Japan", "continent": "Asia", "display_name": "Tokyo"},
        "jp-osa": {"lat": 34.6937, "lng": 135.5023, "country": "Japan", "continent": "Asia", "display_name": "Osaka"},
        "kr-seo": {"lat": 37.5665, "lng": 126.9780, "country": "South Korea", "continent": "Asia", "display_name": "Seoul"},
        "in-che": {"lat": 13.0827, "lng": 80.2707, "country": "India", "continent": "Asia", "display_name": "Chennai"},
        "eu-es": {"lat": 40.4168, "lng": -3.7038, "country": "Spain", "continent": "Europe", "display_name": "Madrid"},
    }
    
    def __init__(self, vpc_manager: Optional[VPCManager] = None):
        self.vpc_manager = vpc_manager
        self.regions_cache = None
        
    async def fetch_regions_from_api(self) -> List[RegionInfo]:
        """Fetch regions from IBM Cloud VPC API and enrich with coordinates"""
        if not self.vpc_manager:
            logger.warning("No VPC manager available, using fallback regions")
            return self._get_fallback_regions()
            
        try:
            # Fetch regions from API
            regions_response = await self.vpc_manager.list_regions()
            api_regions = regions_response.get('regions', [])
            
            enriched_regions = []
            for region in api_regions:
                region_code = region.get('name', '')
                region_display_name = region.get('display_name', region_code)
                
                # Try to get coordinates from our mapping
                coords = self._get_coordinates_for_region(region_code, region_display_name)
                
                # Extract zones if available
                zones = []
                if 'zones' in region:
                    zones = [zone.get('name', '') for zone in region.get('zones', [])]
                else:
                    # Generate likely zone names based on pattern
                    zones = [f"{region_code}-{i}" for i in range(1, 4)]
                
                region_info = RegionInfo(
                    code=region_code,
                    name=coords.get('display_name', region_display_name),
                    country=coords.get('country', 'Unknown'),
                    continent=coords.get('continent', 'Unknown'),
                    lat=coords.get('lat', 0.0),
                    lng=coords.get('lng', 0.0),
                    zones=zones
                )
                enriched_regions.append(region_info)
                
            logger.info(f"Fetched {len(enriched_regions)} regions from API")
            return enriched_regions
            
        except Exception as e:
            logger.error(f"Failed to fetch regions from API: {e}")
            return self._get_fallback_regions()
    
    def _get_coordinates_for_region(self, region_code: str, display_name: str) -> Dict[str, Any]:
        """Get coordinates for a region based on code or display name"""
        # Try region code first
        if region_code in self.CITY_COORDINATES:
            coords = self.CITY_COORDINATES[region_code]
            return {**coords, 'display_name': display_name}
        
        # Try display name
        if display_name in self.CITY_COORDINATES:
            coords = self.CITY_COORDINATES[display_name]
            return {**coords, 'display_name': display_name}
        
        # Try to extract city name from display name patterns
        city_patterns = [
            display_name.split(' ')[0],  # First word
            display_name.split(',')[0] if ',' in display_name else display_name,  # Before comma
        ]
        
        for pattern in city_patterns:
            if pattern in self.CITY_COORDINATES:
                coords = self.CITY_COORDINATES[pattern]
                return {**coords, 'display_name': display_name}
        
        # Default fallback - center of map
        logger.warning(f"No coordinates found for region {region_code} ({display_name})")
        return {
            'lat': 0.0,
            'lng': 0.0,
            'country': 'Unknown',
            'continent': 'Unknown',
            'display_name': display_name
        }
    
    def _get_fallback_regions(self) -> List[RegionInfo]:
        """Get fallback regions when API is not available"""
        return [
            RegionInfo(
                code="us-south", name="Dallas", country="United States", 
                continent="North America", lat=32.7767, lng=-96.7970,
                zones=["us-south-1", "us-south-2", "us-south-3"]
            ),
            RegionInfo(
                code="us-east", name="Washington DC", country="United States",
                continent="North America", lat=38.9072, lng=-77.0369,
                zones=["us-east-1", "us-east-2", "us-east-3"]
            ),
            RegionInfo(
                code="br-sao", name="São Paulo", country="Brazil",
                continent="South America", lat=-23.5558, lng=-46.6396,
                zones=["br-sao-1", "br-sao-2", "br-sao-3"]
            ),
            RegionInfo(
                code="eu-gb", name="London", country="United Kingdom",
                continent="Europe", lat=51.5074, lng=-0.1278,
                zones=["eu-gb-1", "eu-gb-2", "eu-gb-3"]
            ),
            RegionInfo(
                code="eu-de", name="Frankfurt", country="Germany",
                continent="Europe", lat=50.1109, lng=8.6821,
                zones=["eu-de-1", "eu-de-2", "eu-de-3"]
            ),
            RegionInfo(
                code="au-syd", name="Sydney", country="Australia",
                continent="Australia/Oceania", lat=-33.8688, lng=151.2093,
                zones=["au-syd-1", "au-syd-2", "au-syd-3"]
            )
        ]
    
    async def get_regions(self) -> List[RegionInfo]:
        """Get regions (cached or fetch from API)"""
        if self.regions_cache is None:
            self.regions_cache = await self.fetch_regions_from_api()
        return self.regions_cache
        
    async def create_world_map_html(self) -> str:
        """Create interactive world map HTML with IBM Cloud regions"""
        
        # Get regions from API or fallback
        regions = await self.get_regions()
        
        # Convert regions to JavaScript-friendly format
        regions_js = json.dumps([
            {
                "code": r.code,
                "name": r.name,
                "country": r.country,
                "continent": r.continent,
                "lat": r.lat,
                "lng": r.lng,
                "zones": r.zones
            }
            for r in regions
        ], indent=2)
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IBM Cloud VPC Regions Map</title>
    
    <!-- Plotly.js CDN -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
            color: #ffffff;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        h1 {{
            text-align: center;
            color: #4fc3f7;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 2px 4px rgba(79, 195, 247, 0.3);
        }}
        
        .map-container {{
            background: #262626;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .map-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(45deg, rgba(79, 195, 247, 0.05) 0%, rgba(79, 195, 247, 0.1) 100%);
            pointer-events: none;
        }}
        
        #worldMap {{
            width: 100%;
            height: 600px;
            border-radius: 10px;
            background: #1a1a1a;
            position: relative;
        }}
        
        .region-marker {{
            position: absolute;
            width: 20px;
            height: 20px;
            background: linear-gradient(135deg, #4fc3f7 0%, #29b6f6 100%);
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(79, 195, 247, 0.4);
            border: 3px solid rgba(255, 255, 255, 0.8);
            z-index: 10;
        }}
        
        .region-marker:hover {{
            transform: scale(1.3);
            background: linear-gradient(135deg, #29b6f6 0%, #0288d1 100%);
            box-shadow: 0 6px 25px rgba(79, 195, 247, 0.6);
        }}
        
        .region-marker::after {{
            content: '';
            position: absolute;
            top: -5px;
            left: -5px;
            right: -5px;
            bottom: -5px;
            border: 2px solid rgba(79, 195, 247, 0.3);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{
                transform: scale(1);
                opacity: 1;
            }}
            100% {{
                transform: scale(1.5);
                opacity: 0;
            }}
        }}
        
        .region-label {{
            position: absolute;
            bottom: -35px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.8);
            color: #4fc3f7;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s ease;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(79, 195, 247, 0.3);
        }}
        
        .region-marker:hover .region-label {{
            opacity: 1;
        }}
        
        .continent {{
            fill: #334155;
            stroke: #475569;
            stroke-width: 1;
            opacity: 0.8;
            transition: all 0.3s ease;
        }}
        
        .continent:hover {{
            fill: #3f4b5c;
            opacity: 1;
        }}
        
        .info-panel {{
            margin-top: 30px;
            background: rgba(38, 38, 38, 0.8);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(79, 195, 247, 0.2);
        }}
        
        .region-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .region-card {{
            background: rgba(79, 195, 247, 0.1);
            border: 1px solid rgba(79, 195, 247, 0.3);
            border-radius: 8px;
            padding: 15px;
            transition: all 0.3s ease;
            cursor: pointer;
        }}
        
        .region-card:hover {{
            background: rgba(79, 195, 247, 0.2);
            transform: translateY(-2px);
        }}
        
        .region-card h3 {{
            margin: 0 0 10px 0;
            color: #4fc3f7;
            font-size: 1.1em;
        }}
        
        .region-card p {{
            margin: 5px 0;
            font-size: 0.9em;
            color: #b0bec5;
        }}
        
        /* Popup styles */
        .popup-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        
        .popup {{
            background: linear-gradient(135deg, #263238 0%, #37474f 100%);
            border-radius: 15px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(79, 195, 247, 0.3);
            position: relative;
            animation: popupSlideIn 0.3s ease-out;
        }}
        
        @keyframes popupSlideIn {{
            from {{
                transform: scale(0.8) translateY(-20px);
                opacity: 0;
            }}
            to {{
                transform: scale(1) translateY(0);
                opacity: 1;
            }}
        }}
        
        .popup h2 {{
            margin: 0 0 20px 0;
            color: #4fc3f7;
            font-size: 1.8em;
            text-align: center;
        }}
        
        .popup-close {{
            position: absolute;
            top: 15px;
            right: 20px;
            background: none;
            border: none;
            color: #4fc3f7;
            font-size: 24px;
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }}
        
        .popup-close:hover {{
            background: rgba(79, 195, 247, 0.1);
            transform: rotate(90deg);
        }}
        
        .region-details {{
            display: grid;
            gap: 15px;
        }}
        
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(79, 195, 247, 0.1);
        }}
        
        .detail-label {{
            font-weight: 600;
            color: #90caf9;
        }}
        
        .detail-value {{
            color: #ffffff;
        }}
        
        .zones-list {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .zone-tag {{
            background: rgba(79, 195, 247, 0.2);
            color: #4fc3f7;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            border: 1px solid rgba(79, 195, 247, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🌍 IBM Cloud VPC Regions</h1>
        
        <div class="map-container">
            <!-- Plotly map will be rendered here -->
            <div id="worldMap"></div>
        </div>
        
        <div class="info-panel">
            <h2>Available Regions</h2>
            <p>Click on any region marker on the map or select a region below to view details.</p>
            <div class="region-grid" id="regionGrid">
                <!-- Region cards will be populated by JavaScript -->
            </div>
        </div>
    </div>
    
    <!-- Popup overlay -->
    <div class="popup-overlay" id="popupOverlay">
        <div class="popup">
            <button class="popup-close" id="popupClose">&times;</button>
            <h2 id="popupTitle">Region Details</h2>
            <div class="region-details" id="regionDetails">
                <!-- Details will be populated by JavaScript -->
            </div>
        </div>
    </div>
    
    <script>
        // IBM Cloud VPC Regions data
        const regions = {regions_js};
        
        // Create Plotly world map with region markers
        function createPlotlyMap() {{
            // Prepare data for Plotly
            const latitudes = regions.map(r => r.lat);
            const longitudes = regions.map(r => r.lng);
            const regionNames = regions.map(r => r.name);
            const regionCodes = regions.map(r => r.code);
            const countries = regions.map(r => r.country);
            const continents = regions.map(r => r.continent);
            const zones = regions.map(r => r.zones.join(', '));
            
            // Create hover text with detailed information
            const hoverText = regions.map(r => 
                `<b>${{r.name}} (${{r.code}})</b><br>` +
                `📍 ${{r.country}}<br>` +
                `🌍 ${{r.continent}}<br>` +
                `🏢 Zones: ${{r.zones.join(', ')}}<br>` +
                `📐 ${{r.lat.toFixed(4)}}°, ${{r.lng.toFixed(4)}}°<br>` +
                `<i>Click for more details</i>`
            );
            
            // Create the scatter plot data
            const scatterData = {{
                type: 'scattergeo',
                lon: longitudes,
                lat: latitudes,
                text: regionNames,
                hovertext: hoverText,
                hoverinfo: 'text',
                customdata: regions,
                mode: 'markers+text',
                marker: {{
                    size: 15,
                    color: '#4fc3f7',
                    symbol: 'circle',
                    line: {{
                        color: '#ffffff',
                        width: 3
                    }},
                    opacity: 0.9
                }},
                textposition: 'bottom center',
                textfont: {{
                    size: 11,
                    color: '#4fc3f7',
                    family: 'Segoe UI, sans-serif'
                }}
            }};
            
            // Layout configuration
            const layout = {{
                title: {{
                    text: '',
                    font: {{ size: 16, color: '#4fc3f7' }}
                }},
                geo: {{
                    projection: {{ type: 'natural earth' }},
                    showland: true,
                    landcolor: '#2d3748',
                    oceancolor: '#1a202c',
                    showocean: true,
                    showcountries: true,
                    countrycolor: '#4a5568',
                    showlakes: true,
                    lakecolor: '#1a202c',
                    coastlinecolor: '#4a5568',
                    bgcolor: '#1a1a1a'
                }},
                paper_bgcolor: '#1a1a1a',
                plot_bgcolor: '#1a1a1a',
                font: {{ color: '#ffffff' }},
                margin: {{ l: 0, r: 0, t: 30, b: 0 }},
                height: 600
            }};
            
            // Configuration options
            const config = {{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: [
                    'pan2d', 'select2d', 'lasso2d', 'autoScale2d', 'hoverClosestGeo'
                ],
                modeBarButtonsToAdd: [{{
                    name: 'Reset View',
                    icon: Plotly.Icons.home,
                    click: function(gd) {{
                        Plotly.relayout(gd, {{
                            'geo.projection.scale': 1
                        }});
                    }}
                }}]
            }};
            
            // Create the plot
            Plotly.newPlot('worldMap', [scatterData], layout, config);
            
            // Add click event handler
            document.getElementById('worldMap').on('plotly_click', function(data) {{
                if (data.points && data.points.length > 0) {{
                    const point = data.points[0];
                    const region = point.customdata;
                    showRegionPopup(region);
                }}
            }});
        }}
        
        // Create region cards in the info panel
        function createRegionCards() {{
            const grid = document.getElementById('regionGrid');
            
            regions.forEach(region => {{
                const card = document.createElement('div');
                card.className = 'region-card';
                card.addEventListener('click', () => showRegionPopup(region));
                
                card.innerHTML = `
                    <h3>${{region.name}} (${{region.code}})</h3>
                    <p>📍 ${{region.country}}</p>
                    <p>🌍 ${{region.continent}}</p>
                    <p>🏢 ${{region.zones.length}} Availability Zones</p>
                `;
                
                grid.appendChild(card);
            }});
        }}
        
        // Show region popup with details
        function showRegionPopup(region) {{
            const overlay = document.getElementById('popupOverlay');
            const title = document.getElementById('popupTitle');
            const details = document.getElementById('regionDetails');
            
            title.textContent = `${{region.name}} (${{region.code}})`;
            
            details.innerHTML = `
                <div class="detail-row">
                    <span class="detail-label">Region Code:</span>
                    <span class="detail-value">${{region.code}}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Location:</span>
                    <span class="detail-value">${{region.name}}, ${{region.country}}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Continent:</span>
                    <span class="detail-value">${{region.continent}}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Coordinates:</span>
                    <span class="detail-value">${{region.lat.toFixed(4)}}°, ${{region.lng.toFixed(4)}}°</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Availability Zones:</span>
                    <div class="zones-list">
                        ${{region.zones.map(zone => `<span class="zone-tag">${{zone}}</span>`).join('')}}
                    </div>
                </div>
            `;
            
            overlay.style.display = 'flex';
        }}
        
        // Hide region popup
        function hideRegionPopup() {{
            const overlay = document.getElementById('popupOverlay');
            overlay.style.display = 'none';
        }}
        
        // Initialize the map
        document.addEventListener('DOMContentLoaded', () => {{
            createPlotlyMap();
            createRegionCards();
            
            // Set up popup close handlers
            document.getElementById('popupClose').addEventListener('click', hideRegionPopup);
            document.getElementById('popupOverlay').addEventListener('click', (e) => {{
                if (e.target === e.currentTarget) {{
                    hideRegionPopup();
                }}
            }});
            
            // ESC key to close popup
            document.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape') {{
                    hideRegionPopup();
                }}
            }});
        }});
    </script>
</body>
</html>
        """
        
        return html
    
    async def create_world_map_resource(self) -> Resource:
        """Create MCP UI resource for the world map"""
        html_content = await self.create_world_map_html()
        
        return Resource(
            uri="ui://vpc-regions/world-map",
            name="IBM Cloud VPC Regions Map",
            description="Interactive world map showing IBM Cloud VPC regions",
            mimeType="text/html",
            text=html_content
        )
    
    async def handle_region_click(self, region_code: str) -> Dict[str, Any]:
        """Handle region selection and return region info"""
        regions = await self.get_regions()
        regions_map = {r.code: r for r in regions}
        
        if region_code not in regions_map:
            return {"error": f"Unknown region: {region_code}"}
        
        region = regions_map[region_code]
        
        return {
            "region": {
                "code": region.code,
                "name": region.name,
                "country": region.country,
                "continent": region.continent,
                "coordinates": {"lat": region.lat, "lng": region.lng},
                "zones": region.zones
            },
            "message": f"Selected region: {region.name} ({region.code})"
        }

# MCP Server Setup
def create_mcp_server() -> Server:
    """Create MCP server with UI tools"""
    server = Server("vpc-ui-server")
    
    # Initialize UI server
    api_key = os.environ.get('IBMCLOUD_API_KEY')
    vpc_manager = None
    if api_key:
        authenticator = IAMAuthenticator(apikey=api_key)
        vpc_manager = VPCManager(authenticator)
    
    ui_server = VPCUIServer(vpc_manager)
    
    @server.list_resources()
    async def list_resources() -> List[Resource]:
        """List available UI resources"""
        return [await ui_server.create_world_map_resource()]
    
    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read UI resource content"""
        if uri == "ui://vpc-regions/world-map":
            return await ui_server.create_world_map_html()
        raise ValueError(f"Unknown resource: {uri}")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """List available tools"""
        return [
            Tool(
                name="show_vpc_regions_map",
                description="Display interactive world map of IBM Cloud VPC regions",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            ),
            Tool(
                name="select_region",
                description="Select a specific IBM Cloud VPC region",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region_code": {
                            "type": "string",
                            "description": "IBM Cloud VPC region code (e.g., 'us-south', 'eu-gb')"
                        }
                    },
                    "required": ["region_code"],
                    "additionalProperties": False
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Any]:
        """Handle tool calls"""
        if name == "show_vpc_regions_map":
            resource = await ui_server.create_world_map_resource()
            return [{"type": "resource", "resource": resource}]
        
        elif name == "select_region":
            region_code = arguments.get("region_code", "")
            result = await ui_server.handle_region_click(region_code)
            return [{"type": "text", "text": json.dumps(result, indent=2)}]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    return server

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="IBM Cloud VPC UI Server")
    parser.add_argument("--dev-mode", action="store_true", help="Run in development mode")
    args = parser.parse_args()
    
    # Set up logging
    log_level = os.environ.get('LOG_LEVEL', 'INFO' if not args.dev_mode else 'DEBUG')
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.dev_mode:
        logger.info("Starting VPC UI Server in development mode")
        # In dev mode, we could serve HTTP directly for testing
        api_key = os.environ.get('IBMCLOUD_API_KEY')
        vpc_manager = None
        if api_key:
            authenticator = IAMAuthenticator(apikey=api_key)
            vpc_manager = VPCManager(authenticator)
        
        ui_server = VPCUIServer(vpc_manager)
        html = await ui_server.create_world_map_html()
        
        # Save HTML to file for testing
        with open("/tmp/vpc_map.html", "w") as f:
            f.write(html)
        logger.info("Saved test HTML to /tmp/vpc_map.html")
        
        print("🗺️  VPC Regions Map HTML generated!")
        print("📁 Test file saved to: /tmp/vpc_map.html")
        print("🌐 Open the file in your browser to test the interactive map")
        
        # Show regions info
        regions = await ui_server.get_regions()
        print(f"📍 Found {len(regions)} regions:")
        for region in regions:
            print(f"  - {region.name} ({region.code}) - {region.country}")
        return
    
    # Run MCP server
    server = create_mcp_server()
    
    logger.info("Starting IBM Cloud VPC UI Server")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())