"""
IBM Cloud VPC MCP-UI Regional Graph

Generates an interactive SVG world-map visualisation of IBM Cloud VPC
resources using the mcp-ui-server package, suitable for embedding in
MCP tool responses (legacy embedded-resource pattern).

Map rendering uses D3.js (geoNaturalEarth1 projection) + Natural Earth
TopoJSON data loaded from CDN — no tile server required.
"""

from __future__ import annotations

import json
from typing import Any

from mcp_ui_server import UIResource, create_ui_resource

# ---------------------------------------------------------------------------
# Region metadata: region_id → display details
# ---------------------------------------------------------------------------
IBM_CLOUD_REGIONS: dict[str, dict[str, Any]] = {
    "us-south": {"name": "Dallas",     "lat": 32.78,  "lon": -96.80, "geo": "Americas"},
    "us-east":  {"name": "Washington", "lat": 38.91,  "lon": -77.04, "geo": "Americas"},
    "ca-tor":   {"name": "Toronto",    "lat": 43.65,  "lon": -79.38, "geo": "Americas"},
    "ca-mon":   {"name": "Montreal",   "lat": 45.50,  "lon": -73.57, "geo": "Americas"},
    "br-sao":   {"name": "São Paulo",  "lat": -23.55, "lon": -46.63, "geo": "Americas"},
    "eu-de":    {"name": "Frankfurt",  "lat": 50.11,  "lon":   8.68, "geo": "Europe"},
    "eu-gb":    {"name": "London",     "lat": 51.51,  "lon":  -0.13, "geo": "Europe"},
    "eu-es":    {"name": "Madrid",     "lat": 40.42,  "lon":  -3.70, "geo": "Europe"},
    "eu-fr2":   {"name": "Paris",      "lat": 48.86,  "lon":   2.35, "geo": "Europe"},
    "jp-tok":   {"name": "Tokyo",      "lat": 35.69,  "lon": 139.69, "geo": "Asia Pacific"},
    "jp-osa":   {"name": "Osaka",      "lat": 34.69,  "lon": 135.50, "geo": "Asia Pacific"},
    "au-syd":   {"name": "Sydney",     "lat": -33.87, "lon": 151.21, "geo": "Asia Pacific"},
    "in-che":   {"name": "Chennai",    "lat": 13.08,  "lon":  80.27, "geo": "Asia Pacific"},
}


def _node_radius(vpc_count: int) -> int:
    """Circle radius proportional to VPC count (min 8, max 28)."""
    return max(8, min(28, 8 + vpc_count * 4))


# ---------------------------------------------------------------------------
# HTML builder
# ---------------------------------------------------------------------------

def build_regional_graph_html(regions_data: list[dict[str, Any]]) -> str:
    """
    Build a self-contained interactive HTML page with a D3.js Natural Earth
    world-map showing IBM Cloud regions, sized and coloured by VPC count.

    Requires network access to load D3, topojson-client, and world-atlas
    from jsDelivr CDN (all MIT/BSD licensed, no API key needed).

    Args:
        regions_data: List of dicts, each with keys:
            - region_id  (str)
            - vpc_count  (int)
            - vpc_names  (list[str])
    """
    vpc_by_region: dict[str, dict[str, Any]] = {
        r["region_id"]: {
            "count": r.get("vpc_count", 0),
            "names": r.get("vpc_names", []),
        }
        for r in regions_data
    }

    nodes: list[dict[str, Any]] = []
    for region_id, info in IBM_CLOUD_REGIONS.items():
        vpc_info = vpc_by_region.get(region_id, {"count": 0, "names": []})
        nodes.append(
            {
                "id": region_id,
                "label": info["name"],
                "lon": info["lon"],
                "lat": info["lat"],
                "vpc_count": vpc_info["count"],
                "vpc_names": vpc_info["names"],
                "geo": info["geo"],
                "radius": _node_radius(vpc_info["count"]),
            }
        )

    nodes_json = json.dumps(nodes, ensure_ascii=False)
    total_vpcs = sum(n["vpc_count"] for n in nodes)
    active_regions = sum(1 for n in nodes if n["vpc_count"] > 0)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IBM Cloud VPC Regional Map</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: #0f1117;
  color: #e2e8f0;
  font-family: 'IBM Plex Mono', 'Courier New', monospace;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}}
