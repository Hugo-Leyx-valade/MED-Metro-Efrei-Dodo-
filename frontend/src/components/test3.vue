<template>
  <div id="app">
    <div id="container">
      <!-- Barre latérale gauche -->
      <aside id="sidebar">
        <!-- Bloc 1 : Formulaire -->
        <div class="form-section">
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

          <label class="label">Heure de départ :</label>
          <input v-model="departureTime" type="time" class="select" />
        </div>

        <!-- Bloc 2 : Boutons -->
        <div class="button-group">
          <button class="btn primary" @click="fetchPath">Afficher le chemin</button>
          <button class="btn" @click="resetPath">Réinitialiser</button>
          <button class="btn" @click="fetchKruskal">Afficher Kruskal</button>
        </div>

        <!-- Bloc 3 : Résumé du trajet -->
        <div
          class="trajet-summary"
          v-if="totalDuration !== null"
          @click="detailsVisible = !detailsVisible"
          :class="{ clickable: true }"
        >
          <p><strong>Départ :</strong> {{ formattedStartTime }}</p>
          <p><strong>Arrivée :</strong> {{ formattedArrivalTime }}</p>
          <p><strong>Durée :</strong> {{ totalDuration }} min</p>
          <p><strong>CO₂ :</strong> {{ co2Emission }} kg</p>
          <p>
            <strong>Avec une voiture vous auriez consommé : <br /></strong>
            {{ co2EmissionV }} kg de CO₂
          </p>
        </div>

        <!-- Bloc 4 : Détail de l’itinéraire -->
        <transition name="fade">
          <div v-if="detailsVisible && trajetDetails.length" class="trajet-details">
            <h3>Détail de l'itinéraire</h3>
            <ul>
              <li
                v-for="(etape, i) in trajetDetails"
                :key="i"
                :style="{
                  borderLeft: `4px solid ${etape[6] === 1 ? '#999' : lineColors[etape[1]] || lineColors.default}`,
                }"
              >
                <p>
                  <strong>{{ etape[2] }}</strong>
                </p>
                <p v-if="etape[6] === 0">
                  Ligne {{ etape[1] }} → <b>{{ stations[etape[3]]?.nom }}</b
                  ><br />
                  <small>Arrivée : {{ etape[5] }}</small>
                </p>
                <p v-else>
                  Correspondance → <b>{{ stations[etape[3]]?.nom }}</b
                  ><br />
                  <small>Arrivée : {{ etape[5] }}</small>
                </p>
              </li>
            </ul>
          </div>
        </transition>

        <!-- Bloc 5 : Résumé de Kruskal -->
        <div
          class="trajet-summary"
          v-if="kruskalSummary.edgeCount > 0"
          @click="kruskalDetailsVisible = !kruskalDetailsVisible"
          :class="{ clickable: true }"
        >
          <p>
            <strong>Arbre couvrant minimal trouvé :</strong> {{ kruskalSummary.edgeCount }} arêtes
          </p>
          <p><strong>Poids total :</strong> {{ formattedKruskalTime }}</p>
          <p><strong>CO₂ estimé (métro) :</strong> {{ co2Kruskal }} kg</p>
          <p><strong>En voiture :</strong> {{ co2KruskalV }} kg</p>
        </div>

        <!-- Détails de Kruskal -->
        <transition name="fade">
          <div v-if="kruskalDetailsVisible && filteredKruskalEdges.length" class="trajet-details">
            <h3>Exemple d’arêtes (10 premières)</h3>
            <ul>
              <li v-for="(edge, i) in filteredKruskalEdges" :key="i">
                {{ stations[edge.from].nom }} ⇄ {{ stations[edge.to].nom }} (poids :
                {{ edge.weight }})
              </li>
            </ul>
            <p v-if="filteredKruskalEdges.length === 0">Aucune arête affichable pour le moment.</p>
          </div>
        </transition>

        <!-- Bloc 6 : Source CO₂ -->
        <div class="co2-source">
          <a
            href="https://chair-energy-prosperity.org/wp-content/uploads/2019/01/emissions-de-co2-par-mode-de-transport.pdf"
            target="_blank"
            rel="noopener"
          >
            Source des données CO₂ : Chaire Énergie & Prospérité (2019)
          </a>
        </div>
      </aside>

      <!-- Carte à droite -->
      <div id="map" ref="map"></div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

// === Données réactives ===
const kruskalSummary = ref({
  edgeCount: 0,
  totalWeight: 0,
  exemples: [],
})

const stations = ref({})
const edges = ref([])

const startId = ref('')
const endId = ref('')
const departureTime = ref('08:00')

const totalDuration = ref(null)
const trajetDetails = ref([])
const detailsVisible = ref(false)
const kruskalDetailsVisible = ref(false)

let pathLayer = null
let networkLayer = null
let kruskalLayer = null

const leafletMap = ref(null)

// === Couleurs de lignes métro ===
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

// === Calculs dérivés ===
const co2Emission = computed(() =>
  totalDuration.value !== null ? (0.18 * (totalDuration.value / 60)).toFixed(3) : '',
)
const co2EmissionV = computed(() =>
  totalDuration.value !== null ? (6.5 * (totalDuration.value / 60)).toFixed(3) : '',
)

