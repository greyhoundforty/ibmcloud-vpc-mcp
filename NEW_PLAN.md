# IBM Cloud VPC Interactive World Map Implementation Plan

## Overview
This plan outlines the implementation of an interactive world map using mcp-ui to display IBM Cloud VPC regions with clickable functionality for exploring VPCs within each region.

## Project Goals
1. Create an interactive geometric world map showing IBM Cloud VPC regions
2. Enable region-specific VPC exploration through click interactions
3. Integrate with existing IBM Cloud VPC MCP server tools
4. Provide a modern, geometric visual design

## Technical Architecture

### Core Components
1. **MCP-UI Integration**: Leverage mcp-ui server and client libraries for UI rendering
2. **Interactive Map**: SVG-based world map with geometric styling
3. **Region Integration**: Connect map regions to existing VPC management tools
4. **Data Layer**: IBM Cloud region and VPC data management

### Technology Stack
- **Backend**: Python (existing MCP server)
- **Frontend**: HTML/CSS/JavaScript with SVG
- **UI Framework**: mcp-ui (@mcp-ui/server, @mcp-ui/client)
- **Map Rendering**: Custom SVG with D3.js or similar for interactivity
- **Styling**: CSS3 with geometric design patterns

## Implementation Phases

### Phase 1: Environment Setup and Branch Management
**Branch**: `mcpui`
**Timeline**: 1-2 hours

#### Tasks:
1. Create new git branch `mcpui`
2. Add mise tasks for branch management
3. Install mcp-ui dependencies
4. Set up development environment

#### Deliverables:
- New git branch with clean working directory
- Updated `.mise.toml` with mcpui-specific tasks
- Package dependencies installed

### Phase 2: IBM Cloud Region Data Integration
**Timeline**: 2-3 hours

#### IBM Cloud VPC Regions Data:
```json
{
  "regions": [
    {
      "code": "us-south",
      "name": "Dallas",
      "country": "United States",
      "continent": "North America",
      "coordinates": { "lat": 32.7767, "lng": -96.7970 }
    },
    {
      "code": "us-east", 
      "name": "Washington DC",
      "country": "United States", 
      "continent": "North America",
      "coordinates": { "lat": 38.9072, "lng": -77.0369 }
    },
    {
      "code": "br-sao",
      "name": "São Paulo", 
      "country": "Brazil",
      "continent": "South America", 
      "coordinates": { "lat": -23.5558, "lng": -46.6396 }
    },
    {
      "code": "eu-gb",
      "name": "London",
      "country": "United Kingdom",
      "continent": "Europe",
      "coordinates": { "lat": 51.5074, "lng": -0.1278 }
    },
    {
      "code": "eu-de", 
      "name": "Frankfurt",
      "country": "Germany",
      "continent": "Europe",
      "coordinates": { "lat": 50.1109, "lng": 8.6821 }
    },
    {
      "code": "au-syd",
      "name": "Sydney", 
      "country": "Australia",
      "continent": "Australia/Oceania",
      "coordinates": { "lat": -33.8688, "lng": 151.2093 }
    }
  ]
}
```

#### Tasks:
1. Create `region_data.py` module with comprehensive region information
2. Extend VPCManager with region coordinate and metadata methods
3. Add MCP tools for region data retrieval
4. Create region-to-coordinate mapping utilities

#### Deliverables:
- Region data module with coordinates and metadata
- Enhanced VPCManager with geographic data support
- New MCP tools: `get_region_coordinates`, `list_regions_with_geo`

### Phase 3: World Map SVG Creation
**Timeline**: 4-5 hours

#### Design Requirements:
- **Geometric Style**: Low-poly, angular continent shapes
- **Color Scheme**: Modern, minimal palette with IBM Cloud brand colors
- **Interactive Elements**: Clickable region markers
- **Responsive Design**: Scalable SVG that works on different screen sizes

#### Map Features:
1. **Base Map**: Geometric world continents
2. **Region Markers**: Prominent markers for each IBM Cloud region
3. **Hover States**: Visual feedback on region hover
4. **Click Handlers**: JavaScript event handling for region selection
5. **Info Panels**: Dynamic information display for selected regions

