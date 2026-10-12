<script setup lang="ts">
import { computed, ref } from 'vue'
import { usePlayer } from '@/stores/player'
import Cartridge from '@/components/library/Cartridge.vue'
import { gridKeys } from '@/composables/useGridKeys'
const player = usePlayer(),
  sort = ref('title')
const games = computed(() =>
  [...player.ownedGames].sort((a, b) =>
    sort.value === 'completion'
      ? player.completion(b.id).pct - player.completion(a.id).pct
      : a.title.localeCompare(b.title),
  ),
)
const completed = computed(
  () => games.value.filter((g) => player.completion(g.id).pct === 100).length,
)
function keys(event: KeyboardEvent) {
  gridKeys(event, window.innerWidth < 768 ? 2 : 3)
}
</script>
<template>
  <section class="page-content">
    <div class="page-heading">
      <div>
        <p class="eyebrow">PLAYER ONE / HOME BASE</p>
        <h1>Your cartridge shelf<span class="red">.</span></h1>
        <p>Good games. Hard-earned milestones. All yours.</p>
      </div>
      <RouterLink class="button" to="/catalog">Browse catalog <span>↗</span></RouterLink>
    </div>
    <div class="stats-strip">
      <div>
        <strong>{{ games.length.toString().padStart(2, '0') }}</strong
        ><span>CARTRIDGES</span>
      </div>
      <div>
        <strong>{{ player.unlockedIds.size.toString().padStart(2, '0') }}</strong
        ><span>ACHIEVEMENTS</span>
      </div>
      <div>
        <strong>{{ completed.toString().padStart(2, '0') }}</strong
        ><span>100% COMPLETE</span>
      </div>
      <div class="stats-note"><span class="red">★</span> EVERY LITTLE WIN COUNTS.</div>
    </div>
    <div class="section-heading">
      <h2>
        MY COLLECTION <span>({{ games.length }})</span>
      </h2>
      <label class="inline-label"
        >Sort by
        <select v-model="sort">
          <option value="title">Title A–Z</option>
          <option value="completion">Completion</option>
        </select></label
      >
    </div>
    <div v-if="games.length" class="cartridge-shelf" @keydown="keys">
      <Cartridge
        v-for="(game, index) in games"
        :key="game.id"
        :game="game"
        :completion="player.completion(game.id)"
        :index="index"
      />
    </div>
    <div v-else class="state empty-shelf">
      <span aria-hidden="true">▦</span>
      <h2>A fresh shelf. A new adventure.</h2>
      <p>No cartridges yet. Ask a developer to add games to your library.</p>
      <RouterLink to="/catalog" class="button">Explore the catalog →</RouterLink>
    </div>
    <div class="shelf-footer">
      <span>↑ ↓ ← → TO SELECT / ENTER TO INSERT</span
      ><span>YOU BRING THE SKILL. WE KEEP THE SCORE.</span>
    </div>
  </section>
</template>
