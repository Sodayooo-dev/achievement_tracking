<script setup lang="ts">
import { computed } from 'vue'
import { usePlayer } from '@/stores/player'
import { useCatalog } from '@/stores/catalog'
import PixelIcon from '@/components/ui/PixelIcon.vue'
const player = usePlayer(),
  catalog = useCatalog()
const groups = computed(() => {
  const result = new Map<string, typeof player.unlocks>()
  for (const unlock of [...player.unlocks].sort(
    (a, b) => b.acquired_date.localeCompare(a.acquired_date) || b.id - a.id,
  )) {
    const month = unlock.acquired_date.slice(0, 7)
    result.set(month, [...(result.get(month) ?? []), unlock])
  }
  return result
})
const achievement = (id: number) => catalog.achievements.find((a) => a.id === id)
const game = (id: number) => catalog.games.find((g) => g.id === achievement(id)?.game_id)
const monthName = (month: string) =>
  new Date(`${month}-01T12:00:00`).toLocaleDateString(undefined, {
    month: 'long',
    year: 'numeric',
  })
</script>
<template>
  <section class="page-content">
    <div class="page-heading">
      <div>
        <p class="eyebrow">NO WIN LEFT BEHIND</p>
        <h1>Your save history<span class="red">.</span></h1>
        <p>A little proof that all those hours meant something.</p>
      </div>
      <span class="catalog-count">{{ player.unlocks.length }} SAVES</span>
    </div>
    <div v-if="!groups.size" class="state">
      <h2>No saves yet.</h2>
      <p>Your first achievement is the start of a great story.</p>
      <RouterLink class="button" to="/hub">Back to library →</RouterLink>
    </div>
    <div v-for="[month, unlocks] in groups" :key="month" class="history-month">
      <h2>{{ monthName(month) }}</h2>
      <ol class="timeline">
        <li v-for="unlock in unlocks" :key="unlock.id">
          <time :datetime="unlock.acquired_date">{{ unlock.acquired_date }}</time
          ><PixelIcon :name="achievement(unlock.achievement_id)?.name ?? 'Unknown'" />
          <div>
            <small>{{ game(unlock.achievement_id)?.title ?? 'Unavailable game' }}</small>
            <h3>
              {{ achievement(unlock.achievement_id)?.name ?? 'Unavailable achievement' }}
            </h3>
            <p>{{ achievement(unlock.achievement_id)?.description }}</p>
          </div>
          <strong class="red">+{{ achievement(unlock.achievement_id)?.exp_value ?? 0 }} XP</strong>
        </li>
      </ol>
    </div>
  </section>
</template>
