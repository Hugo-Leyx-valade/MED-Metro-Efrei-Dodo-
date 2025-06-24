<template>
  <div id="container">
    <aside id="sidebar">
      <h1 class="title">🗺️ Calcul d’itinéraire Métro</h1>

      <label class="label">Station de départ :</label>
      <select v-model="startId" class="select">
        <option disabled value="">-- Sélectionner --</option>
        <option v-for="(station, id) in stations" :key="id" :value="id">
          {{ station.nom }} (Ligne{{ station.lignes.length > 1 ? 's' : '' }} : {{ station.lignes.join(', ') }})
        </option>
      </select>

      <label class="label">Station d’arrivée :</label>
      <select v-model="endId" class="select">
        <option disabled value="">-- Sélectionner --</option>
        <option v-for="(station, id) in stations" :key="id" :value="id">
          {{ station.nom }} (Ligne{{ station.lignes.length > 1 ? 's' : '' }} : {{ station.lignes.join(', ') }})
        </option>
      </select>

      <button class="btn primary" @click="fetchPath">Afficher le chemin</button>
      <button class="btn" @click="resetPath">Réinitialiser</button>
    </aside>

    <div id="map" ref="map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const leafletMap = ref(null)
const stations = ref({})
const edges = ref([])

const startId = ref('')
const endId = ref('')
let pathLayer = null

const lineColors = {
  '1': '#ffcd00',
  '2': '#0055c8',
  '3': '#837902',
  '4': '#932990',
  '5': '#ff7e2e',
  '6': '#6ec4e8',
  '7': '#f5a2bd',
  '7B': '#ff7f50',
  '8': '#c9910d',
  '9': '#d5c900',
  '10': '#e4b12f',
  '11': '#704b1c',
  '12': '#007852',
  '13': '#99d4e4',
  '14': '#62259d',
  'default': '#999'
}

async function fetchData() {
  const nodesRes = await fetch('http://localhost:5000/api/nodesV2')
  stations.value = await nodesRes.json()

  const edgesRes = await fetch('http://localhost:5000/api/edgesV2')
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

  for (const [id, station] of Object.entries(stations.value)) {
    L.circleMarker([station.latitude, station.longitude], {
      radius: 3,
      fillColor: '#007bff',
      color: '#004080',
      weight: 1,
      fillOpacity: 1
    })
      .bindPopup(`<b>${station.nom}</b><br>Lignes : ${station.lignes.join(', ')}`)
      .addTo(leafletMap.value)
  }

  edges.value.forEach(edge => {
    const from = stations.value[edge.node0]
    const to = stations.value[edge.node1]

    if (from && to) {
      const line = from.lignes.length > 0 ? from.lignes[0] : 'default'
      const color = lineColors[line] || lineColors.default

      L.polyline([
        [from.latitude, from.longitude],
        [to.latitude, to.longitude]
      ], {
        color,
        weight: 2,
        opacity: 0.6
      }).addTo(leafletMap.value)
    }
  })
}

async function fetchPath() {
  if (!startId.value || !endId.value) {
    alert('Veuillez sélectionner les deux stations.')
    return
  }

  const response = await fetch(`http://localhost:5000/api/pathV2?start_id=${startId.value}&end_id=${endId.value}`)
  const data = await response.json()
  console.log('Chemin trouvé:', data)

  if (!leafletMap.value) {
    alert("Carte non encore initialisée.")
    return
  }

  if (pathLayer) {
    leafletMap.value.removeLayer(pathLayer)
  }

  const latlngs = data.path.map(id => {
    const s = stations.value[id]
    return [s.latitude, s.longitude]
  })

  console.log('LatLngs:', latlngs)

  pathLayer = L.polyline(latlngs, {
    color: 'red',
    weight: 5,
    opacity: 1
  }).addTo(leafletMap.value)

  leafletMap.value.fitBounds(pathLayer.getBounds())
}

function resetPath() {
  if (pathLayer && leafletMap.value) {
    leafletMap.value.removeLayer(pathLayer)
    pathLayer = null
  }
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
  background: #f8f9fa;
}

#container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

#sidebar {
  width: 30%;
  padding: 24px;
  background: #ffffff;
  border-right: 1px solid #ddd;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
}

#map {
  width: 70%;
  height: 100vh;
}

.title {
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.label {
  font-weight: 500;
  margin-top: 12px;
  margin-bottom: 4px;
}

.select {
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 6px;
  width: 100%;
  background: #fff;
}

.btn {
  padding: 10px;
  font-size: 14px;
  border-radius: 6px;
  border: none;
  background: #eee;
  cursor: pointer;
  transition: 0.2s;
}

.btn:hover {
  background: #ddd;
}

.btn.primary {
  background-color: #007bff;
  color: white;
}

.btn.primary:hover {
  background-color: #0056b3;
}
</style>
