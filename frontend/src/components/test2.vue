<template>
  <div id="app">
    <h1>Stations de métro sur la carte</h1>
    <div id="map" ref="map" style="height: 600px;"></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const map = ref(null)
const stations = ref([])

// Exemple de données (à remplacer par un fetch depuis backend ou fichier JSON)
stations.value = [
  { nom: 'Station A', latitude: 48.8566, longitude: 2.3522, lignes: ['7', '3'] },
  { nom: 'Station B', latitude: 48.857, longitude: 2.36, lignes: ['1'] },
  // ajoute ici tes stations
]

onMounted(() => {
  map.value = L.map('map').setView([48.8566, 2.3522], 12)

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
  }).addTo(map.value)

  // Ajout des marqueurs pour chaque station
  stations.value.forEach(station => {
    L.circleMarker([station.latitude, station.longitude], {
      radius: 6,
      fillColor: '#007bff',
      color: '#004080',
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8
    })
    .bindPopup(`<strong>${station.nom}</strong><br>Lignes : ${station.lignes.join(', ')}`)
    .addTo(map.value)
  })
})
</script>

<style>
#map {
  width: 100%;
}
</style>
