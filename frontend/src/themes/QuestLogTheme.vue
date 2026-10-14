<script setup lang="ts">
import type { ThemeItem } from '@/api/types'
import AchievementDetail from './AchievementDetail.vue'
defineProps<{ items: ThemeItem[] }>()
</script>
<template>
  <div class="quest-journal">
    <div class="theme-heading"><span>THE ADVENTURER’S JOURNAL</span><span>✦</span></div>
    <article
      v-for="item in items"
      :key="item.id"
      :data-achievement-id="item.id"
      data-cell
      class="quest-entry"
      tabindex="0"
      role="button"
      @keydown.enter="($event.currentTarget as HTMLElement).click()"
      @keydown.space.prevent="($event.currentTarget as HTMLElement).click()"
    >
      <span class="quest-marker">{{ item.unlocked ? '✓' : '◇' }}</span
      ><AchievementDetail :item="item" />
    </article>
  </div>
</template>
