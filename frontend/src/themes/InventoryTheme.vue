<script setup lang="ts">
import { ref } from 'vue'
import type { ThemeItem } from '@/api/types'
import PixelIcon from '@/components/ui/PixelIcon.vue'
import AchievementDetail from './AchievementDetail.vue'
import { gridKeys } from '@/composables/useGridKeys'
defineProps<{ items: ThemeItem[] }>()
const selected = ref<ThemeItem | null>(null)
function keys(event: KeyboardEvent) {
  gridKeys(event, window.innerWidth < 768 ? 5 : 9)
}
</script>
<template>
  <div class="inventory-board">
    <div class="theme-heading">
      <span>PLAYER INVENTORY</span><span>SELECT A SLOT TO INSPECT</span>
    </div>
    <div class="inventory-grid" @keydown="keys">
      <button
        v-for="(item, index) in items"
        :key="item.id"
        data-cell
        :tabindex="index === 0 ? 0 : -1"
        class="inventory-slot"
        :class="{ unlocked: item.unlocked, selected: selected?.id === item.id }"
        :aria-label="`${item.unlocked ? item.name : 'Locked achievement'}: ${item.description}`"
        @focus="selected = item"
        @mouseenter="selected = item"
        @click="selected = item"
      >
        <PixelIcon :name="item.name" :locked="!item.unlocked" /><span>{{
          item.unlocked ? item.exp_value : '???'
        }}</span>
      </button>
      <div
        v-for="n in Math.max(0, 27 - items.length)"
        :key="`empty-${n}`"
        class="inventory-slot empty-slot"
        aria-hidden="true"
      />
    </div>
    <AchievementDetail v-if="selected" :item="selected" />
    <p v-else class="inspect-hint">Hover, focus, or tap an item to inspect it.</p>
  </div>
</template>
