<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ThemeItem } from '@/api/types'
import PixelIcon from '@/components/ui/PixelIcon.vue'
import AchievementDetail from './AchievementDetail.vue'
const props = defineProps<{ items: ThemeItem[]; allItems?: ThemeItem[] }>(),
  selected = ref<ThemeItem | null>(null)
const tiers = computed(() => {
  const sorted = [...(props.allItems ?? props.items)].sort(
    (a, b) => a.exp_value - b.exp_value || a.id - b.id,
  )
  return [0, 1, 2].map((tier) =>
    sorted
      .slice(Math.ceil((sorted.length * tier) / 3), Math.ceil((sorted.length * (tier + 1)) / 3))
      .filter((a) => props.items.some((item) => item.id === a.id)),
  )
})
</script>
<template>
  <div class="skill-tree">
    <div class="theme-heading">
      <span>PATH OF THE ADVENTURER</span><span>THREE TIERS / ONE LEGACY</span>
    </div>
    <div class="tree-stage">
      <div v-for="(tier, index) in tiers" :key="index" class="tree-tier">
        <h3>{{ ['INITIATE', 'ADEPT', 'MASTER'][index] }}</h3>
        <div class="tree-nodes">
          <button
            v-for="item in tier"
            :key="item.id"
            :data-achievement-id="item.id"
            data-cell
            class="skill-node"
            :class="{ unlocked: item.unlocked }"
            :aria-label="`${item.name}: ${item.unlocked ? 'Unlocked' : 'Locked'} achievement`"
            @focus="selected = item"
            @mouseenter="selected = item"
            @click="selected = item"
          >
            <PixelIcon :name="item.name" :locked="!item.unlocked" /><span>{{ item.name }}</span
            ><small>{{ item.exp_value }} XP</small>
          </button>
        </div>
        <svg v-if="index < 2" class="tree-connector" viewBox="0 0 100 20" aria-hidden="true">
          <path
            d="M50 0 V10 M10 20 V10 H90 V20 M50 10 V20"
            fill="none"
            stroke="currentColor"
            stroke-width="1"
            :class="{ lit: tier.some((a) => a.unlocked) }"
          />
        </svg>
      </div>
    </div>

    <p class="inspect-hint">
      Explore a node to see its objective. Tiers show XP value, not prerequisites.
    </p>
  </div>
</template>
