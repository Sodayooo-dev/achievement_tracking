<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCatalog } from '@/stores/catalog'
import { usePlayer } from '@/stores/player'
import { genreToTheme, themeNames } from '@/lib/genre'
import { themes } from '@/themes/registry'
import CartridgeInsert from '@/components/fx/CartridgeInsert.vue'
import { useCartridgeLoad } from '@/composables/useCartridgeLoad'
import LoadState from '@/components/ui/LoadState.vue'
const route = useRoute(),
  catalog = useCatalog(),
  player = usePlayer()
const { loading, error, inserting, loadGame, animationFinished } = useCartridgeLoad(async () => {
  await catalog.load()
  await player.load()
})
watch(
  () => route.params.gameId,
  () => {
    void loadGame()
  },
  { immediate: true },
)
const game = computed(() => catalog.games.find((g) => g.id === Number(route.params.gameId)))
const key = computed(() => genreToTheme(game.value?.genre ?? ''))
const items = computed(() =>
  catalog.achievements
    .filter((a) => a.game_id === game.value?.id)
    .map((a) => ({
      ...a,
      unlocked: player.unlockedIds.has(a.id),
      acquired_date: player.unlocks.find((u) => u.achievement_id === a.id)?.acquired_date,
    })),
)
const completion = computed(() => player.completion(game.value?.id ?? 0))
</script>
<template>
  <section v-if="game" class="page-content play-page">
    <RouterLink v-if="!inserting" class="back-link" data-sound="back" to="/hub"
      >← Eject cartridge / back to library</RouterLink
    >
    <div v-if="!inserting" class="page-heading">
      <div>
        <p class="eyebrow">{{ game.genre }} / {{ themeNames[key] }}</p>
        <h1>{{ game.title }}<span class="red">.</span></h1>
        <p>{{ game.publisher }}</p>
      </div>
      <div class="game-completion">
        <strong
          >{{ completion.got }}<span> / {{ completion.total }} ★</span></strong
        ><small>{{ Math.round(completion.pct) }}% COMPLETE</small>
      </div>
    </div>
    <CartridgeInsert
      v-if="inserting"
      :key="game.id"
      :game="game"
      :loading="loading"
      @complete="animationFinished"
    />
    <LoadState v-else :loading="loading" :error="error" @retry="loadGame">
      <div v-if="!items.length" class="state">
        <h2>No objectives on this cartridge yet.</h2>
        <p>A developer can add achievements to get you started.</p>
      </div>
      <div v-else class="genre-screen" :class="key">
        <component :is="themes[key]" :game="game" :items="items" :completion="completion" />
      </div>
    </LoadState>
  </section>
  <LoadState v-else :loading="loading" :error="error" @retry="loadGame"
    ><div class="state">
      <h1>Cartridge not found.</h1>
      <RouterLink class="button" to="/hub">Back to library →</RouterLink>
    </div></LoadState
  >
</template>