header {{
  background: #161929;
  border-bottom: 1px solid #1e2d3d;
  padding: 9px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}}
.logo {{
  width: 32px; height: 32px;
  background: #0f62fe;
  border-radius: 3px;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 11px; color: #fff; letter-spacing: 0.05em;
}}
header h1 {{ font-size: 12px; font-weight: 600; letter-spacing: 0.07em; color: #c8d3e0; }}
.stats {{ margin-left: auto; display: flex; gap: 18px; }}
.stat {{ font-size: 10px; color: #4a5568; }}
.stat strong {{ color: #63b3ed; }}
#map-wrap {{ flex: 1; position: relative; overflow: hidden; }}
svg {{ width: 100%; height: 100%; display: block; }}
/* Land + borders */
.land {{ fill: #1a2236; }}
.border {{ fill: none; stroke: #243050; stroke-width: 0.4; }}
.graticule {{ fill: none; stroke: #141c2e; stroke-width: 0.3; }}
.sphere {{ fill: #0c0f1a; }}
/* Region nodes */
.region-node {{ cursor: pointer; }}
.region-node .glow {{
  fill: none;
  stroke-width: 1.5;
  opacity: 0;
  transition: opacity 0.25s;
}}
.region-node:hover .glow {{ opacity: 0.35; }}
.region-node .ring {{
  fill: none;
  stroke-width: 1;
  opacity: 0.2;
}}
.region-node circle.dot {{
  stroke-width: 1.5;
  transition: filter 0.2s;
}}
.region-node:hover circle.dot {{ filter: brightness(1.45) drop-shadow(0 0 6px currentColor); }}
.region-node text.lbl {{
  font-size: 9.5px;
  fill: #718096;
  text-anchor: middle;
  pointer-events: none;
  font-family: 'IBM Plex Mono', monospace;
}}
.region-node text.cnt {{
  font-size: 10px;
  font-weight: 700;
  fill: #fff;
  text-anchor: middle;
  dominant-baseline: central;
  pointer-events: none;
}}
/* Side panel */
.panel {{
  position: absolute;
  top: 12px; right: 12px;
  background: rgba(22, 25, 41, 0.96);
  border: 1px solid #1e2d3d;
  border-radius: 6px;
  padding: 13px 15px;
  min-width: 210px; max-width: 260px;
  backdrop-filter: blur(4px);
  font-size: 11px;
}}
.panel h3 {{
  font-size: 9px; color: #4a90d9;
  letter-spacing: .12em; text-transform: uppercase;
  margin-bottom: 10px;
}}
.pname  {{ font-size: 16px; font-weight: 700; margin-bottom: 2px; }}
.pgeo   {{ font-size: 9px;  color: #68d391;   margin-bottom: 8px; }}
.pcount {{
  font-size: 28px; font-weight: 800; color: #0f62fe; line-height: 1;
  margin-bottom: 6px;
}}
.pcount small {{ font-size: 10px; color: #718096; font-weight: 400; margin-left: 3px; }}
.vpc-list {{
  list-style: none; margin-top: 6px;
  max-height: 130px; overflow-y: auto;
}}
.vpc-list li {{
  font-size: 10px; color: #a0aec0; padding: 3px 0;
  border-top: 1px solid #1e2d3d;
  display: flex; align-items: center; gap: 5px;
}}
.vpc-list li::before {{ content: '▸'; color: #0f62fe; }}
.hint {{ color: #4a5568; font-size: 10px; text-align: center; padding: 8px 0; }}
/* Legends */
.legend {{
  position: absolute; bottom: 12px; left: 12px;
  background: rgba(22, 25, 41, 0.94);
  border: 1px solid #1e2d3d; border-radius: 6px;
  padding: 9px 13px;
  backdrop-filter: blur(4px);
}}
.legend h4, .geo-key h4 {{
  font-size: 8px; color: #4a5568; text-transform: uppercase;
  letter-spacing: .12em; margin-bottom: 6px;
}}
.leg-row {{
  display: flex; align-items: center; gap: 7px;
  margin-bottom: 3px; font-size: 9px; color: #4a5568;
}}
.leg-dot {{ border-radius: 50%; background: #0f62fe; opacity: .75; flex-shrink: 0; }}
.geo-key {{
  position: absolute; bottom: 12px; right: 12px;
  background: rgba(22, 25, 41, 0.94);
  border: 1px solid #1e2d3d; border-radius: 6px;
  padding: 9px 13px;
  backdrop-filter: blur(4px);
}}
.geo-row {{
  display: flex; align-items: center; gap: 7px;
  margin-bottom: 3px; font-size: 9px; color: #a0aec0;
}}
.geo-swatch {{ width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }}
#loading {{
  position: absolute; inset: 0; display: flex;
  align-items: center; justify-content: center;
  color: #4a5568; font-size: 11px; letter-spacing: .08em;
}}
</style>
</head>
<body>
<header>
  <div class="logo">IBM</div>
  <h1>VPC REGIONAL MAP</h1>
  <div class="stats">
    <span class="stat">Regions: <strong>{len(IBM_CLOUD_REGIONS)}</strong></span>
    <span class="stat">Active: <strong>{active_regions}</strong></span>
    <span class="stat">Total VPCs: <strong>{total_vpcs}</strong></span>
  </div>
</header>

<div id="map-wrap">
  <div id="loading">Loading map data…</div>
  <svg id="map"></svg>

  <div class="panel" id="panel">
    <h3>Region Details</h3>
    <div class="hint">Click a region to view details</div>
  </div>

  <div class="legend">
    <h4>Circle size = VPC count</h4>
    <div class="leg-row"><div class="leg-dot" style="width:8px;height:8px"></div>0 VPCs</div>
    <div class="leg-row"><div class="leg-dot" style="width:14px;height:14px"></div>1–2 VPCs</div>
    <div class="leg-row"><div class="leg-dot" style="width:22px;height:22px"></div>3–4 VPCs</div>
    <div class="leg-row"><div class="leg-dot" style="width:28px;height:28px"></div>5+ VPCs</div>
  </div>

  <div class="geo-key">
    <h4>Geography</h4>
    <div class="geo-row"><div class="geo-swatch" style="background:#0f62fe"></div>Americas</div>
    <div class="geo-row"><div class="geo-swatch" style="background:#8b5cf6"></div>Europe</div>
    <div class="geo-row"><div class="geo-swatch" style="background:#10b981"></div>Asia Pacific</div>
  </div>
</div>

<!-- D3 v7 + TopoJSON client (MIT licensed, jsDelivr CDN) -->
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3/dist/topojson-client.min.js"></script>
<script>
const NODES = {nodes_json};

const GEO_COLOR = {{
  'Americas':     '#0f62fe',
  'Europe':       '#8b5cf6',
  'Asia Pacific': '#10b981',
}};

function nodeColor(n) {{
  return n.vpc_count === 0 ? '#2d3748' : (GEO_COLOR[n.geo] || '#0f62fe');
}}

const wrap  = document.getElementById('map-wrap');
const svg   = d3.select('#map');
const panel = document.getElementById('panel');

// Fit projection to container on every render
function render(world) {{
  document.getElementById('loading').style.display = 'none';

  const W = wrap.clientWidth;
  const H = wrap.clientHeight;

  svg.attr('viewBox', `0 0 ${{W}} ${{H}}`);

  const projection = d3.geoNaturalEarth1()
    .scale(W / 6.2)
    .translate([W / 2, H / 2 + H * 0.05]);

  const path = d3.geoPath().projection(projection);

  svg.selectAll('*').remove();

  // Sphere (ocean)
  svg.append('path')
    .datum({{ type: 'Sphere' }})
    .attr('class', 'sphere')
    .attr('d', path);

  // Graticule
  svg.append('path')
    .datum(d3.geoGraticule()())
    .attr('class', 'graticule')
    .attr('d', path);

  // Land masses
  svg.append('path')
    .datum(topojson.feature(world, world.objects.land))
    .attr('class', 'land')
    .attr('d', path);

  // Country borders
  svg.append('path')
    .datum(topojson.mesh(world, world.objects.countries, (a, b) => a !== b))
    .attr('class', 'border')
    .attr('d', path);

  // Region nodes
  const nodes = svg.selectAll('.region-node')
    .data(NODES)
    .join('g')
    .attr('class', 'region-node')
    .attr('transform', d => {{
      const [x, y] = projection([d.lon, d.lat]);
      return `translate(${{x.toFixed(1)}},${{y.toFixed(1)}})`;
    }});

  // Outer glow ring (visible on hover via CSS; always present for active nodes)
  nodes.filter(d => d.vpc_count > 0)
    .append('circle')
    .attr('class', 'glow')
    .attr('r', d => d.radius + 8)
    .style('stroke', d => nodeColor(d));

  // Pulsing ring for active regions
  nodes.filter(d => d.vpc_count > 0)
    .append('circle')
    .attr('class', 'ring')
    .attr('r', d => d.radius + 5)
    .style('stroke', d => nodeColor(d));

  // Main circle
  nodes.append('circle')
    .attr('class', 'dot')
    .attr('r', d => d.radius)
    .style('fill', d => nodeColor(d))
    .style('fill-opacity', d => d.vpc_count > 0 ? 0.85 : 0.45)
    .style('stroke', d => nodeColor(d))
    .style('color', d => nodeColor(d));

  // VPC count badge
  nodes.filter(d => d.vpc_count > 0)
    .append('text')
    .attr('class', 'cnt')
    .attr('y', 0)
    .text(d => d.vpc_count);

  // City label below node
  nodes.append('text')
    .attr('class', 'lbl')
    .attr('y', d => d.radius + 13)
    .text(d => d.label);

  // Click handler
  nodes.on('click', (event, d) => {{
    event.stopPropagation();
    showPanel(d);
  }});
}}

function showPanel(n) {{
  const c = nodeColor(n);
  const vpcs = n.vpc_names.length
    ? '<ul class="vpc-list">' + n.vpc_names.map(v => `<li>${{v}}</li>`).join('') + '</ul>'
    : '<div class="hint">No VPCs in this region</div>';

  panel.innerHTML = `
    <h3>Region Details</h3>
    <div class="pname" style="color:${{c}}">${{n.id}}</div>
    <div class="pgeo">${{n.geo}} &middot; ${{n.label}}</div>
    <div class="pcount">${{n.vpc_count}}<small>VPC${{n.vpc_count !== 1 ? 's' : ''}}</small></div>
    ${{vpcs}}`;
}}

// Load Natural Earth 110m TopoJSON from jsDelivr (MIT / public domain data)
d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json')
  .then(world => {{
    render(world);
    window.addEventListener('resize', () => render(world));
  }})
  .catch(() => {{
    document.getElementById('loading').textContent =
      'Map data unavailable — check network access to cdn.jsdelivr.net';
  }});
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

REGIONAL_GRAPH_URI = "ui://ibm-vpc/regional-graph"


def create_regional_graph_resource(
    regions_data: list[dict[str, Any]],
    uri: str = REGIONAL_GRAPH_URI,
) -> UIResource:
    """
    Build a mcp-ui UIResource containing the interactive regional VPC map.

    Args:
        regions_data: List of dicts with keys region_id, vpc_count, vpc_names.
        uri:          MCP resource URI (defaults to REGIONAL_GRAPH_URI).

    Returns:
        UIResource ready for embedding in an MCP tool response.
    """
    html = build_regional_graph_html(regions_data)
    return create_ui_resource(
        {
            "uri": uri,
            "content": {"type": "rawHtml", "htmlString": html},
            "encoding": "text",
        }
    )
