<template>
  <div class="map-container" @click="addPoint">
    <!-- Image utilisée pour le placement, invisible -->
    <img ref="imageRef" src="../assets/metrof_r.png" class="map-image" style="visibility:hidden;" />

    <!-- Lignes entre les points -->
    <svg class="map-svg">
      <line
        v-for="(edge, index) in edges"
        :key="index"
        :x1="getPoint(edge.from.id)?.x"
        :y1="getPoint(edge.from.id)?.y"
        :x2="getPoint(edge.to.id)?.x"
        :y2="getPoint(edge.to.id)?.y"
        :stroke="getLineColor(edge.from.line)"
        stroke-width="2"
      />
    </svg>

    <!-- Points -->
    <div
      v-for="(point, index) in points"
      :key="index"
      class="point"
      :style="{ top: point.y + 'px', left: point.x + 'px', background: 'white' }"
      :title="point.name"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const points = ref([])
const edges = ref([])
const imageRef = ref(null)

async function fetchData() {
  try {
    const res = await axios.get('http://localhost:3001/V1/links')
    const links = res.data
    console.log('Données chargées:', links)
    edges.value = links

    // Extraire les points uniques des edges
    const seen = new Set()
    const uniquePoints = []

    for (const link of links) {
      if (!seen.has(link.from.id)) {
        uniquePoints.push({ id: link.from.id, name: link.from.name, x: link.from.x, y: link.from.y })
        seen.add(link.from.id)
      }
      if (!seen.has(link.to.id)) {
        uniquePoints.push({ id: link.to.id, name: link.to.name, x: link.to.x, y: link.to.y })
        seen.add(link.to.id)
      }
    }

    points.value = uniquePoints
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
function addPoint(event) {
  const rect = imageRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  points.value.push({ x, y, name: 'Nouveau point' })
}

function getPoint(id) {
  return points.value.find(p => p.id === id)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.map-container {
  position: relative;
  display: inline-block;
}

.map-image {
  display: block;
  max-width: 200%;
}

.map-svg {
  position: absolute;
  top: 0;
  left: 0;
  width: 200%;
  height: 100%;
  pointer-events: none;
}

.point {
  position: absolute;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
}
</style>
