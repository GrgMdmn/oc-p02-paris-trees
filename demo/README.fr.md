# Travail complémentaire - carte interactive des arbres de Paris

📘 This folder is also documented in [English 🇬🇧](./README.md)

Ce dossier est un **complément** au projet P02, pas une pièce du rendu d'origine.
Le notebook `Paris_trees_analysis.ipynb`, le module `data_analysis_functions.py`
et les cartes Folium `map_arrondissement.html` / `map_lieu.html` restent la
source de référence et ne sont pas modifiés.

## Ce que ça ajoute

Le notebook produit des cartes Folium statiques. Cette page va plus loin côté
restitution :

- **filtres** par zone (arrondissements, bois, départements limitrophes) et par
  espèce (top 40 + « autres espèces ») ;
- **trois vues** : densité par zone (cercles proportionnels), heatmap, points
  individuels ;
- **KPI recalculés à la volée** : nombre d'arbres, hauteur moyenne,
  circonférence moyenne, nombre de remarquables ;
- **top espèces / top zones** mis à jour selon les filtres ;
- page **autonome** (un seul fichier HTML). Leaflet et Leaflet.heat sont
  chargés depuis un CDN, avec des empreintes Subresource Integrity.

C'est le même moteur que Folium (Leaflet), piloté directement en JavaScript
pour avoir des filtres utilisables.

Page en ligne (le même fichier) : https://demo.gregoiremureau.com/arbres-paris-carte-interactive.html

## Régénérer la page

Le CSV n'est pas versionné (environ 29 Mo). Voir `../fetch-data.sh` pour le
récupérer depuis l'open data de la Ville de Paris.

```bash
cd demo
python3 generer_carte_arbres.py ../p2-trees-fr.csv carte_arbres_paris_interactive.html
```

Le script n'a besoin que de la bibliothèque standard Python (csv, json, random).
Il échantillonne 8 000 points pour la heatmap et agrège les 200 137 arbres
par zone et par espèce.

## Données

- Source : [Open Data Ville de Paris - Les arbres](https://opendata.paris.fr/explore/dataset/les-arbres/)
- 200 137 arbres, 536 espèces, 184 remarquables.
- Les valeurs manquantes et aberrantes sont traitées dans le notebook
  d'origine. Cette page part du CSV brut pour la restitution.

## Auteur

Grégoire Mureau - travail complémentaire au projet P02 (Master AI Engineer).
