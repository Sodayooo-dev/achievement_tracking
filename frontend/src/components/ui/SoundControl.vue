<script setup lang="ts">
import { soundEnabled, toggleSound } from '@/lib/sound'
</script>
<template>
  <button
    class="text-button sound-control"
    data-sound="silent"
    :aria-pressed="soundEnabled"
    :aria-label="soundEnabled ? 'Mute sound effects' : 'Enable sound effects'"
    :title="soundEnabled ? 'Sound effects on' : 'Sound effects off'"
    @click="toggleSound"
  >
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
    >
      <path d="M3 9h4l5-4v14l-5-4H3z" />
      <path v-if="soundEnabled" d="M16 8a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14" />
      <path v-else d="m16 9 6 6m0-6-6 6" />
    </svg>
  </button>
</template>
