<template>
  <div class="map-container" @click="addPoint">
    <!-- Image utilisée pour le placement, invisible -->
    <img ref="imageRef" src="../assets/metrof_r.png" class="map-image" style="visibility:visible;" />

    <!-- Lignes entre les points -->
    <svg class="map-svg">
      <line
        v-for="(edge, index) in edges"
        :key="index"
        :x1="getPoint(edge.from)?.x"
        :y1="getPoint(edge.from)?.y"
        :x2="getPoint(edge.to)?.x"
        :y2="getPoint(edge.to)?.y"
        stroke="white"
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
    const pointRes = await axios.get('http://localhost:3001/V1/map-points')
    points.value = pointRes.data

    const edgeRes = await axios.get('http://localhost:3001/V1/intersections')
    edges.value = edgeRes.data
  } catch (error) {
    console.error('Erreur chargement données:', error)
  }
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
  width: 100%;
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
