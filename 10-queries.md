
Histogram
- Histogram — 'MindatGeoMaterialQuery': Plot histogram of 'weighting' for IMA-approved minerals with hardness between 5 and 10.  
- Histogram — 'MindatGeoMaterialQuery': Plot histogram of element counts for hexagonal crystal-system minerals (include elements field).  
- Histogram — 'MindatGeoMaterialQuery': Plot histogram of 'weighting' for minerals that include Fe and exclude S.  
- Histogram — 'MindatGeoMaterialQuery': Plot histogram of hardness for IMA-approved minerals discovered before 1990.  
- Histogram — 'MindatGeoMaterialQuery': Plot overlaid histograms comparing 'weighting' for Abelsonite vs Pyrite (top 50 results each).  
- Histogram — 'MindatGeoMaterialQuery': Create histogram of 'weighting' (log scale) for minerals with 'weighting' > 1000.  
- Histogram — 'MindatGeoMaterialQuery': Plot histogram of reported crystal size or abundance proxy (use 'weighting') for minerals containing Cu with page-size=500.

Heatmap
- Heatmap — 'MindatLocalityQuery': Show density heatmap of localities in Canada ('country=Canada', expand=~all, fields=latitude,longitude).  
- Heatmap — 'MindatLocalityQuery': Create heatmap of mineral localities in Brazil colored by locality count per province ('country=Brazil', fields=latitude,longitude,country,parent).  
- Heatmap — 'MindatLocalityQuery': Produce a spatial heatmap for Korea for records updated since 2000 ('country=Korea', updated_at>=2000-01-01 00:00:00).  
- Heatmap — 'MindatLocalityQuery': Generate choropleth of distinct mineral richness per Canadian province (use 'expand=geomaterials', fields=parent,latitude,longitude).  
- Heatmap — 'MindatLocalityQuery': Plot a two-layer heatmap for Canada comparing localities labeled "mine" vs "outcrop" (filter by 'locality_type' via 'fields'/'expand').  
- Heatmap — 'MindatLocalityQuery': Create grid heatmap for western Canada using a lat/lon bounding-box (use 'fields=latitude,longitude' and page-size large).  
- Heatmap — 'MindatLocalityQuery': Show heatmap of mean mineral 'weighting' at localities in Canada (expand geomaterials to aggregate weighting per locality).

Network Plot
- Network — 'MindatLocalityQuery' + 'MindatGeoMaterialQuery': Plot mineral co-occurrence network for Canada (nodes=minerals from localities where 'country=Canada'; edges weighted by shared localities).  
- Network — 'MindatLocalityQuery': Create bipartite network linking minerals ⇄ localities in Canada, include minerals appearing in ≥5 localities ('country=Canada', expand=geomaterials).  
- Network — 'MindatLocalityQuery': Produce a locality-level network where edges connect localities sharing ≥3 minerals ('country=Canada', expand=geomaterials).  
- Network — 'MindatGeoMaterialQuery': Build element co-occurrence network for minerals containing at least one of {Fe, Cu, Al} (nodes=elements, edges=co-occurrence within mineral records).  
- Network — 'MindatGeoMaterialQuery' + 'MindatLocalityQuery': Generate a regional mineral-network limited to Ontario (filter localities by parent/region=Ontario, then minerals from those localities).  
- Network — 'MindatGeoMaterialQuery': Create a mineral-class network where nodes are mineral classes and edges represent shared localities (expand geomaterials → class).  

