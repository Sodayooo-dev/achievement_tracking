import { defineAsyncComponent } from 'vue'
export const themes = {
  questlog: defineAsyncComponent(() => import('./QuestLogTheme.vue')),
  inventory: defineAsyncComponent(() => import('./InventoryTheme.vue')),
  skilltree: defineAsyncComponent(() => import('./SkillTreeTheme.vue')),
  worldmap: defineAsyncComponent(() => import('./WorldMapTheme.vue')),
  killfeed: defineAsyncComponent(() => import('./KillFeedTheme.vue')),
  charselect: defineAsyncComponent(() => import('./CharSelectTheme.vue')),
  trophy: defineAsyncComponent(() => import('./TrophyCaseTheme.vue')),
}
