<script setup lang="ts">
import { computed } from 'vue'
import type { ThemeItem } from '@/api/types'
import PixelIcon from '@/components/ui/PixelIcon.vue'
import AchievementDetail from './AchievementDetail.vue'
const props = defineProps<{ items: ThemeItem[]; completion: { pct: number } }>()
const feed = computed(() =>
  [...props.items]
    .filter((a) => a.unlocked)
    .sort((a, b) => (b.acquired_date ?? '').localeCompare(a.acquired_date ?? '') || b.id - a.id),
)
</script>
<template>
  <div class="combat-hud">
    <div class="theme-heading">
      <span>OPERATIONS / AFTER ACTION REPORT</span><span>● LIVE</span>
    </div>
    <div class="combat-top">
      <div class="combat-reticle" aria-hidden="true">
        <span>＋</span><small>OBJECTIVE ACQUIRED</small>
      </div>
      <div class="kill-feed">
        <h3>YOUR UNLOCK FEED</h3>
        <p v-if="!feed.length">Awaiting your first confirmed achievement.</p>
        <button v-for="item in feed" :key="item.id" :data-achievement-id="item.id" data-cell>
          <b>YOU</b><span>▸</span><PixelIcon :name="item.name" /><span
            >{{ item.name }}<small>{{ item.acquired_date }}</small></span
          ><strong>+{{ item.exp_value }}</strong>
        </button>
      </div>
    </div>
    <h3 class="contracts-heading">
      OPEN CONTRACTS / {{ items.filter((a) => !a.unlocked).length }}
    </h3>
    <article
      v-for="item in items.filter((a) => !a.unlocked)"
      :key="item.id"
      :data-achievement-id="item.id"
      data-cell
      class="contract"
      tabindex="0"
      role="button"
      @keydown.enter="($event.currentTarget as HTMLElement).click()"
      @keydown.space.prevent="($event.currentTarget as HTMLElement).click()"
    >
      <AchievementDetail :item="item" />
    </article>
    <p v-if="completion.pct === 100" class="inspect-hint">
      All contracts fulfilled. Mission accomplished.
    </p>
  </div>
</template>
