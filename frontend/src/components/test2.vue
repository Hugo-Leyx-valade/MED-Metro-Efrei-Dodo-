<template>
  <div id="container">
    <aside id="sidebar" class="panel">
      <h1 class="title">🗺️ Calcul d’itinéraire Métro</h1>

      <label class="label">Station de départ :</label>
      <select v-model="startId" class="select">
        <option disabled value="">-- Sélectionner --</option>
        <option v-for="(station, id) in stations" :key="id" :value="id">
          {{ station.nom }} (Ligne{{ station.lignes.length > 1 ? 's' : '' }} :
          {{ station.lignes.join(', ') }})
        </option>
      </select>

      <label class="label">Station d’arrivée :</label>
      <select v-model="endId" class="select">
        <option disabled value="">-- Sélectionner --</option>
        <option v-for="(station, id) in stations" :key="id" :value="id">
          {{ station.nom }} (Ligne{{ station.lignes.length > 1 ? 's' : '' }} :
          {{ station.lignes.join(', ') }})
        </option>
      </select>

      <button class="btn primary" @click="fetchPath">Afficher le chemin</button>
      <button class="btn" @click="resetPath">Réinitialiser</button>
      <button class="btn" @click="fetchACPM">Calculer l'ACPM</button>
    </aside>

    <div id="details" class="panel">
      <h2>🧭 Chemin :</h2>
      <div v-if="estimatedDuration > 0" class="duration">
        ⏱️ Durée estimée : {{ estimatedDuration }} min
      </div>
      <ul>
        <li v-for="(id, index) in currentPath" :key="index">
          <span
            class="badge"
            :style="{ backgroundColor: getLineColor(stations[id]?.lignes?.[0]) }"
          ></span>
          {{ stations[id]?.nom || '(station inconnue)' }}
        </li>
      </ul>

      <h2 style="margin-top: 20px">🌐 ACPM :</h2>
      <div v-if="acpmEdges.length > 0" class="duration">
        ✅ {{ acpmEdges.length }} connexions – poids total : {{ Math.round(totalWeight / 60) }} min
      </div>
      <ul v-if="acpmEdges.length > 0">
        <li v-for="(edge, index) in acpmEdges" :key="'acpm-' + index" class="acpm-edge">
          <span>
            <b>{{ stations[normalizeId(edge.node0)]?.nom || edge.node0 }}</b>
            ⇄
            <b>{{ stations[normalizeId(edge.node1)]?.nom || edge.node1 }}</b>
            ({{ Math.round(edge.weight / 60) }} min)
          </span>
        </li>
      </ul>
    </div>

    <div id="map" ref="map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Références
const leafletMap = ref(null)
const acpmLayer = ref(null)
let pathLayer = null
let backgroundLines = []
let stationCircles = []

// Données principales
const stations = ref({})
const edges = ref([])
const startId = ref('')
const endId = ref('')
const currentPath = ref([])

const acpmEdges = ref([])
const totalWeight = ref(0)

const estimatedDuration = computed(() => currentPath.value.length > 1 ? currentPath.value.length - 1 : 0)

// Couleurs des lignes
const lineColors = {
  1: '#ffcd00', 2: '#0055c8', 3: '#837902', 4: '#932990', 5: '#ff7e2e',
  6: '#6ec4e8', 7: '#f5a2bd', '7B': '#ff7f50', 8: '#c9910d', 9: '#d5c900',
  10: '#e4b12f', 11: '#704b1c', 12: '#007852', 13: '#99d4e4', 14: '#62259d',
  default: '#999'
}

