<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ThemeItem } from '@/api/types'
import PixelIcon from '@/components/ui/PixelIcon.vue'
import AchievementDetail from './AchievementDetail.vue'
const props = defineProps<{ items: ThemeItem[] }>(),
  selected = ref<ThemeItem | null>(null)
const shelves = computed(() => {
  const sorted = [...props.items].sort((a, b) => b.exp_value - a.exp_value || a.id - b.id)
  return [0, 1, 2].map((tier) =>
    sorted.slice(
      Math.ceil((sorted.length * tier) / 3),
      Math.ceil((sorted.length * (tier + 1)) / 3),
    ),
  )
})
</script>
<template>
  <div class="trophy-cabinet">
    <div class="theme-heading">
      <span>THE WINNER’S CABINET</span><span>HARD EARNED / WELL DESERVED</span>
    </div>
    <div
      v-for="(shelf, tier) in shelves"
      :key="tier"
      class="trophy-shelf"
      :class="['gold', 'silver', 'bronze'][tier]"
    >
      <h3>{{ ['GOLD', 'SILVER', 'BRONZE'][tier] }}</h3>
      <div>
        <button
          v-for="item in shelf"
          :key="item.id"
          :class="{ unlocked: item.unlocked }"
          :aria-label="`${item.unlocked ? item.name : 'Locked trophy'}: ${item.description}`"
          @focus="selected = item"
          @click="selected = item"
        >
          <span class="trophy-shape"><PixelIcon :name="item.name" :locked="!item.unlocked" /></span
          ><strong>{{ item.unlocked ? item.name : '???' }}</strong
          ><small>{{ item.exp_value }} XP</small>
        </button>
        <p v-if="!shelf.length">An empty shelf, full of possibility.</p>
      </div>
    </div>
    <AchievementDetail v-if="selected" :item="selected" />
    <p class="inspect-hint" v-else>
      Trophy tiers are ranked by XP within this game. Select one to inspect.
    </p>
  </div>
</template>