#### Tasks:
1. Create base world map SVG with geometric styling
2. Add region markers with coordinate positioning
3. Implement hover and click interactions
4. Style with modern geometric design patterns
5. Add responsive CSS for different screen sizes

#### File Structure:
```
static/
├── css/
│   ├── map.css          # Map styling
│   └── geometric.css    # Geometric design system
├── js/
│   ├── map.js          # Map interactions
│   └── regions.js      # Region data handling
└── svg/
    └── world-map.svg   # Base geometric world map
```

### Phase 4: MCP-UI Integration
**Timeline**: 3-4 hours

#### MCP-UI Implementation:
1. **Server-Side**: Create UI resources using mcp-ui server library
2. **Client Rendering**: Implement UIResourceRenderer components
3. **Action Handling**: Set up two-way communication for map interactions
4. **Data Binding**: Connect map clicks to VPC data retrieval

#### Key Components:
```python
# vpc_ui_server.py - New UI server module
class VPCUIServer:
    def create_world_map_ui(self) -> UIResource:
        """Create interactive world map UI resource"""
        
    def handle_region_click(self, region_code: str) -> Dict[str, Any]:
        """Handle region selection and return VPC data"""
        
    def create_vpc_details_ui(self, region: str, vpcs: List[Dict]) -> UIResource:
        """Create VPC details UI for selected region"""
```

#### Tasks:
1. Create VPCUIServer class with UI resource management
2. Implement world map UI resource creation
3. Add region click handlers and VPC data integration
4. Create VPC details view for selected regions
5. Set up MCP tool integration for UI actions

#### Deliverables:
- VPCUIServer module with complete UI management
- Interactive world map as MCP UI resource
- Region-specific VPC detail views
- Integrated click-to-VPC-data workflow

### Phase 5: Enhanced User Interface
**Timeline**: 2-3 hours

#### UI Enhancements:
1. **Loading States**: Show loading indicators during data fetching
2. **Error Handling**: Graceful error display for API failures
3. **Data Visualization**: Charts and graphs for VPC statistics
4. **Search and Filter**: Tools for finding specific VPCs or resources
5. **Export Features**: Export region/VPC data to various formats

#### Additional Features:
- **Region Statistics**: Show VPC counts, instance counts, etc.
- **Status Indicators**: Visual health status for regions
- **Historical Data**: Track changes over time (if applicable)
- **Keyboard Navigation**: Accessibility improvements

#### Tasks:
1. Add loading and error state handling
2. Create VPC statistics visualization components
3. Implement search and filtering capabilities
4. Add data export functionality
5. Enhance accessibility and keyboard navigation

### Phase 6: Testing and Documentation
**Timeline**: 2-3 hours

#### Testing Strategy:
1. **Unit Tests**: Test region data utilities and UI components
2. **Integration Tests**: Test MCP-UI resource creation and rendering
3. **User Interaction Tests**: Test map clicks and VPC data flow
4. **Visual Regression Tests**: Ensure map renders correctly

#### Documentation:
1. Update CLAUDE.md with UI development patterns
2. Create user guide for interactive map features
3. Document MCP-UI integration patterns
4. Add troubleshooting guide for common issues

#### Tasks:
1. Write comprehensive unit and integration tests
2. Create user documentation and guides
3. Update development documentation
4. Perform user acceptance testing

## File Structure

```
ibmcloud-vpc-mcp/
├── vpc_ui_server.py          # New UI server module
├── region_data.py            # Region geographic data
├── static/                   # UI assets
│   ├── css/
│   │   ├── map.css
│   │   └── geometric.css
│   ├── js/
│   │   ├── map.js
│   │   └── regions.js
│   └── svg/
│       └── world-map.svg
├── templates/                # HTML templates
│   ├── world-map.html
│   └── vpc-details.html
├── tests/
│   ├── test_ui_server.py
│   └── test_region_data.py
└── docs/
    └── UI_GUIDE.md
```

## Mise Tasks Integration

