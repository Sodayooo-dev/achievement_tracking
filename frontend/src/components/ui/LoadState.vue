<script setup lang="ts">
defineProps<{ loading: boolean; error: string }>()
defineEmits<{ retry: [] }>()
</script>
<template>
  <div v-if="loading" class="state" role="status">
    <span class="loading-bars">▮ ▮ ▮</span>
    <h2>Reading save data</h2>
    <p>Getting your cartridges ready…</p>
  </div>
  <div v-else-if="error" class="state" role="alert">
    <h2>Connection interrupted</h2>
    <p>{{ error }}</p>
    <button @click="$emit('retry')">Try again ↻</button>
  </div>
  <slot v-else />
</template>
