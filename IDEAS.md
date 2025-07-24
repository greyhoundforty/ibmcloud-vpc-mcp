I would like to See if the [mcp-ui](https://mcpui.dev/guide/introduction) server will allow me to display a clickable graph of IBM Cloud regions to interact with the VPCs in those regions. Before I do that, I need to:

 - Display the IBM Cloud regions overlayed on a world map. The locations to be displayed can be found in this svg: https://cloud.ibm.com/docs-content/v4/content/8d120c63c6b3d35dc52f4f2bd6a4e3b27430976d/overview/images/Global-View.svg. This includes their Cities and regional names.
- I would like the world map to have a more geometric look similar to this https://media.gettyimages.com/id/523595885/vector/geometric-world-map.webp?s=2048x2048&w=gi&k=20&c=8484gWwwNNeHGMWvpbmcb1CJqsSyQvWPQ2PN9xI_j3E=
- The map should be interactive, allowing users to click on a region to see the VPCs available in that region, but for now, I just want to display the regions.

Come up with a plan to implement this using mcp-ui, including any necessary libraries or tools that would facilitate the creation of the interactive map. Consider how to handle the SVG data and how to make the regions clickable. Write the plan in a structured format to ensure clarity and ease of implementation.