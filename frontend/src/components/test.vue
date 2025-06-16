<template>
  <div class="map-container" @click="addPoint">
    <img ref="imageRef" src="../assets/metrof_r.png" class="map-image" />
    <div
      class="point"
      style="top: 539px; left : 530px;background: pink;"></div>
  <div
      class="point"
      style="top: 548px; left : 527px;background: pink;"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const points = ref([])
const imageRef = ref(null)

function addPoint(event) {
  const rect = imageRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  points.value.push({ x, y })
}
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

.point {
  position: absolute;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
}
</style>
