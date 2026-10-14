<script setup lang="ts">
import { computed, ref } from 'vue'
import { useCatalog } from '@/stores/catalog'
import { usePlayer } from '@/stores/player'
import GameArtwork from '@/components/ui/GameArtwork.vue'
import { genreToTheme } from '@/lib/genre'
import GameSelect from '@/components/ui/GameSelect.vue'
import { addToLibrary } from '@/api/endpoints'
const catalog = useCatalog(),
  player = usePlayer(),
  search = ref(''),
  genre = ref('')
const genres = computed(() => [...new Set(catalog.games.map((g) => g.genre))].sort())
const games = computed(() =>
  catalog.games.filter(
    (g) =>
      g.title.toLowerCase().includes(search.value.toLowerCase()) &&
      (!genre.value || g.genre === genre.value),
  ),
)
const owned = (id: number) => player.library.some((l) => l.game_id === id)
const adding = ref(new Set<number>()),
  errors = ref<Record<number, string>>({})
async function add(id: number) {
  if (adding.value.has(id)) return
  adding.value.add(id)
  delete errors.value[id]
  try {
    const row = await addToLibrary(id)
    if (!owned(id)) player.library.push(row)
  } catch (e) {
    errors.value[id] = e instanceof Error ? e.message : 'Could not add game. Please retry.'
  } finally {
    adding.value.delete(id)
  }
}
function clearFilters() {
  search.value = ''
  genre.value = ''
}
</script>
<template>
  <section class="page-content">
    <div class="page-heading">
      <div>
        <p class="eyebrow">FIND YOUR NEXT OBSESSION</p>
        <h1>The game catalog<span class="red">.</span></h1>
        <p>A world of achievements, waiting to be collected.</p>
      </div>
      <span class="catalog-count">{{ catalog.games.length }} TITLES</span>
    </div>
    <div class="filters">
      <label
        >Search games<input v-model="search" type="search" placeholder="Find a cartridge…" /></label
      ><label
        >Genre<GameSelect
          v-model="genre"
          label="Catalog genre"
          :options="[
            { value: '', label: 'All genres' },
            ...genres.map((value) => ({ value, label: value })),
          ]"
      /></label>
    </div>
    <div v-if="games.length" class="catalog-grid">
      <article
        v-for="game in games"
        :key="game.id"
        class="catalog-card"
        :class="genreToTheme(game.genre)"
      >
        <div class="catalog-art">
          <span>{{ game.genre }}</span
          ><GameArtwork :title="game.title" :url="game.image_url" /><small
            >CH–{{ String(game.id).padStart(3, '0') }}</small
          >
        </div>
        <div class="catalog-body">
          <p class="eyebrow" :title="game.publisher">{{ game.publisher }}</p>
          <h2 :title="game.title">{{ game.title }}</h2>
          <p>
            {{ catalog.achievements.filter((a) => a.game_id === game.id).length }}
            achievements
          </p>
          <RouterLink v-if="owned(game.id)" class="button" :to="`/play/${game.id}`"
            >✓ In library <span>Play →</span></RouterLink
          ><button v-else class="catalog-add" :disabled="adding.has(game.id)" @click="add(game.id)">
            {{ adding.has(game.id) ? 'Adding…' : '+ Add to my library' }}
          </button>
          <p v-if="errors[game.id]" class="field-error" role="alert">{{ errors[game.id] }}</p>
        </div>
      </article>
    </div>
    <div v-else class="state">
      <h2>
        {{ catalog.games.length ? 'No matching cartridges' : 'The catalog is waiting' }}
      </h2>
      <p>
        {{
          catalog.games.length
            ? 'Try another title or genre.'
            : 'Games will appear here when a developer adds them.'
        }}
      </p>
      <button v-if="catalog.games.length" @click="clearFilters">Clear filters</button>
    </div>
  </section>
</template>