### New .mise.toml Tasks:
```toml
# Branch Management
[tasks."git:create-mcpui"]
description = "Create and switch to mcpui branch"
run = '''
git checkout -b mcpui
echo "✅ Created and switched to mcpui branch"
'''

[tasks."git:switch-mcpui"]
description = "Switch to mcpui branch"
run = '''
git checkout mcpui
echo "✅ Switched to mcpui branch"
'''

[tasks."git:merge-main"]
description = "Merge latest main into mcpui"
run = '''
git checkout mcpui
git merge main
echo "✅ Merged main into mcpui"
'''

# UI Development
[tasks."ui:install"]
description = "Install mcp-ui dependencies"
run = '''
npm install @mcp-ui/server @mcp-ui/client
uv pip install jinja2 aiofiles
echo "✅ UI dependencies installed"
'''

[tasks."ui:dev"]
description = "Start UI development server"
run = '''
python vpc_ui_server.py --dev-mode
'''

[tasks."ui:test"]
description = "Test UI components"
run = '''
python -m pytest tests/test_ui_server.py -v
'''

# Map Development
[tasks."map:validate"]
description = "Validate SVG map structure"
run = '''
python -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('static/svg/world-map.svg')
    print('✅ SVG map is valid')
except Exception as e:
    print(f'❌ SVG validation failed: {e}')
"
'''
```

## Technical Considerations

### Performance Optimization:
1. **SVG Optimization**: Minimize SVG file size while maintaining quality
2. **Lazy Loading**: Load VPC data only when regions are clicked
3. **Caching**: Cache region data and UI resources
4. **Progressive Enhancement**: Ensure basic functionality without JavaScript

### Security Considerations:
1. **Input Validation**: Validate all region codes and parameters
2. **XSS Prevention**: Sanitize all user inputs and dynamic content
3. **API Rate Limiting**: Respect IBM Cloud API rate limits
4. **Error Information**: Avoid exposing sensitive data in error messages

### Accessibility:
1. **Screen Reader Support**: Proper ARIA labels and descriptions
2. **Keyboard Navigation**: Full keyboard accessibility
3. **Color Contrast**: Meet WCAG guidelines for visual elements
4. **Alternative Text**: Descriptive alt text for all visual elements

## Success Metrics

### Functional Requirements:
- ✅ Interactive world map displays all 6 IBM Cloud VPC regions
- ✅ Clicking regions shows VPC data for that region
- ✅ Map renders with geometric/modern design
- ✅ Integration with existing MCP server tools
- ✅ Responsive design works on different screen sizes

### Technical Requirements:
- ✅ Proper MCP-UI protocol implementation
- ✅ Clean separation of UI and data layers
- ✅ Comprehensive error handling
- ✅ Unit and integration test coverage > 80%
- ✅ Documentation for all new components

### User Experience:
- ✅ Map loads within 2 seconds
- ✅ Region selection provides immediate visual feedback
- ✅ VPC data loads within 3 seconds of region click
- ✅ Intuitive navigation and interaction patterns
- ✅ Accessible to users with disabilities

## Risk Mitigation

### Technical Risks:
1. **MCP-UI Learning Curve**: Allocate extra time for learning mcp-ui patterns
2. **SVG Complexity**: Start with simple geometric shapes, enhance iteratively
3. **IBM Cloud API Limits**: Implement proper caching and rate limiting
4. **Browser Compatibility**: Test across major browsers early

### Project Risks:
1. **Scope Creep**: Focus on core functionality first, enhance later
2. **Time Overruns**: Break work into smaller, testable chunks
3. **Integration Issues**: Test MCP integration early and frequently

## Next Steps

1. **Execute Phase 1**: Create branch and set up environment
2. **Validate Approach**: Create minimal proof-of-concept
3. **Iterate Rapidly**: Build incrementally with frequent testing
4. **Gather Feedback**: Test with users early and often
5. **Document Progress**: Keep implementation notes for future reference

## Conclusion

This plan provides a comprehensive approach to implementing an interactive IBM Cloud VPC world map using mcp-ui. The phased approach ensures systematic development while allowing for iterative improvements and early feedback. The integration with existing VPC management tools ensures consistency with the current system architecture.

The geometric design approach will provide a modern, professional appearance while the mcp-ui integration ensures proper protocol compliance and extensibility for future enhancements.