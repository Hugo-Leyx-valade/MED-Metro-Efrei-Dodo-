<template>
  <div class="map-container">
    <!-- Contrôles -->
    <div class="controls">
      <h3>Choix des stations</h3>
      <label>
        De :
        <select v-model="selectedFrom">
          <option disabled value="">Sélectionner...</option>
          <option v-for="station in points" :key="station.id" :value="station">
            {{ station.name }} (Ligne {{ station.line }})
          </option>
        </select>
      </label>

      <label>
        À :
        <select v-model="selectedTo">
          <option disabled value="">Sélectionner...</option>
          <option v-for="station in points" :key="station.id" :value="station">
            {{ station.name }} (Ligne {{ station.line }})
          </option>
        </select>
      </label>

      <button @click="computeShortestPath">Calculer le plus court chemin</button>
      <button @click="computeACPM">Calculer ACPM</button>

      <p v-if="shortestweight">🛤️ Durée chemin : {{ (shortestweight / 60).toFixed(1) }} minutes</p>
      <p v-if="totalWeight">🌐 Poids ACPM : {{ (totalWeight / 60).toFixed(1) }} minutes</p>
    </div>

    <!-- Liste du chemin -->
    <div class="path-box">
      <h4>🧭 Chemin :</h4>
      <ul>
        <li v-for="(id, index) in shortestPath" :key="id" :class="getStepClass(index)">
          <span
            class="circle"
            :style="{ backgroundColor: getHexColorByLine(getStationLineById(id)) }"
          ></span>
          <strong v-if="index === 0 || index === shortestPath.length - 1">
            {{ getStationNameById(id) }}
          </strong>
          <span v-else>
            {{ getStationNameById(id) }}
          </span>
        </li>
      </ul>
    </div>

    <!-- Carte SVG -->
    <svg class="map-svg">
      <line
        v-for="(edge, index) in edges"
        :key="'bg-' + index"
        :x1="points[edge.node0]?.x / 1.5"
        :y1="points[edge.node0]?.y / 1.5"
        :x2="points[edge.node1]?.x / 1.5"
        :y2="points[edge.node1]?.y / 1.5"
        :stroke="getLineColor(points[edge.node0]?.line, 0.2)"
        stroke-width="4"
      />
      <line
        v-for="(edge, index) in visiblePathEdges"
        :key="'fg-' + index"
        :x1="points[edge.node0]?.x / 1.5"
        :y1="points[edge.node0]?.y / 1.5"
        :x2="points[edge.node1]?.x / 1.5"
        :y2="points[edge.node1]?.y / 1.5"
        :stroke="getLineColor(points[edge.node0]?.line, 1)"
        stroke-width="5.5"
        class="highlight-path"
      />
      <circle
        v-for="(point, index) in points"
        :key="'pt-' + index"
        :cx="point.x / 1.5"
        :cy="point.y / 1.5"
        r="4"
        fill="white"
        :class="isPointInPath(point.id) ? 'highlight-point' : ''"
      >
        <title>{{ point.name }}</title>
      </circle>
      <g v-if="selectedFrom">
        <circle
          :cx="selectedFrom.x / 1.5"
          :cy="selectedFrom.y / 1.5"
          r="8"
          fill="#00ffcc"
          stroke="black"
          stroke-width="2"
        />
        <text
          :x="selectedFrom.x / 1.5 + 10"
          :y="selectedFrom.y / 1.5 - 10"
          font-size="14"
          fill="white"
        >
          {{ selectedFrom.name }}
        </text>
      </g>
      <g v-if="selectedTo">
        <circle
          :cx="selectedTo.x / 1.5"
          :cy="selectedTo.y / 1.5"
          r="8"
          fill="#ff5e5e"
          stroke="black"
          stroke-width="2"
        />
        <text :x="selectedTo.x / 1.5 + 10" :y="selectedTo.y / 1.5 - 10" font-size="14" fill="white">
          {{ selectedTo.name }}
        </text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const points = ref([])
const edges = ref([])
const selectedFrom = ref('')
const selectedTo = ref('')
const shortestPath = ref([])
const shortestweight = ref(null)
const totalWeight = ref(null)
const shortestPathEdges = ref([])
const visiblePathEdges = ref([])

