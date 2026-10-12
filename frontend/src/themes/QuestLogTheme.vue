<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ThemeItem } from '@/api/types'
import AchievementDetail from './AchievementDetail.vue'
const props = defineProps<{ items: ThemeItem[] }>(),
  tab = ref(false)
const visible = computed(() => props.items.filter((a) => a.unlocked === tab.value))
</script>
<template>
  <div class="quest-journal">
    <div class="theme-heading"><span>THE ADVENTURER’S JOURNAL</span><span>✦</span></div>
    <div class="theme-tabs">
      <button :class="{ selected: !tab }" @click="tab = false">
        Active quests ({{ items.filter((a) => !a.unlocked).length }})</button
      ><button :class="{ selected: tab }" @click="tab = true">
        Completed ({{ items.filter((a) => a.unlocked).length }})
      </button>
    </div>
    <div v-if="!visible.length" class="state">
      <h3>
        {{ tab ? 'Your story is just beginning.' : 'All quests complete!' }}
      </h3>
    </div>
    <article v-for="item in visible" :key="item.id" class="quest-entry" tabindex="0">
      <span class="quest-marker">{{ item.unlocked ? '✓' : '◇' }}</span
      ><AchievementDetail :item="item" />
    </article>
  </div>
</template>
