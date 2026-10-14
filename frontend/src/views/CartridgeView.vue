<script setup lang="ts">
import { computed, inject, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCatalog } from '@/stores/catalog'
import { usePlayer } from '@/stores/player'
import { genreToTheme, themeNames } from '@/lib/genre'
import CartridgeInsert from '@/components/fx/CartridgeInsert.vue'
import { useCartridgeLoad } from '@/composables/useCartridgeLoad'
import LoadState from '@/components/ui/LoadState.vue'
import AchievementBrowser from '@/components/ui/AchievementBrowser.vue'
import GameArtwork from '@/components/ui/GameArtwork.vue'
import Modal from '@/components/ui/Modal.vue'
import { cartridgeControlKey } from '@/lib/cartridgeControl'
const route = useRoute(),
  catalog = useCatalog(),
  player = usePlayer()
const { loading, error, inserting, loadGame, animationFinished } = useCartridgeLoad(async () => {
  await catalog.load()
  await catalog.loadGame(Number(route.params.gameId))
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
const insertionLocked = inject(cartridgeControlKey, null),
  information = ref(false)
watch(
  [game, inserting],
  () => {
    if (insertionLocked) insertionLocked.value = Boolean(game.value && inserting.value)
  },
  { immediate: true },
)
onUnmounted(() => {
  if (insertionLocked) insertionLocked.value = false
})
</script>
<template>
  <section v-if="game" class="page-content play-page">
    <header v-if="!inserting" class="game-bar">
      <GameArtwork class="game-bar-art" :title="game.title" :url="game.image_url" />
      <div class="game-bar-title">
        <h1 :title="game.title">{{ game.title }}</h1>
        <small>{{ themeNames[key] }}</small>
      </div>
      <span
        class="game-bar-progress"
        :aria-label="`${completion.got} of ${completion.total} unlocked, ${Math.round(completion.pct)} percent complete`"
        >{{ completion.got }} / {{ completion.total }} <span aria-hidden="true">★</span></span
      >
      <button class="game-info-button" aria-label="Game information" @click="information = true">
        ⓘ
      </button>
    </header>
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
        <AchievementBrowser :theme="key" :game="game" :items="items" :completion="completion" />
      </div>
    </LoadState>
    <Modal v-if="information" :title="game.title" @close="information = false"
      ><p>{{ game.publisher }}</p>
      <p>{{ game.genre }} · {{ themeNames[key] }}</p>
      <p>
        {{ completion.got }} of {{ completion.total }} achievements ·
        {{ Math.round(completion.pct) }}% complete
      </p></Modal
    >
  </section>
  <LoadState v-else :loading="loading" :error="error" @retry="loadGame"
    ><div class="state">
      <h1>Cartridge not found.</h1>
      <RouterLink class="button" to="/hub">Back to library →</RouterLink>
    </div></LoadState
  >
</template>