const co2Kruskal = computed(() => (0.18 * (kruskalSummary.value.totalWeight / 3600)).toFixed(3))
const co2KruskalV = computed(() => (6.5 * (kruskalSummary.value.totalWeight / 3600)).toFixed(3))

const formattedStartTime = computed(() =>
  trajetDetails.value.length ? trajetDetails.value[0][2] : '',
)
const formattedArrivalTime = computed(() =>
  trajetDetails.value.length ? trajetDetails.value.at(-1)[5] : '',
)

// ✅ Filtres sécurisés pour Kruskal (évite les erreurs de lecture)
const filteredKruskalEdges = computed(() =>
  kruskalSummary.value.exemples.filter(
    (edge) =>
      edge &&
      typeof edge === 'object' &&
      edge.from &&
      edge.to &&
      stations.value[edge.from] &&
      stations.value[edge.to],
  ),
)

// === Initialisation ===
onMounted(fetchData)

async function fetchData() {
  const nodesRes = await fetch('http://localhost:5001/api/nodesV3')
  stations.value = await nodesRes.json()

  const edgesRes = await fetch('http://localhost:5001/api/edgesV3')
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

  // Stations
  for (const [id, station] of Object.entries(stations.value)) {
    L.circleMarker([station.latitude, station.longitude], {
      radius: 3,
      fillColor: '#007bff',
      color: '#004080',
      weight: 1,
      fillOpacity: 1,
    })
      .bindPopup(`<b>${station.nom}</b><br>Lignes : ${station.lignes.join(', ')}`)
      .addTo(leafletMap.value)
  }

  // Réseau
  const segments = []
  edges.value.forEach((edge) => {
    const from = stations.value[edge.from]
    const to = stations.value[edge.to]

    if (from && to) {
      const line = from.lignes.length > 0 ? from.lignes[0] : 'default'
      const color = lineColors[line] || lineColors.default

      const segment = L.polyline(
        [
          [from.latitude, from.longitude],
          [to.latitude, to.longitude],
        ],
        {
          color,
          weight: 2,
          opacity: 0.2,
          interactive: false,
        },
      )
      segments.push(segment)
    }
  })

  networkLayer = L.featureGroup(segments).addTo(leafletMap.value)
}

const formattedKruskalTime = computed(() => {
  const totalSeconds = Math.round(kruskalSummary.value.totalWeight)

  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60

  const parts = []
  if (hours > 0) parts.push(`${hours}h`)
  if (minutes > 0) parts.push(`${minutes}m`)
  if (seconds > 0 || parts.length === 0) parts.push(`${seconds}s`)

  return parts.join(' ')
})

async function fetchPath() {
  if (!startId.value || !endId.value) {
    alert('Veuillez sélectionner les deux stations.')
    return
  }

  const startStation = stations.value[startId.value]
  const endStation = stations.value[endId.value]
  const depart = departureTime.value + ':00'

  const response = await fetch(
    `http://localhost:5001/api/pathV3?start_name=${startStation.nom}&start_ligne=${startStation.lignes[0]}&end_name=${endStation.nom}&end_ligne=${endStation.lignes[0]}&heure_depart=${depart}`,
  )

  const data = await response.json()

  if (!data || !Array.isArray(data.chemin)) {
    alert('Aucun chemin n’a été retourné.')
    return
  }

  totalDuration.value = data.duree_totale
  trajetDetails.value = data.chemin
  detailsVisible.value = true

  if (!leafletMap.value) {
    alert('Carte non encore initialisée.')
    return
  }

  if (pathLayer) {
    leafletMap.value.removeLayer(pathLayer)
  }

  const latlngs = []
  const colors = []

  data.chemin.forEach((step) => {
    const [fromId, fromLigne, fromHeure, toId, toLigne, toHeure, type] = step
    const fromStation = stations.value[fromId]
    const toStation = stations.value[toId]

    if (fromStation && toStation) {
      latlngs.push([
        [fromStation.latitude, fromStation.longitude],
        [toStation.latitude, toStation.longitude],
      ])
      colors.push(type === 1 ? 'red' : lineColors[fromLigne] || lineColors.default)
    }
  })

  const polylines = latlngs.map((segment, i) =>
    L.polyline(segment, {
      color: colors[i],
      weight: 6,
      opacity: 1,
      dashArray: colors[i] === 'red' ? '4, 4' : null,
    }).addTo(leafletMap.value),
  )

  pathLayer = L.featureGroup(polylines)
  leafletMap.value.addLayer(pathLayer)
  leafletMap.value.fitBounds(pathLayer.getBounds())
}

