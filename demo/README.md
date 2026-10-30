# Complementary work - interactive map of Paris trees

📘 Ce dossier est également documenté en [français 🇫🇷](./README.fr.md)

This folder is a **complement** to project P02, not part of the original submission.
The notebook `Paris_trees_analysis.ipynb`, the module `data_analysis_functions.py`
and the Folium maps `map_arrondissement.html` / `map_lieu.html` stay the
reference and are not modified.

## What it adds

The notebook produces static Folium maps. This page goes further on the
user-facing side:

- **filters** by area (districts, woods, neighbouring departments) and by
  species (top 40 + "other species");
- **three views**: density by area (proportional circles), heatmap, individual points;
- **KPIs recomputed on the fly**: tree count, mean height, mean circumference,
  number of remarkable trees;
- **top species / top areas** updated with the filters;
- a **single HTML file**. Leaflet and Leaflet.heat are loaded from a CDN,
  with Subresource Integrity hashes.

It uses the same engine as Folium (Leaflet), driven directly in JavaScript
so the filters are practical to use.

Live page (same file): https://demo.gregoiremureau.com/arbres-paris-carte-interactive.html

## Regenerate the page

The CSV is not versioned (about 29 MB). See `../fetch-data.sh` to get it
from the City of Paris open data.

```bash
cd demo
python3 generer_carte_arbres.py ../p2-trees-fr.csv carte_arbres_paris_interactive.html
```

The script only needs the Python standard library (csv, json, random).
It samples 8,000 points for the heatmap and aggregates the 200,137 trees
by area and by species.

## Data

- Source: [Open Data City of Paris - Trees](https://opendata.paris.fr/explore/dataset/les-arbres/)
- 200,137 trees, 536 species, 184 remarkable trees.
- Missing and aberrant values are handled in the original notebook. This page
  starts from the raw CSV for the display.

## Author

Grégoire Mureau - complementary work on project P02 (Master AI Engineer).
