<script setup lang="ts">
import { onUnmounted, ref, watch } from 'vue'
import { usePlayer } from '@/stores/player'
import { useSession } from '@/stores/session'
import { useCatalog } from '@/stores/catalog'
import { readSaved, save } from '@/lib/storage'
import type { Achievement } from '@/api/types'
import PixelIcon from '@/components/ui/PixelIcon.vue'
import { playSound } from '@/lib/sound'
const props = defineProps<{ ready: boolean }>(),
  player = usePlayer(),
  session = useSession(),
  catalog = useCatalog()
const queue = ref<Achievement[]>([]),
  current = ref<Achievement | null>(null),
  banner = ref('')
const queuedUnlockIds = new Set<number>()
let timer: ReturnType<typeof setTimeout>,
  bannerTimer: ReturnType<typeof setTimeout>,
  pendingIds: number[] = []
function next() {
  clearTimeout(timer)
  current.value = queue.value.shift() ?? null
  if (current.value) {
    playSound('confirm')
    timer = setTimeout(next, 4000)
  } else if (session.profile) {
    save(`ch.seen.${session.profile.id}`, pendingIds)
  }
}
function dismissBanner() {
  banner.value = ''
  clearTimeout(bannerTimer)
}
function keys(event: KeyboardEvent) {
  if (event.key === 'Escape') dismissBanner()
}
window.addEventListener('keydown', keys)
watch(
  () => props.ready,
  (ready) => {
    if (!ready || !session.profile) return
    const id = session.profile.id,
      ids = player.unlocks.map((u) => u.id),
      seen = readSaved<number[] | null>(`ch.seen.${id}`, null)
    pendingIds = ids
    if (seen === null) save(`ch.seen.${id}`, ids)
    else {
      const newIds = new Set(
        player.unlocks
          .filter((u) => !seen.includes(u.id) && !queuedUnlockIds.has(u.id))
          .map((u) => {
            queuedUnlockIds.add(u.id)
            return u.achievement_id
          }),
      )
      queue.value.push(...catalog.achievements.filter((a) => newIds.has(a.id)))
      if (!current.value) next()
    }
    const level = player.progress.current,
      previous = readSaved<number | null>(`ch.level.${id}`, null)
    if (level && previous !== null && level.exp_required > previous) {
      banner.value = `LEVEL UP! LV ${level.number} ${level.title}`
      bannerTimer = setTimeout(dismissBanner, 3000)
    }
    if (level) save(`ch.level.${id}`, level.exp_required)
    for (const game of player.ownedGames)
      if (player.completion(game.id).pct === 100) {
        const key = `ch.perfect.${id}.${game.id}`
        if (!readSaved(key, false)) {
          if (seen !== null) {
            banner.value = `PERFECT! ${game.title}`
            bannerTimer = setTimeout(dismissBanner, 3000)
          }
          save(key, true)
        }
      }
  },
  { immediate: true },
)
onUnmounted(() => {
  clearTimeout(timer)
  clearTimeout(bannerTimer)
  window.removeEventListener('keydown', keys)
})
</script>
<template>
  <div class="toast-region" aria-live="polite" aria-atomic="true">
    <div v-if="current" class="achievement-toast" :key="current.id">
      <PixelIcon :name="current.name" />
      <div>
        <small>ACHIEVEMENT UNLOCKED</small>
        <h3>{{ current.name }}</h3>
        <p>+{{ current.exp_value }} XP</p>
      </div>
      <button @click="next" class="text-button" aria-label="Dismiss achievement notification">
        ×</button
      ><span class="floating-exp">+{{ current.exp_value }} XP</span>
    </div>
    <button v-if="banner" class="level-banner" @click="dismissBanner">
      {{ banner }} <span>×</span>
    </button>
  </div>
</template>
