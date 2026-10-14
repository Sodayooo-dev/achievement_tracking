import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Achievement, Game, Level } from '@/api/types'
import * as api from '@/api/endpoints'
export const useCatalog = defineStore('catalog', () => {
  const games = ref<Game[]>([]),
    achievements = ref<Achievement[]>([]),
    levels = ref<Level[]>([])
  let pending: Promise<void> | null = null,
    loaded = false,
    generation = 0
  const gameLoads = new Map<number, Promise<void>>()
  async function load(force = false) {
    if (pending) return pending
    if (loaded && !force) return
    const ticket = ++generation
    const task = (async () => {
      const result = await Promise.all([api.getGames(), api.getAchievements(), api.getLevels()])
      if (ticket !== generation) return
      ;[games.value, achievements.value, levels.value] = result
      loaded = true
    })()
    pending = task
    try {
      await task
    } finally {
      if (pending === task) pending = null
    }
  }
  async function loadGame(id: number) {
    if (gameLoads.has(id)) return gameLoads.get(id)
    const ticket = generation
    const task = (async () => {
      const rows = await api.getGameAchievements(id)
      if (ticket === generation)
        achievements.value = [...achievements.value.filter((a) => a.game_id !== id), ...rows]
    })()
    gameLoads.set(id, task)
    try {
      await task
    } finally {
      if (gameLoads.get(id) === task) gameLoads.delete(id)
    }
  }
  const levelsSorted = computed(() =>
    [...levels.value].sort((a, b) => a.exp_required - b.exp_required),
  )
  return { games, achievements, levels, levelsSorted, load, loadGame }
})
