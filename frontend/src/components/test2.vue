<template>
  <div id="container">
    <div id="sidebar">
      <h1>Stations et liens sur la carte</h1>
      <!-- Tu peux ajouter d'autres infos ici si besoin -->
    </div>
    <div id="map" ref="map"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const map = ref(null)
const stations = ref({})
const edges = ref([])

async function fetchData() {
  const nodesRes = await fetch('http://localhost:5000/api/nodesV2')
  stations.value = await nodesRes.json()

  const edgesRes = await fetch('http://localhost:5000/api/edgesV2')
  edges.value = await edgesRes.json()
  
  initMap()
}

function initMap() {
  map.value = L.map('map').setView([48.8566, 2.4], 12)
  L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=RjuetPKSahj1157fZGDH', {
    attribution: '&copy; <a href="https://www.maptiler.com/copyright/">MapTiler</a>',
    tileSize: 512,
    zoomOffset: -1,
    minZoom: 1,
    maxZoom: 20
  }).addTo(map.value)

  // Stations
  for (const [id, station] of Object.entries(stations.value)) {
    L.circleMarker([station.latitude, station.longitude], {
      radius: 2,
      fillColor: '#007bff',
      color: '#004080',
      weight: 1,
      fillOpacity: 1,
      opacity: 1
    })
    .bindPopup(`<b>${station.nom}</b><br>Lignes: ${station.lignes.join(', ')}`)
    .addTo(map.value)
  }

  const lineColors = {
    '1': '#ffcd00',
    '2': '#0055c8',
    '3': '#837902',
    '4': '#932990',
    '5': '#ff7e2e',
    '6': '#6ec4e8',
    '7': '#f5a2bd',
    '8': '#c9910d',
    '9': '#d5c900',
    '10': '#e4b12f',
    '11': '#704b1c',
    '12': '#007852',
    '13': '#99d4e4',
    '14': '#62259d',
    '7B': '#ff7f50',
    'default': '#ffffff'
  }

  edges.value.forEach(edge => {
    const from = stations.value[edge.node0]
    const to = stations.value[edge.node1]

    if (from && to) {
      const firstLine = from.lignes.length > 0 ? from.lignes[0] : 'default'
      const color = lineColors[firstLine] || lineColors['default']

      L.polyline([
        [from.latitude, from.longitude],
        [to.latitude, to.longitude]
      ], {
        color: color,
        weight: 3,
        opacity: 0.7
      }).addTo(map.value)
    } else {
      console.warn(`Station manquante pour edge`, edge)
    }
  })
}

onMounted(fetchData)
</script>

<style>
#container {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

#sidebar {
  width: 30%;
  padding: 20px;
  background-color: #f5f5f500;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

#map {
  width: 70%;
  height: 100vh;
}
</style>