async function fetchKruskal() {
  const res = await fetch('http://localhost:5001/api/ACPMV3')
  const data = await res.json()

  const kruskalEdges = data.mst

  if (!Array.isArray(kruskalEdges)) {
    alert("Erreur lors de la récupération de l'arbre de Kruskal.")
    return
  }

  if (kruskalLayer) {
    leafletMap.value.removeLayer(kruskalLayer)
    kruskalLayer = null
  }

  const segments = []

  kruskalEdges.forEach((edge) => {
    const from = stations.value[edge.from]
    const to = stations.value[edge.to]

    if (from && to) {
      const segment = L.polyline(
        [
          [from.latitude, from.longitude],
          [to.latitude, to.longitude],
        ],
        {
          color: '#e6007e',
          weight: 4,
          opacity: 0.7,
          dashArray: '4 6',
        },
      ).addTo(leafletMap.value)

      segments.push(segment)
    }
  })

  kruskalLayer = L.featureGroup(segments)
  leafletMap.value.fitBounds(kruskalLayer.getBounds())

  const poidsTotal = kruskalEdges.reduce((acc, e) => acc + e.weight, 0)

  kruskalSummary.value = {
    edgeCount: data.edge_count,
    totalWeight: poidsTotal,
    exemples: kruskalEdges.slice(0, 10),
  }
}

function resetPath() {
  // Supprime les couches de chemin, Kruskal et réseau
  if (pathLayer && leafletMap.value) {
    leafletMap.value.removeLayer(pathLayer)
    pathLayer = null
  }
  if (kruskalLayer && leafletMap.value) {
    leafletMap.value.removeLayer(kruskalLayer)
    kruskalLayer = null
  }
  if (networkLayer && leafletMap.value) {
    leafletMap.value.removeLayer(networkLayer)
    networkLayer = null
  }

  // Supprime complètement la carte Leaflet
  if (leafletMap.value) {
    leafletMap.value.remove()
    leafletMap.value = null
  }

  // Réinitialise les champs
  startId.value = ''
  endId.value = ''
  departureTime.value = '08:00'
  trajetDetails.value = []
  totalDuration.value = null
  detailsVisible.value = false
  kruskalSummary.value = {
    edgeCount: 0,
    totalWeight: 0,
    exemples: [],
  }
  kruskalDetailsVisible.value = false

  // Recharge la carte et les données
  fetchData()
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

#app {
  margin: 0 !important;
  padding: 0 !important;
  width: 100vw;
}

html,
body {
  margin: 0;
  padding: 0;
  font-family: 'Inter', sans-serif;
  background: #104343;
  color: #f0f0f0;
  height: 100vh;
  width: 100vw;
}

#container {
  display: flex;
  flex-direction: row;
  width: 100vw;
}

#sidebar {
  width: 30%;
  max-width: 460px;
  min-width: 320px;
  padding: 16px 20px;
  background: #104343;
  border-right: 1px solid #1b5050;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow-y: auto;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  color: #f0f0f0;
}

#map {
  flex: 1;
  height: 100vh;
  padding: 0;
  margin: 0;
}

.title {
  font-size: 22px;
  font-weight: 600;
  color: #ffffff;
}

.label {
  font-weight: 500;
  margin-top: 12px;
  margin-bottom: 4px;
  color: #ffffff;
}

.select {
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 6px;
  width: 100%;
  background: #f8f9fa;
  color: #222;
}

.btn {
  padding: 10px;
  font-size: 14px;
  border-radius: 6px;
  border: none;
  background: #1b5050;
  color: #ffffff;
  cursor: pointer;
  transition: 0.2s;
}

.btn:hover {
  background: #237272;
}

.btn.primary {
  background-color: #007bff;
  color: white;
}

.btn.primary:hover {
  background-color: #0056b3;
}

/* === Résumés et détails (trajet et Kruskal) === */

.trajet-summary {
  background: #1b5050;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
  border: 1px solid #104343;
  color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trajet-summary:hover {
  background: #237272;
}

.trajet-summary p {
  margin: 4px 0;
  font-size: 14px;
  color: #f0f0f0;
}

.trajet-details {
  background: #1b5050;
  border-radius: 8px;
  padding: 10px 14px;
  border: 1px solid #104343;
  overflow-y: auto;
  max-height: 40vh;
  color: #ffffff;
}

.trajet-details h3 {
  margin-top: 0;
  font-size: 16px;
  margin-bottom: 12px;
  color: #ffffff;
}

.trajet-details ul {
  padding-left: 0;
  list-style: none;
}

.trajet-details li {
  padding: 10px;
  margin-bottom: 10px;
  background: #104343;
  border-radius: 6px;
  border-left: 5px solid #999;
  box-shadow: 0 0 2px rgba(0, 0, 0, 0.1);
  color: #f0f0f0;
}

.trajet-details p {
  margin: 2px 0;
  font-size: 14px;
  color: #f0f0f0;
}

/* Form section */
.form-section {
  border-top: 1px solid #1b5050;
  padding-top: 12px;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

/* Source CO2 */
.co2-source {
  margin-top: auto;
  padding: 12px 0 0 4px;
  font-size: 12px;
  color: #ccc;
  border-top: 1px solid #1b5050;
}

.co2-source a {
  color: #a5e3e3;
  text-decoration: none;
}

.co2-source a:hover {
  text-decoration: underline;
}

/* Boutons groupe */
.button-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
</style>
