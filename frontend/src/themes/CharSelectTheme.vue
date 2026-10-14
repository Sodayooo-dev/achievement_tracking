<script setup lang="ts">
import { ref } from 'vue'
import type { ThemeItem } from '@/api/types'
import PixelIcon from '@/components/ui/PixelIcon.vue'
import AchievementDetail from './AchievementDetail.vue'
import { gridKeys } from '@/composables/useGridKeys'
defineProps<{ items: ThemeItem[] }>()
const selected = ref<ThemeItem | null>(null)
</script>
<template>
  <div class="fighter-select">
    <div class="theme-heading"><span>CHOOSE YOUR CHAMPION</span><span>1P / READY</span></div>
    <div class="fighter-grid" @keydown="gridKeys($event)">
      <button
        v-for="(item, index) in items"
        :key="item.id"
        :data-achievement-id="item.id"
        data-cell
        :tabindex="index === 0 ? 0 : -1"
        :class="{ unlocked: item.unlocked, selected: selected?.id === item.id }"
        :aria-label="`${item.name}: ${item.unlocked ? 'Unlocked' : 'Locked'} achievement`"
        @focus="selected = item"
        @click="selected = item"
      >
        <span class="fighter-number">{{ String(index + 1).padStart(2, '0') }}</span
        ><PixelIcon :name="item.name" :locked="!item.unlocked" /><strong>{{ item.name }}</strong
        ><span class="fighter-xp">{{ item.exp_value }} XP</span>
      </button>
    </div>

    <p class="inspect-hint">Select a portrait to view the fighter card.</p>
  </div>
</template>
