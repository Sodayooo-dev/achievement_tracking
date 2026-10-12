<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import PixelIcon from './PixelIcon.vue'
const props = defineProps<{ title: string; url?: string }>()
const failed = ref(false)
const source = computed(() => {
  try {
    const parsed = new URL(props.url ?? '')
    return ['https:', 'http:'].includes(parsed.protocol) ? parsed.href : ''
  } catch {
    return ''
  }
})
watch(source, () => {
  failed.value = false
})
</script>
<template>
  <div class="game-artwork" :class="{ 'has-artwork': source && !failed }">
    <img
      v-if="source && !failed"
      :src="source"
      :alt="`${title} game artwork`"
      loading="lazy"
      decoding="async"
      referrerpolicy="no-referrer"
      @error="failed = true"
    /><PixelIcon v-else :name="title" />
  </div>
</template>