async function fetchData() {
  try {
    const res1 = await axios.get('http://localhost:5000/api/edges')
    const res2 = await axios.get('http://localhost:5000/api/nodes')
    edges.value = res1.data.map((e) => ({
      node0: parseInt(e.node0),
      node1: parseInt(e.node1),
      weight: parseInt(e.weight),
    }))
    points.value = res2.data
  } catch (error) {
    console.error('Erreur récupération données :', error)
  }
}

onMounted(fetchData)

async function computeShortestPath() {
  if (!selectedFrom.value || !selectedTo.value) {
    alert('Veuillez choisir deux stations')
    return
  }
  try {
    const res = await axios.get(
      `http://localhost:5000/api/path?start_id=${selectedFrom.value.id}&end_id=${selectedTo.value.id}`,
    )
    shortestPath.value = res.data.path
    shortestweight.value = res.data.total_weight
    shortestPathEdges.value = []
    for (let i = 0; i < shortestPath.value.length - 1; i++) {
      const node0 = shortestPath.value[i]
      const node1 = shortestPath.value[i + 1]
      shortestPathEdges.value.push({ node0, node1 })
    }
    visiblePathEdges.value = shortestPathEdges.value
  } catch (err) {
    console.error('Erreur chemin :', err)
  }
}

async function computeACPM() {
  try {
    const res = await axios.get('http://localhost:5000/api/acpm')
    shortestPathEdges.value = res.data.mst.map((e) => ({
      node0: parseInt(e.node0),
      node1: parseInt(e.node1),
    }))
    totalWeight.value = res.data.total_weight
    visiblePathEdges.value = shortestPathEdges.value
  } catch (err) {
    console.error('Erreur ACPM :', err)
  }
}

function getLineColor(line, opacity = 1) {
  const hex = getHexColorByLine(line)
  return hexToRgba(hex, opacity)
}

function getHexColorByLine(line) {
  const colors = {
    1: '#ffcd00',
    2: '#0055c8',
    3: '#837902',
    4: '#932990',
    5: '#ff7e2e',
    6: '#6ec4e8',
    7: '#f5a2bd',
    8: '#c9910d',
    9: '#d5c900',
    10: '#e4b12f',
    11: '#704b1c',
    12: '#007852',
    13: '#99d4e4',
    14: '#62259d',
  }
  return colors[line] || '#ffffff'
}

function hexToRgba(hex, opacity) {
  const bigint = parseInt(hex.replace('#', ''), 16)
  const r = (bigint >> 16) & 255
  const g = (bigint >> 8) & 255
  const b = bigint & 255
  return `rgba(${r}, ${g}, ${b}, ${opacity})`
}

function isPointInPath(id) {
  return shortestPath.value.includes(id)
}
function getStationNameById(id) {
  const intId = parseInt(id)
  const station = points.value.find((p) => parseInt(p.id) === intId)
  return station ? station.name : 'Inconnu'
}
function getStationLineById(id) {
  const station = points.value.find((p) => parseInt(p.id) === parseInt(id))
  return station?.line || 0
}
function getStepClass(index) {
  if (index === 0) return 'start'
  if (index === shortestPath.value.length - 1) return 'end'
  return 'middle'
}
</script>

<style scoped>
.map-container {
  display: flex;
  height: 100vh;
  background-color: #0b2e2c;
  color: white;
  font-family: 'Segoe UI', sans-serif;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
}

.controls {
  flex: 0 0 300px;
  background-color: rgba(18, 57, 52, 0.92);
  padding: 20px;
  margin: 20px 0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
}

.controls select,
.controls button {
  padding: 10px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
}

.controls button {
  background-color: #195d56;
  color: white;
  cursor: pointer;
}
.controls button:hover {
  background-color: #21897e;
}

.path-box {
  flex: 0 0 260px;
  background-color: rgba(255, 255, 255, 0.08);
  padding: 20px;
  margin: 20px 0;
  border-radius: 10px;
  overflow-y: auto;
  max-height: 90vh;
}

.path-box h4 {
  margin-bottom: 10px;
  font-size: 1.1rem;
}
.path-box ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.path-box li {
  display: flex;
  align-items: center;
  margin: 6px 0;
  font-size: 0.95rem;
}
.path-box .circle {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 10px;
}

.map-svg {
  flex-grow: 1;
  height: 100vh;
  width: 100%;
}

.highlight-path {
  /* no animation */
}

.highlight-point {
  stroke: yellow;
  stroke-width: 2;
  r: 6;
}
</style>
