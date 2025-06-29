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
        v-for="edge in edges"
        :key="'path-' + index"
        :x1="points[parseInt(edge.node0)].x / 1.5"
        :y1="points[parseInt(edge.node0)].y / 1.5"
        :x2="points[parseInt(edge.node1)].x / 1.5"
        :y2="points[parseInt(edge.node1)].y / 1.5"
        :stroke="getLineColor(points[parseInt(edge.node0)].line)"
        stroke-width="2"
      />
    </svg>

    <div class="controls">
      <h3>Calcul de chemin</h3>
      <!-- Autres éléments existants -->

      <!-- Bouton pour calculer l'ACPM -->
      <button @click="computeACPM">Calculer ACPM</button>
      <p v-if="totalWeight !== null">Poids total de l'ACPM : {{ totalWeight }}</p>
    </div>
    <!-- Points -->
    <div
      v-for="(point, index) in points"
      :key="index"
      class="point"
      :style="{ top: point.y / 1.5 + 'px', left: point.x / 1.5 + 'px', background: 'white' }"
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
const shortestPath = ref([])
const shortestweight = ref(null)
const totalWeight = ref(null)
const acpm = ref([])
const visiblePathEdges = ref([])
async function fetchData() {
  try {
    const res1 = await axios.get('http://localhost:5000/api/edges')
    edges.value = res1.data

    const res2 = await axios.get('http://localhost:5000/api/nodes')
    points.value = res2.data
    console.log('Points:', edges.value.length)
  } catch (error) {
    console.error('Erreur lors de la récupération des données:', error)
  }
}

async function computeACPM() {
  try {
    const res = await axios.get('http://localhost:5000/api/acpm')
    shortestPathEdges.value = res.data
    totalWeight.value = res.data.total_weight
    console.log('ACPM:', shortestPathEdges.value, 'Poids total:', totalWeight.value)
    alert(`ACPM calculé avec succès ! Poids total : ${totalWeight.value / 3600}`)
    animatePathDisplay()
  } catch (error) {
    console.error("Erreur lors du calcul de l'ACPM :", error)
  }
}

function getLineColor(line) {
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
  return colors[line] || 'white'
}

onMounted(() => {
  fetchData()
})

const selectedFrom = ref('')
const selectedTo = ref('')
const shortestPathEdges = ref([])

async function computeShortestPath() {
  if (!selectedFrom.value || !selectedTo.value) {
    alert("Veuillez sélectionner une station de départ et d'arrivée.")
    return
  }

  const startId = selectedFrom.value.id
  const endId = selectedTo.value.id

  try {
    const response = await fetch(
      `http://localhost:5000/api/path?start_id=${startId}&end_id=${endId}`,
    )
    if (!response.ok) {
      throw new Error(`Erreur serveur: ${response.status}`)
    }
    const data = await response.json()
    shortestPath.value = data.path
    shortestweight.value = data.total_weight
    console.log('Chemin le plus court:', shortestPath.value, 'Poids:', shortestweight.value)
    alert(`Chemin le plus court calculé avec succès ! Poids total : ${shortestweight.value / 3600}`)
  } catch (error) {
    console.error('Erreur calcul chemin :', error)
  }
}

function animatePathDisplay() {
  visiblePathEdges.value = []
  let i = 0
  const interval = setInterval(() => {
    if (i < shortestPathEdges.value.length) {
      visiblePathEdges.value.push(shortestPathEdges.value[i])
      i++
    } else {
      clearInterval(interval)
    }
  }, 300) // délai entre chaque segment en ms
}
</script>

<style scoped>
.page-wrapper {
  display: flex;
  justify-content: flex-end; /* pour pousser à droite */
  align-items: center; /* centré verticalement */
  height: 100vh; /* prend toute la hauteur */
  width: 100vw; /* prend toute la largeur */
  background-color: #121212; /* optionnel pour mieux voir */
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
  position: fixed;
  top: 10%;
  left: 0;
  width: 40%;
  height: 80%;
  pointer-events: none;
  margin-left: 60%;
}

.point {
  position: fixed;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  margin-top: 5%;
  margin-left: 60%;
  border-color: aqua;
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
