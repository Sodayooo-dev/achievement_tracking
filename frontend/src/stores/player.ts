import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { PlayerAchievement, PlayerGame } from '@/api/types'
import * as api from '@/api/endpoints'
import { useSession } from './session'
import { useCatalog } from './catalog'
import { progression } from '@/lib/progression'
export const usePlayer = defineStore('player', () => {
  const library = ref<PlayerGame[]>([]),
    unlocks = ref<PlayerAchievement[]>([])
  const session = useSession(),
    catalog = useCatalog()
  let generation = 0
  let pending: Promise<void> | null = null
  async function load() {
    if (pending) return pending
    const ticket = ++generation
    const id = session.profile?.id
    const task = (async () => {
      const [games, achievements] = await Promise.all([api.getLibrary(), api.getUnlocks()])
      if (session.profile?.id !== id || ticket !== generation) return
      library.value = games.filter((g) => g.player_id === id)
      unlocks.value = achievements.filter((a) => a.player_id === id)
    })()
    pending = task
    try {
      await task
    } finally {
      if (pending === task) pending = null
    }
  }
  function reset() {
    generation++
    pending = null
    library.value = []
    unlocks.value = []
  }
  const unlockedIds = computed(() => new Set(unlocks.value.map((u) => u.achievement_id)))
  const ownedGames = computed(() =>
    catalog.games.filter((g) => library.value.some((l) => l.game_id === g.id)),
  )
  const totalExp = computed(() =>
    catalog.achievements
      .filter((a) => unlockedIds.value.has(a.id))
      .reduce((sum, a) => sum + a.exp_value, 0),
  )
  const progress = computed(() => progression(catalog.levels, totalExp.value))
  function completion(id: number) {
    const items = catalog.achievements.filter((a) => a.game_id === id)
    const got = items.filter((a) => unlockedIds.value.has(a.id)).length
    return {
      got,
      total: items.length,
      pct: items.length ? (got / items.length) * 100 : 0,
    }
  }
  return {
    library,
    unlocks,
    unlockedIds,
    ownedGames,
    totalExp,
    progress,
    completion,
    load,
    reset,
  }
})
