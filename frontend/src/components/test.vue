<template>
  
  <div class="map-container">

    <div class="controls">
  <h3>Calcul de chemin</h3>
  <label>
    De :
    <select v-model="selectedFrom">
      <option disabled value="">Sélectionner...</option>
      <option v-for="station in points" :key="station.id" :value="station">
        Station : {{ station.name }} Ligne : {{ station.line }}
      </option>
    </select>
  </label>

  <label>
    À :
    <select v-model="selectedTo">
      <option disabled value="">Sélectionner...</option>
      <option v-for="station in points" :key="station.id" :value="station">
        Station : {{ station.name }} Ligne : {{ station.line }}
      </option>
    </select>
  </label>

  <button @click="computeShortestPath">Calculer</button>
</div>
    <!-- Image utilisée pour le placement, invisible -->
    <img ref="imageRef" src="../assets/metrof_r.png" class="map-image" />

    <!-- Lignes entre les points -->
    <svg class="map-svg">
      <line
        v-for="(edge, index) in edges"
        :key="index"
        :x1="getPoint(edge.from.id)?.x/1.5"
        :y1="getPoint(edge.from.id)?.y/1.5"
        :x2="getPoint(edge.to.id)?.x/1.5"
        :y2="getPoint(edge.to.id)?.y/1.5"
        :stroke="getLineColor(edge.from.line)"
        stroke-width="2"
      />

      <!-- Chemin le plus court en rouge -->
      <line
        v-for="(edge, index) in shortestPathEdges"
        :key="'path-' + index"
        :x1="getPoint(edge.from.id)?.x / 1.5"
        :y1="getPoint(edge.from.id)?.y / 1.5"
        :x2="getPoint(edge.to.id)?.x / 1.5"
        :y2="getPoint(edge.to.id)?.y / 1.5"
        stroke="red"
        stroke-width="4"
      />
    </svg>

    <!-- Points -->
    <div
      v-for="(point, index) in points"
      :key="index"
      class="point"
      :style="{ top: point.y/1.5 + 'px', left: point.x/1.5 + 'px', background: 'white' }"
      :title="point.name"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const points = ref([])
const edges = ref([])
const imageRef = ref(null)

async function fetchData() {
  try {
    const res = await axios.get('http://localhost:3001/V1/links')
    const links = res.data
    edges.value = links

    // Extraire les points uniques des edges
    const seen = new Set()
    const uniquePoints = []

    for (const link of links) {
      console.log(link)
      if (!seen.has(link.from.id)) {
        uniquePoints.push({ id: link.from.id, name: link.from.name,line:link.from.line, x: link.from.x, y: link.from.y })
        seen.add(link.from.id)
      }
      if (!seen.has(link.to.id)) {
        uniquePoints.push({ id: link.to.id, name: link.to.name,line:link.to.line, x: link.to.x, y: link.to.y })
        seen.add(link.to.id)
      }
    }

    points.value = uniquePoints
    console.log('Points chargés:', points.value)
  } catch (error) {
    console.error('Erreur chargement données:', error)
  }
}

function getLineColor(line) {
  const colors = {
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
    '14': '#62259d'
  }
  return colors[line] || 'white'
}

function getPoint(id) {
  return points.value.find(p => p.id === id)
}

onMounted(() => {
  fetchData()
})

const selectedFrom = ref('')
const selectedTo = ref('')
const shortestPathEdges = ref([])

async function computeShortestPath() {
  console.log('Calcul du chemin de', selectedFrom.value, 'à', selectedTo.value)
  if (!selectedFrom.value || !selectedTo.value) return

  try {
    const res = await axios.get('http://localhost:3001/V1/shortest-path', {
  params: {
    from: selectedFrom.value.id,
    to: selectedTo.value.id
  }
})
    shortestPathEdges.value = res.data
  } catch (error) {
    console.error('Erreur calcul chemin :', error)
  }
}

</script>

<style scoped>
.page-wrapper {
  display: flex;
  justify-content: flex-end; /* pour pousser à droite */
  align-items: center;        /* centré verticalement */
  height: 100vh;              /* prend toute la hauteur */
  width: 100vw;               /* prend toute la largeur */
  background-color: #121212;  /* optionnel pour mieux voir */
}

.map-container {
  position: flex;
  width: 100%;
  height: auto;
}

.map-image {
  display: block;
  width: 100%;
  height: auto;
  visibility: hidden;
}

.map-svg {
  position:fixed;
  top: 10%;
  left: 0;
  width: 40%;
  height: 80%;
  pointer-events: none;
  margin-left: 60%;
}

.point {
  position: fixed;
  width: 3px;
  height: 3px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  margin-top: 5%;
  margin-left: 60%;
  cursor: pointer;
}


.controls {
  position: fixed;
  top: 10px;
  left: 10px;
  background: #ffffffcc;
  padding: 1rem;
  border-radius: 8px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.controls select,
.controls button {
  padding: 5px;
  font-size: 0.9rem;
}

</style>
