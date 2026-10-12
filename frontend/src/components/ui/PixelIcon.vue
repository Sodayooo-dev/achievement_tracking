<script setup lang="ts">
import { computed } from 'vue'
import { pixelIcon } from '@/lib/pixelIcon'
const props = defineProps<{ name: string; locked?: boolean }>()
const cells = computed(() => pixelIcon(props.name))
</script>
<template>
  <svg
    viewBox="-1 -1 10 10"
    aria-hidden="true"
    shape-rendering="crispEdges"
    class="pixel-icon"
    :class="{ silhouette: locked }"
  >
    <rect
      v-for="(cell, i) in cells"
      :key="i"
      :x="cell.x"
      :y="cell.y"
      width="1"
      height="1"
      fill="currentColor"
    />
  </svg>
</template>
