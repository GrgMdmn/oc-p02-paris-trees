#!/usr/bin/env python3
"""Génère une carte interactive des arbres de Paris (travail complémentaire P02).

Lit le CSV Open Data Paris (p2-trees-fr.csv), agrège par zone et par espèce,
échantillonne des points pour la heatmap, et écrit une page HTML autonome
(Leaflet + Leaflet.heat via CDN).

Usage :
    python3 generer_carte_arbres.py ../p2-trees-fr.csv carte_arbres_paris_interactive.html
"""

import csv
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

SAMPLE_POINTS = 8000
TOP_SPECIES = 40


def parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def zone_sort_key(name):
    upper = name.upper()
    if upper.startswith("PARIS ") and "ARRDT" in upper:
        digits = "".join(c for c in upper.split()[1] if c.isdigit())
        return (0, int(digits) if digits else 99)
    if upper.startswith("BOIS DE"):
        return (1, upper)
    return (2, upper)


def species_label(row):
    label = (row.get("libelle_francais") or "").strip()
    if label:
        return label
    genre = (row.get("genre") or "").strip()
    espece = (row.get("espece") or "").strip()
    label = f"{genre} {espece}".strip()
    return label or "Non renseigné"


def main(csv_path, out_path):
    rows = []
    zone_counts = defaultdict(int)
    species_counts = defaultdict(int)
    zone_species = defaultdict(lambda: [0, 0, 0.0, 0, 0.0, 0, 0, 0.0, 0, 0.0])
    zone_lat = defaultdict(float)
    zone_lon = defaultdict(float)
    zone_n = defaultdict(int)
    zone_top = defaultdict(lambda: defaultdict(int))
    species_top = defaultdict(lambda: defaultdict(int))
    global_stats = [0, 0, 0.0, 0, 0.0, 0, 0, 0.0, 0, 0.0]

    reservoir = []
    seen = 0
    rng = random.Random(42)

    with open(csv_path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        for row in reader:
            zone = (row.get("arrondissement") or "").strip() or "Non renseigné"
            species = species_label(row)
            height = parse_float(row.get("hauteur_m"))
            circ = parse_float(row.get("circonference_cm"))
            remarkable = (row.get("remarquable") or "").strip() == "1"
            lat = parse_float(row.get("geo_point_2d_a"))
            lon = parse_float(row.get("geo_point_2d_b"))

            zone_counts[zone] += 1
            species_counts[species] += 1
            zone_top[zone][species] += 1
            species_top[species][zone] += 1

            cell = zone_species[(zone, species)]
            cell[0] += 1
            if height is not None:
                cell[1] += 1
                cell[2] += height
            if circ is not None:
                cell[3] += 1
                cell[4] += circ
            if remarkable:
                cell[5] += 1
                if height is not None:
                    cell[6] += 1
                    cell[7] += height
                if circ is not None:
                    cell[8] += 1
                    cell[9] += circ

            global_stats[0] += 1
            if height is not None:
                global_stats[1] += 1
                global_stats[2] += height
            if circ is not None:
                global_stats[3] += 1
                global_stats[4] += circ
            if remarkable:
                global_stats[5] += 1
                if height is not None:
                    global_stats[6] += 1
                    global_stats[7] += height
                if circ is not None:
                    global_stats[8] += 1
                    global_stats[9] += circ

            if lat is not None and lon is not None:
                zone_lat[zone] += lat
                zone_lon[zone] += lon
                zone_n[zone] += 1
                seen += 1
                point = [round(lat, 5), round(lon, 5), zone, species,
                         round(height, 1) if height is not None else None,
                         round(circ, 1) if circ is not None else None,
                         1 if remarkable else 0]
                if len(reservoir) < SAMPLE_POINTS:
                    reservoir.append(point)
                else:
                    j = rng.randint(0, seen - 1)
                    if j < SAMPLE_POINTS:
                        reservoir[j] = point

    zones = sorted(zone_counts, key=zone_sort_key)
    species = sorted(species_counts, key=lambda s: (-species_counts[s], s))
    zone_index = {name: i for i, name in enumerate(zones)}
    species_index = {name: i for i, name in enumerate(species)}

    zone_payload = []
    for zone in zones:
        lat = zone_lat[zone] / zone_n[zone] if zone_n[zone] else None
        lon = zone_lon[zone] / zone_n[zone] if zone_n[zone] else None
        top = sorted(zone_top[zone].items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        zone_payload.append({
            "name": zone,
            "count": zone_counts[zone],
            "lat": round(lat, 5) if lat is not None else None,
            "lon": round(lon, 5) if lon is not None else None,
            "top": [[name, count] for name, count in top],
        })

    species_payload = []
    for name in species:
        top = sorted(species_top[name].items(), key=lambda kv: (-kv[1], kv[0]))[:1]
        species_payload.append({
            "name": name,
            "count": species_counts[name],
            "top": [[zone, count] for zone, count in top],
        })

    matrix = {}
    for (zone, sp), cell in zone_species.items():
        matrix[f"{zone_index[zone]}|{species_index[sp]}"] = [round(v, 1) if isinstance(v, float) else v for v in cell]

    points = []
    for lat, lon, zone, sp, height, circ, remarkable in reservoir:
        points.append([lat, lon, zone_index[zone], species_index[sp], height, circ, remarkable])

    data = {
        "global": {
            "total": global_stats[0],
            "zones": len(zones),
            "species": len(species),
            "avgHeight": round(global_stats[2] / global_stats[1], 1) if global_stats[1] else None,
            "avgCirc": round(global_stats[4] / global_stats[3], 1) if global_stats[3] else None,
            "remarkable": global_stats[5],
        },
        "zones": zone_payload,
        "species": species_payload,
        "matrix": matrix,
        "points": points,
        "topSpecies": species[:TOP_SPECIES],
    }

    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    Path(out_path).write_text(html, encoding="utf-8")
    print(f"écrit {out_path} ({Path(out_path).stat().st_size / 1024 / 1024:.2f} Mo)")
    print(f"{len(zones)} zones, {len(species)} espèces, {len(points)} points échantillonnés")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow"><meta name="description" content="Carte interactive des arbres de Paris (open data Ville de Paris) : filtres par zone et espèce, densité, heatmap, indicateurs recalculés. Démo de cartographie web.">
<title>Arbres de Paris - carte interactive</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha384-sHL9NAb7lN7rfvG5lfHpm643Xkcjzp4jFvuavGOndn6pjVqS6ny56CAt3nsEVT4H" crossorigin="anonymous">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha384-cxOPjt7s7Iz04uaHJceBmS+qpjv2JkIHNVcuOrM+YHwZOmJGBXI00mdUXEq65HTH" crossorigin="anonymous"></script>
<script src="https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js" integrity="sha384-mFKkGiGvT5vo1fEyGCD3hshDdKmW3wzXW/x+fWriYJArD0R3gawT6lMvLboM22c0" crossorigin="anonymous"></script>
<style>
  :root {
    --bg: #0f1120;
    --panel: #171a2e;
    --panel-2: #1e2238;
    --line: #2b3050;
    --ink: #e8eaf2;
    --muted: #9aa1b8;
    --accent: #e94560;
    --accent-2: #ff9f43;
    --ok: #2ecc71;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
    line-height: 1.45;
  }
  .wrap { max-width: 1240px; margin: 0 auto; padding: 1.4rem 1rem 3rem; }
  header { margin-bottom: 1rem; }
  .badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border: 1px solid rgba(233, 69, 96, 0.45);
    background: rgba(233, 69, 96, 0.12);
    color: #ff8ba0;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  h1 { margin: 0.45rem 0 0.2rem; font-size: 1.65rem; }
  .sub { margin: 0; color: var(--muted); font-size: 0.9rem; max-width: 900px; }
  .sub a { color: #ff9f43; }
  .kpis {
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 0.5rem;
    margin: 1rem 0;
  }
  .kpi {
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 0.55rem 0.65rem;
  }
  .kpi strong { display: block; font-size: 1.15rem; color: #fff; line-height: 1.15; }
  .kpi span { display: block; font-size: 0.68rem; color: var(--muted); margin-top: 0.15rem; text-transform: uppercase; letter-spacing: 0.05em; }
  .toolbar {
    display: grid;
    grid-template-columns: 1.2fr 1.6fr auto auto auto;
    gap: 0.55rem;
    align-items: end;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
  }
  .field { display: flex; flex-direction: column; gap: 0.25rem; }
  .field label { font-size: 0.68rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
  select, button {
    font: inherit;
    font-size: 0.86rem;
    color: var(--ink);
    background: var(--panel-2);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 0.45rem 0.5rem;
  }
  select:focus, button:focus { outline: 2px solid var(--accent); outline-offset: 1px; }
  button { cursor: pointer; }
  button:hover { border-color: var(--accent); }
  .check { display: flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: var(--muted); padding-bottom: 0.45rem; }
  .check input { accent-color: var(--accent); }
  .layout { display: grid; grid-template-columns: 1fr 300px; gap: 0.75rem; }
  #map {
    height: 62vh;
    min-height: 440px;
    border-radius: 10px;
    border: 1px solid var(--line);
    background: #dfe6ee;
  }
  .side { display: flex; flex-direction: column; gap: 0.6rem; }
  .panel {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 0.7rem 0.8rem;
  }
  .panel h2 { margin: 0 0 0.5rem; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
  .bar-row { margin-bottom: 0.45rem; }
  .bar-top { display: flex; justify-content: space-between; gap: 0.5rem; font-size: 0.78rem; }
  .bar-top span:last-child { color: var(--muted); white-space: nowrap; }
  .bar { height: 5px; background: #0d0f1c; border-radius: 999px; margin-top: 0.2rem; overflow: hidden; }
  .bar i { display: block; height: 100%; background: linear-gradient(90deg, var(--accent-2), var(--accent)); border-radius: 999px; }
  .legend {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 0.6rem 0.7rem;
    font-size: 0.76rem;
    color: var(--muted);
  }
  .legend .grad { height: 8px; border-radius: 999px; margin: 0.35rem 0; background: linear-gradient(90deg, #ffe08a, #ff9f43, #e94560, #8e1f38); }
  .legend .row { display: flex; justify-content: space-between; font-size: 0.68rem; }
  .note { font-size: 0.78rem; color: var(--muted); margin-top: 0.8rem; }
  .note a { color: #ff9f43; }
  footer { margin-top: 1.4rem; padding-top: 0.8rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 0.78rem; }
  @media (max-width: 980px) {
    .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    .toolbar { grid-template-columns: 1fr 1fr; }
    .layout { grid-template-columns: 1fr; }
    #map { height: 55vh; }
  }
  @media (max-width: 560px) {
    .kpis { grid-template-columns: 1fr 1fr; }
    .toolbar { grid-template-columns: 1fr; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="badge">Travail complémentaire - projet P02</span>
    <h1>Arbres de Paris - carte interactive</h1>
    <p class="sub">Exploration du patrimoine arboré parisien à partir de l'open data de la Ville de Paris. Filtres par zone et par espèce, trois vues (densité, heatmap, points), indicateurs recalculés à la volée. Le notebook et les cartes Folium d'origine restent dans <a href="https://git.gregoiremureau.com/openclassroom-ai/oc-p02-paris-trees" target="_blank" rel="noopener">le dépôt P02</a> ; cette page est un complément interactif.</p>
  </header>

  <div class="kpis" id="kpis"></div>

  <div class="toolbar">
    <div class="field">
      <label for="zone">Zone</label>
      <select id="zone"></select>
    </div>
    <div class="field">
      <label for="species">Espèce</label>
      <select id="species"></select>
    </div>
    <div class="field">
      <label for="view">Vue</label>
      <select id="view">
        <option value="zones">Densité par zone</option>
        <option value="heat">Heatmap</option>
        <option value="points">Points</option>
      </select>
    </div>
    <label class="check"><input type="checkbox" id="remarkable"> Remarquables</label>
    <button type="button" id="reset">Réinitialiser</button>
  </div>

  <div class="layout">
    <div id="map"></div>
    <aside class="side">
      <div class="panel">
        <h2>Top espèces</h2>
        <div id="topSpecies"></div>
      </div>
      <div class="panel">
        <h2>Top zones</h2>
        <div id="topZones"></div>
      </div>
      <div class="legend">
        <div><strong>Légende</strong></div>
        <div class="grad"></div>
        <div class="row"><span>Faible</span><span>Forte densité</span></div>
        <div id="legendText" style="margin-top:0.4rem;"></div>
      </div>
    </aside>
  </div>

  <p class="note">Données : <a href="https://opendata.paris.fr/explore/dataset/les-arbres/" target="_blank" rel="noopener">Open Data Ville de Paris - Les arbres</a>. 200 137 arbres, 536 espèces, 184 remarquables. Le notebook d'origine traite le nettoyage et les analyses statistiques ; cette page ajoute les agrégats, les filtres et la restitution interactive.</p>

  <footer>
    Grégoire Mureau - démo de cartographie web, travail complémentaire au projet P02 (Master AI Engineer).
  </footer>
</div>

<script>
const DATA = __DATA__;
const TOP = DATA.topSpecies.length;
const state = { zone: -1, species: -1, remarkable: false, view: 'zones' };

const map = L.map('map', { zoomControl: true, preferCanvas: true }).setView([48.8566, 2.3522], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap'
}).addTo(map);

const zonesLayer = L.layerGroup();
const pointsLayer = L.layerGroup();
let heatLayer = null;

function zoneName(i) { return DATA.zones[i] ? DATA.zones[i].name : ''; }
function speciesName(i) { return DATA.species[i] ? DATA.species[i].name : ''; }
function fmt(n) { return n == null ? 'n/d' : Number(n).toLocaleString('fr-FR'); }

function cellFor(zi, si) {
  const cell = DATA.matrix[zi + '|' + si];
  return cell || [0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
}

function selectedSpeciesMatch(si) {
  if (state.species === -1) return true;
  if (state.species === -2) return si >= TOP;
  return si === state.species;
}

function aggregate() {
  let count = 0, nH = 0, sumH = 0, nC = 0, sumC = 0, rem = 0, remNH = 0, remSumH = 0, remNC = 0, remSumC = 0;
  const bySpecies = {};
  const byZone = {};
  DATA.zones.forEach((z, zi) => {
    if (state.zone !== -1 && zi !== state.zone) return;
    DATA.species.forEach((s, si) => {
      if (!selectedSpeciesMatch(si)) return;
      const c = cellFor(zi, si);
      if (!c[0]) return;
      if (state.remarkable) {
        if (!c[5]) return;
        count += c[5]; rem += c[5];
        nH += c[6]; sumH += c[7]; nC += c[8]; sumC += c[9];
      } else {
        count += c[0]; nH += c[1]; sumH += c[2]; nC += c[3]; sumC += c[4]; rem += c[5];
        remNH += c[6]; remSumH += c[7]; remNC += c[8]; remSumC += c[9];
      }
      bySpecies[si] = (bySpecies[si] || 0) + (state.remarkable ? c[5] : c[0]);
      byZone[zi] = (byZone[zi] || 0) + (state.remarkable ? c[5] : c[0]);
    });
  });
  return { count, nH, sumH, nC, sumC, rem, bySpecies, byZone };
}

function renderKpis(agg) {
  const avgH = agg.nH ? (agg.sumH / agg.nH) : null;
  const avgC = agg.nC ? (agg.sumC / agg.nC) : null;
  const items = [
    ['Arbres', fmt(agg.count)],
    ['Zones', fmt(Object.keys(agg.byZone).length)],
    ['Espèces', fmt(Object.keys(agg.bySpecies).length)],
    ['Hauteur moy.', avgH == null ? 'n/d' : avgH.toFixed(1) + ' m'],
    ['Circonf. moy.', avgC == null ? 'n/d' : avgC.toFixed(0) + ' cm'],
    ['Remarquables', fmt(agg.rem)]
  ];
  document.getElementById('kpis').innerHTML = items.map(([label, value]) =>
    `<div class="kpi"><strong>${value}</strong><span>${label}</span></div>`).join('');
}

function renderBars(container, entries, total) {
  const max = Math.max(1, ...entries.map(e => e[1]));
  document.getElementById(container).innerHTML = entries.length ? entries.map(([name, count]) =>
    `<div class="bar-row"><div class="bar-top"><span>${name}</span><span>${fmt(count)}</span></div><div class="bar"><i style="width:${Math.round(count / max * 100)}%"></i></div></div>`
  ).join('') : '<div style="color:var(--muted);font-size:0.8rem;">Aucune donnée pour ces filtres.</div>';
}

function renderSide(agg) {
  const species = Object.entries(agg.bySpecies).sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([si, c]) => [speciesName(Number(si)), c]);
  const zones = Object.entries(agg.byZone).sort((a, b) => b[1] - a[1]).slice(0, 8)
    .map(([zi, c]) => [zoneName(Number(zi)), c]);
  renderBars('topSpecies', species);
  renderBars('topZones', zones);
}

function clearLayers() {
  zonesLayer.clearLayers();
  pointsLayer.clearLayers();
  if (map.hasLayer(zonesLayer)) map.removeLayer(zonesLayer);
  if (map.hasLayer(pointsLayer)) map.removeLayer(pointsLayer);
  if (heatLayer && map.hasLayer(heatLayer)) { map.removeLayer(heatLayer); heatLayer = null; }
}

function renderZones(agg) {
  const max = Math.max(1, ...Object.values(agg.byZone));
  DATA.zones.forEach((z, zi) => {
    if (state.zone !== -1 && zi !== state.zone) return;
    const count = agg.byZone[zi] || 0;
    if (!count || z.lat == null || z.lon == null) return;
    const ratio = count / max;
    const radius = 8 + 30 * Math.sqrt(ratio);
    const color = ratio > 0.75 ? '#8e1f38' : ratio > 0.5 ? '#e94560' : ratio > 0.25 ? '#ff9f43' : '#ffe08a';
    L.circleMarker([z.lat, z.lon], {
      radius, color: '#ffffff', weight: 1, fillColor: color, fillOpacity: 0.62
    }).bindPopup(
      `<strong>${z.name}</strong><br>${fmt(count)} arbres<br>` +
      `Top espèces : ${z.top.map(t => t[0] + ' (' + fmt(t[1]) + ')').join(', ')}`
    ).addTo(zonesLayer);
  });
  zonesLayer.addTo(map);
  document.getElementById('legendText').textContent = 'Cercles proportionnels au nombre d’arbres.';
}

function filteredPoints() {
  return DATA.points.filter(p => {
    if (state.zone !== -1 && p[2] !== state.zone) return false;
    if (!selectedSpeciesMatch(p[3])) return false;
    if (state.remarkable && p[6] !== 1) return false;
    return true;
  });
}

function renderHeat(agg) {
  const pts = filteredPoints();
  // Nouvelle couche à chaque fois : Leaflet.heat ne se réattache pas proprement
  // après un removeLayer (canvas détaché), donc on ne réutilise pas l'ancienne.
  heatLayer = L.heatLayer(pts.map(p => [p[0], p[1]]), { radius: 20, blur: 24, maxZoom: 14 }).addTo(map);
  document.getElementById('legendText').textContent = `${fmt(pts.length)} points échantillonnés (sur ${fmt(agg.count)} arbres filtrés).`;
}

function renderPoints(agg) {
  const pts = filteredPoints();
  pts.forEach(p => {
    const color = p[6] ? '#e94560' : '#2f6fb0';
    L.circleMarker([p[0], p[1]], { radius: 3, color: '#fff', weight: 0.5, fillColor: color, fillOpacity: 0.8 })
      .bindPopup(`<strong>${speciesName(p[3])}</strong><br>${zoneName(p[2])}<br>` +
        `${p[4] == null ? 'hauteur n/d' : p[4] + ' m'} · ${p[5] == null ? 'circonf. n/d' : p[5] + ' cm'}` +
        (p[6] ? '<br><span style="color:#e94560">Remarquable</span>' : ''))
      .addTo(pointsLayer);
  });
  pointsLayer.addTo(map);
  document.getElementById('legendText').textContent = `${fmt(pts.length)} points affichés (échantillon). Rouge = remarquable.`;
}

function render() {
  const agg = aggregate();
  renderKpis(agg);
  renderSide(agg);
  clearLayers();
  if (state.view === 'zones') renderZones(agg);
  else if (state.view === 'heat') renderHeat(agg);
  else renderPoints(agg);
}

function fillSelects() {
  const zone = document.getElementById('zone');
  zone.innerHTML = '<option value="-1">Toutes les zones</option>' +
    DATA.zones.map((z, i) => `<option value="${i}">${z.name}</option>`).join('');
  const species = document.getElementById('species');
  species.innerHTML = '<option value="-1">Toutes les espèces</option>' +
    DATA.topSpecies.map((s, i) => `<option value="${i}">${s}</option>`).join('') +
    '<option value="-2">Autres espèces</option>';
}

document.getElementById('zone').addEventListener('change', e => { state.zone = Number(e.target.value); render(); });
document.getElementById('species').addEventListener('change', e => { state.species = Number(e.target.value); render(); });
document.getElementById('view').addEventListener('change', e => { state.view = e.target.value; render(); });
document.getElementById('remarkable').addEventListener('change', e => { state.remarkable = e.target.checked; render(); });
document.getElementById('reset').addEventListener('click', () => {
  state.zone = -1; state.species = -1; state.remarkable = false; state.view = 'zones';
  document.getElementById('zone').value = '-1';
  document.getElementById('species').value = '-1';
  document.getElementById('view').value = 'zones';
  document.getElementById('remarkable').checked = false;
  render();
});

fillSelects();
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