// 🔁 ID uniforme (majuscule)
// Mapping: nom normalisé → ID réel
const nameToId = {}
for (const [id, station] of Object.entries(stations.value)) {
  if (station.name) {
    const cleanName = station.name.toLowerCase().replace(/[\s\-']/g, '_')
    nameToId[cleanName] = id
  }
}

// Fonction de normalisation :
function normalizeId(name) {
  const clean = name.toLowerCase().replace(/[\s\-']/g, '_')
  return nameToId[clean] || null
}
function normalizeName(name) {
  return name.toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // enlever accents
    .replace(/[\s\-']/g, '_') // remplacer espaces, tirets, apostrophes par _
}
const getLineColor = (line) => lineColors[line] || lineColors.default
const getDynamicRadius = (zoom) => Math.max(1.5, zoom - 8) * 0.9

// Chargement initial
onMounted(async () => {
  await fetchData()
  if (leafletMap.value) {
    acpmLayer.value = L.layerGroup().addTo(leafletMap.value)
  }
})

async function fetchData() {
  const nodesRes = await fetch('http://localhost:5001/api/nodesV2')
  stations.value = await nodesRes.json()
  for (const key of Object.keys(stations.value)) {
    normalizedStationKeys[normalizeName(key)] = key
  }
  const edgesRes = await fetch('http://localhost:5001/api/edgesV2')
  edges.value = await edgesRes.json()

  initMap()
}

function initMap() {
  leafletMap.value = L.map('map').setView([48.8566, 2.3522], 12)

  L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=RjuetPKSahj1157fZGDH', {
    attribution: '&copy; MapTiler',
    tileSize: 512,
    zoomOffset: -1
  }).addTo(leafletMap.value)

  leafletMap.value.on('zoomend', () => {
    const zoom = leafletMap.value.getZoom()
    stationCircles.forEach(c => c.setRadius(getDynamicRadius(zoom)))
  })

  for (const [id, station] of Object.entries(stations.value)) {
    const circle = L.circleMarker([station.latitude, station.longitude], {
      radius: getDynamicRadius(leafletMap.value.getZoom()),
      fillColor: '#00e1d6',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9
    })
      .bindPopup(`<b>${station.nom}</b><br>Lignes : ${station.lignes.join(', ')}`)
      .addTo(leafletMap.value)

    circle._stationId = id
    stationCircles.push(circle)
  }

  edges.value.forEach(edge => {
    const from = stations.value[normalizeId(edge.node0)]
    const to = stations.value[normalizeId(edge.node1)]
    if (!from || !to) return

    const color = getLineColor(from.lignes?.[0])
    const segment = L.polyline([[from.latitude, from.longitude], [to.latitude, to.longitude]], {
      color,
      weight: 3,
      opacity: 1
    }).addTo(leafletMap.value)
    backgroundLines.push(segment)
  })
}

async function fetchPath() {
  if (!startId.value || !endId.value) {
    alert('Veuillez sélectionner les deux stations.')
    return
  }

  const res = await fetch(`http://localhost:5001/api/pathV2?start_id=${startId.value}&end_id=${endId.value}`)
  const data = await res.json()
  currentPath.value = data.path

  if (!leafletMap.value) return

  if (pathLayer) leafletMap.value.removeLayer(pathLayer)
  pathLayer = L.layerGroup()

  backgroundLines.forEach(line => line.setStyle({ opacity: 0.1 }))
  const pathSet = new Set(data.path)

  stationCircles.forEach(circle => {
    if (pathSet.has(circle._stationId)) {
      circle.setStyle({ opacity: 1, fillOpacity: 0.9 }).addTo(leafletMap.value)
    } else {
      leafletMap.value.removeLayer(circle)
    }
  })

  for (let i = 0; i < data.path.length - 1; i++) {
    const stationA = stations.value[data.path[i]]
    const stationB = stations.value[data.path[i + 1]]
    if (!stationA || !stationB) continue

    const commonLine = stationA.lignes.find(l => stationB.lignes.includes(l)) || 'default'
    const color = getLineColor(commonLine)

    const segment = L.polyline([[stationA.latitude, stationA.longitude], [stationB.latitude, stationB.longitude]], {
      color,
      weight: 6,
      opacity: 1
    }).addTo(pathLayer)
  }

  pathLayer.addTo(leafletMap.value)

  const bounds = data.path.map(id => {
    const s = stations.value[id]
    return s ? [s.latitude, s.longitude] : null
  }).filter(Boolean)

  if (bounds.length > 0) {
    leafletMap.value.fitBounds(L.latLngBounds(bounds).pad(0.2))
  }
}

const normalizedStationKeys = {}

function findStationKey(nameWithoutSuffix) {
  const normName = normalizeName(nameWithoutSuffix)
  for (const normKey in normalizedStationKeys) {
    if (normKey.startsWith(normName)) {
      return normalizedStationKeys[normKey]
    }
  }
  return null
}

async function fetchACPM() {
  console.log('→ Chargement ACPM...')

  if (!leafletMap.value || !acpmLayer.value) {
    console.warn('Carte ou couche ACPM non initialisée')
    return
  }

  const res = await fetch('http://localhost:5001/api/acpmV2')
  const data = await res.json()
  console.log('Réponse ACPM:', data)

  acpmEdges.value = data.mst || []
  totalWeight.value = acpmEdges.value.reduce((sum, edge) => sum + edge.weight, 0)
  acpmLayer.value.clearLayers()

  for (const edge of acpmEdges.value) {
    const keyA = findStationKey(edge.node0)
    const keyB = findStationKey(edge.node1)

    if (!keyA || !keyB) {
      console.warn('Station manquante pour l’edge', edge)
      continue
    }

    const stationA = stations.value[keyA]
    const stationB = stations.value[keyB]

    if (!stationA || !stationB) {
      console.warn('Station non trouvée pour clés', keyA, keyB)
      continue
    }
    if (!stationA.latitude || !stationA.longitude || !stationB.latitude || !stationB.longitude) {
      console.warn('Coordonnées invalides', stationA, stationB)
      continue
    }

    console.log('Ajout segment entre:', keyA, keyB)

    const segment = L.polyline([[stationA.latitude, stationA.longitude], [stationB.latitude, stationB.longitude]], {
      color: 'red',
      weight: 4,
      opacity: 1
    }).bindTooltip(`${Math.round(edge.weight / 60)} min`)

    acpmLayer.value.addLayer(segment)
  }
}




function resetPath() {
  if (pathLayer && leafletMap.value) {
    leafletMap.value.removeLayer(pathLayer)
    pathLayer = null
  }

  if (acpmLayer.value && leafletMap.value) {
    acpmLayer.value.clearLayers()
  }

  backgroundLines.forEach(line => line.setStyle({ opacity: 0.4 }))
  stationCircles.forEach(c => c.setStyle({ opacity: 1, fillOpacity: 0.9 }).addTo(leafletMap.value))

  currentPath.value = []
  acpmEdges.value = []
  totalWeight.value = 0
  startId.value = ''
  endId.value = ''
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

body {
  margin: 0;
  font-family: 'Inter', sans-serif;
  background: #005252;
  color: #ffffff;
}
html,
body {
  margin: 0;
  padding: 0;
  height: 100%;
  background: #043434 !important;
}
#container {
  display: flex;
  height: 100vh;
  width: 100vw;
  align-items: stretch;
  gap: 8px;
}

.panel {
  width: 25%;
  padding: 24px;
  background: #0d4e4c;
  color: #e5f6f5;
  overflow-y: auto;
  border-radius: 16px;
  height: 100vh;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

#map {
  width: 50%;
  height: 100vh;
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #d0fefb;
}

.label {
  font-weight: 500;
  margin-top: 12px;
  margin-bottom: 4px;
  color: #b9e8e6;
}

.select {
  padding: 10px;
  font-size: 14px;
  border: none;
  border-radius: 6px;
  width: 100%;
  background: #195c59;
  color: #ffffff;
}

.select option {
  background-color: #195c59;
  color: #ffffff;
}

.btn {
  padding: 10px;
  font-size: 14px;
  border-radius: 6px;
  border: none;
  background: #136b67;
  color: #ffffff;
  cursor: pointer;
  transition: 0.2s;
  margin-top: 8px;
}

.btn:hover {
  background: #0f524f;
}

.btn.primary {
  background-color: #17a391;
  color: white;
}

.btn.primary:hover {
  background-color: #148579;
}

#details h2 {
  font-size: 18px;
  margin-bottom: 12px;
  color: #d0fefb;
}

.duration {
  margin-bottom: 12px;
  font-weight: bold;
  color: #aefdf2;
}

#details ul {
  list-style: none;
  padding-left: 0;
}

#details li {
  padding: 6px 0;
  border-bottom: 1px solid #195c59;
}

.acpm-edge {
  font-size: 13px;
  color: #b9e8e6;
}

.badge {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}
</style>
