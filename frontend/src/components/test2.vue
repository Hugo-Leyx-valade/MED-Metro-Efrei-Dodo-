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
    </div>

    <div id="map" ref="map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const leafletMap = ref(null)
const stations = ref({})
const edges = ref([])

const startId = ref('')
const endId = ref('')
const currentPath = ref([])

const estimatedDuration = computed(() => {
  return currentPath.value.length > 1 ? currentPath.value.length - 1 : 0
})

let pathLayer = null

let backgroundLines = []
let stationCircles = []

const lineColors = {
  1: '#ffcd00',
  2: '#0055c8',
  3: '#837902',
  4: '#932990',
  5: '#ff7e2e',
  6: '#6ec4e8',
  7: '#f5a2bd',
  '7B': '#ff7f50',
  8: '#c9910d',
  9: '#d5c900',
  10: '#e4b12f',
  11: '#704b1c',
  12: '#007852',
  13: '#99d4e4',
  14: '#62259d',
  default: '#999',
}

function getLineColor(line) {
  return lineColors[line] || lineColors.default
}

function getDynamicRadius(zoom) {
  return Math.max(1.5, zoom - 8) * 0.9
}

async function fetchData() {
  const nodesRes = await fetch('http://localhost:5001/api/nodesV2')
  stations.value = await nodesRes.json()

  const edgesRes = await fetch('http://localhost:5001/api/edgesV2')
  edges.value = await edgesRes.json()

  initMap()
}

function initMap() {
  leafletMap.value = L.map('map').setView([48.8566, 2.3522], 12)
  L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=RjuetPKSahj1157fZGDH', {
    attribution: '&copy; MapTiler',
    tileSize: 512,
    zoomOffset: -1,
  }).addTo(leafletMap.value)

  leafletMap.value.on('zoomend', () => {
    const zoom = leafletMap.value.getZoom()
    stationCircles.forEach((circle) => {
      circle.setRadius(getDynamicRadius(zoom))
    })
  })

  for (const [id, station] of Object.entries(stations.value)) {
    const circle = L.circleMarker([station.latitude, station.longitude], {
      radius: getDynamicRadius(leafletMap.value.getZoom()),
      fillColor: '#00e1d6',
      color: '#ffffff',
      weight: 2,
      opacity: 1,
      fillOpacity: 0.9,
    })
      .bindPopup(`<b>${station.nom}</b><br>Lignes : ${station.lignes.join(', ')}`)
      .addTo(leafletMap.value)

    circle._stationId = id
    stationCircles.push(circle)
  }

  edges.value.forEach((edge) => {
    const from = stations.value[edge.node0]
    const to = stations.value[edge.node1]

    if (from && to) {
      const line = from.lignes.length > 0 ? from.lignes[0] : 'default'
      const color = lineColors[line] || lineColors.default

      const lineSegment = L.polyline(
        [
          [from.latitude, from.longitude],
          [to.latitude, to.longitude],
        ],
        {
          color,
          weight: 3,
          opacity: 0.4,
        },
      ).addTo(leafletMap.value)

      backgroundLines.push(lineSegment)
    }
  })
}

async function fetchPath() {
  if (!startId.value || !endId.value) {
    alert('Veuillez sélectionner les deux stations.')
    return
  }

  const response = await fetch(
    `http://localhost:5001/api/pathV2?start_id=${startId.value}&end_id=${endId.value}`,
  )
  const data = await response.json()
  currentPath.value = data.path

  if (!leafletMap.value) {
    alert('Carte non encore initialisée.')
    return
  }

  if (pathLayer) {
    leafletMap.value.removeLayer(pathLayer)
  }

  backgroundLines.forEach((line) => line.setStyle({ opacity: 0.1 }))

  const pathSet = new Set(data.path)
  stationCircles.forEach((circle) => {
    if (pathSet.has(circle._stationId)) {
      circle.setStyle({ opacity: 1, fillOpacity: 0.9 })
      circle.addTo(leafletMap.value)
    } else {
      leafletMap.value.removeLayer(circle)
    }
  })

  pathLayer = L.layerGroup()

  for (let i = 0; i < data.path.length - 1; i++) {
    const idA = data.path[i]
    const idB = data.path[i + 1]

    const stationA = stations.value[idA]
    const stationB = stations.value[idB]

    if (!stationA || !stationB) continue

    const commonLines = stationA.lignes.filter((l) => stationB.lignes.includes(l))
    const line = commonLines.length > 0 ? commonLines[0] : 'default'
    const color = lineColors[line] || lineColors.default

    const segment = L.polyline(
      [
        [stationA.latitude, stationA.longitude],
        [stationB.latitude, stationB.longitude],
      ],
      {
        color,
        weight: 6,
        opacity: 1,
      },
    )

    segment.addTo(pathLayer)
  }

  pathLayer.addTo(leafletMap.value)

  const bounds = []
  for (let i = 0; i < data.path.length; i++) {
    const s = stations.value[data.path[i]]
    if (s) bounds.push([s.latitude, s.longitude])
  }
  leafletMap.value.fitBounds(L.latLngBounds(bounds).pad(0.2))
}

function resetPath() {
  if (pathLayer && leafletMap.value) {
    leafletMap.value.removeLayer(pathLayer)
    pathLayer = null
  }

  backgroundLines.forEach((line) => line.setStyle({ opacity: 0.4 }))

  stationCircles.forEach((circle) => {
    circle.setStyle({ opacity: 1, fillOpacity: 0.9 })
    circle.addTo(leafletMap.value)
  })

  currentPath.value = []
  startId.value = ''
  endId.value = ''
}

onMounted(fetchData)
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
  height: 100vh; /* occupe toute la hauteur */
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

.badge {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}
</style>
