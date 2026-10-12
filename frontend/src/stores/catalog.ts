import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Achievement, Game, Level } from '@/api/types'
import * as api from '@/api/endpoints'
export const useCatalog = defineStore('catalog', () => {
  const games = ref<Game[]>([]),
    achievements = ref<Achievement[]>([]),
    levels = ref<Level[]>([])
  async function load() {
    const result = await Promise.all([api.getGames(), api.getAchievements(), api.getLevels()])
    ;[games.value, achievements.value, levels.value] = result
  }
  const levelsSorted = computed(() =>
    [...levels.value].sort((a, b) => a.exp_required - b.exp_required),
  )
  return { games, achievements, levels, levelsSorted, load }
})
