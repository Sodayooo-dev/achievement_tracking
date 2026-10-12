<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ThemeItem } from '@/api/types'
import AchievementDetail from './AchievementDetail.vue'
const props = defineProps<{ items: ThemeItem[] }>(),
  selected = ref<ThemeItem | null>(null)
const sorted = computed(() => [...props.items].sort((a, b) => a.id - b.id))
const recent = computed(
  () =>
    [...props.items]
      .filter((a) => a.unlocked)
      .sort(
        (a, b) => (b.acquired_date ?? '').localeCompare(a.acquired_date ?? '') || b.id - a.id,
      )[0]?.id,
)
const point = (i: number) => ({
  x: 80 + (Math.floor(i / 4) % 2 ? 3 - (i % 4) : i % 4) * 145,
  y: 60 + Math.floor(i / 4) * 130,
})
const path = computed(() =>
  sorted.value.map((_, i) => `${i ? 'L' : 'M'} ${point(i).x} ${point(i).y}`).join(' '),
)
</script>
<template>
  <div class="world-map">
    <div class="theme-heading">
      <span>WORLD {{ items.length ? '01' : '00' }} / THE LONG WAY HOME</span
      ><span>★ = CLEARED</span>
    </div>
    <div class="map-scroll">
      <div
        class="map-stage"
        :style="{
          height: Math.max(200, Math.ceil(items.length / 4) * 130) + 'px',
        }"
      >
        <svg
          :viewBox="`0 0 600 ${Math.max(200, Math.ceil(items.length / 4) * 130)}`"
          aria-hidden="true"
        >
          <path
            :d="path"
            fill="none"
            stroke="currentColor"
            stroke-width="5"
            stroke-dasharray="8 8"
          /></svg
        ><button
          v-for="(item, i) in sorted"
          :key="item.id"
          class="map-node"
          :class="{ unlocked: item.unlocked, recent: recent === item.id }"
          :style="{ left: point(i).x / 6 + '%', top: point(i).y + 'px' }"
          :aria-label="`${item.unlocked ? item.name : 'Locked level'}: ${item.description}`"
          @focus="selected = item"
          @click="selected = item"
        >
          <span>{{ item.unlocked ? '⚑' : String(i + 1).padStart(2, '0') }}</span
          ><small>{{ item.unlocked ? item.name : '???' }}</small
          ><i v-if="recent === item.id" aria-hidden="true">▼</i>
        </button>
      </div>
    </div>
    <AchievementDetail v-if="selected" :item="selected" />
    <p class="inspect-hint" v-else>Select a level. Your latest clear is marked with a cursor.</p>
  </div>
</template>
