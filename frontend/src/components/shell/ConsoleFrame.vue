<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSession } from '@/stores/session'
import { usePlayer } from '@/stores/player'
import { useCatalog } from '@/stores/catalog'
import { useAsync } from '@/composables/useAsync'
import LoadState from '@/components/ui/LoadState.vue'
import AchievementToast from '@/components/fx/AchievementToast.vue'
import CrtScreen from './CrtScreen.vue'
import SoundControl from '@/components/ui/SoundControl.vue'
import { cartridgeControlKey } from '@/lib/cartridgeControl'
const session = useSession(),
  player = usePlayer(),
  catalog = useCatalog(),
  route = useRoute(),
  router = useRouter()
const insertionLocked = ref(false)
provide(cartridgeControlKey, insertionLocked)
const playing = computed(() => route.path.startsWith('/play/'))
const { loading, error, run } = useAsync(async () => {
  await catalog.load()
  await session.loadProfile()
  await player.load()
})
watch(
  () => session.profile?.id,
  () => {
    player.reset()
    void run()
  },
  { immediate: true },
)
const nav = computed(() => [
  { path: '/hub', name: 'My library', symbol: '▦' },
  { path: '/catalog', name: 'Game catalog', symbol: '▤' },
  { path: '/history', name: 'Save history', symbol: '◷' },
  ...(session.isAdmin ? [{ path: '/dev', name: 'Admin console', symbol: '⌘' }] : []),
])
function logout() {
  session.logout()
  player.reset()
  void router.push('/')
}
async function refresh() {
  await catalog.load(true)
  await run()
}
</script>
<template>
  <div class="app-shell">
    <a href="#main-content" class="skip-link">Skip to content</a>
    <header class="app-header">
      <RouterLink class="wordmark" to="/hub"
        ><span class="led on" />CARTRIDGE<br /><b>HUB</b
        ><small>ACHIEVEMENT SYSTEM</small></RouterLink
      >
      <nav aria-label="Main navigation">
        <RouterLink
          v-for="item in nav"
          :key="item.path"
          :to="item.path"
          :class="{ active: route.path.startsWith(item.path) }"
          ><span>{{ item.symbol }}</span
          >{{ item.name }}</RouterLink
        >
      </nav>
      <div class="player-menu">
        <SoundControl />
        <span class="avatar">{{ session.profile?.username.slice(0, 2).toUpperCase() }}</span>
        <div>
          <b>{{ session.profile?.username }}</b
          ><small>PLAYER {{ String(session.profile?.id).padStart(3, '0') }}</small>
        </div>
        <button class="text-button" @click="logout" aria-label="Log out">⏻</button>
      </div>
    </header>
    <main id="main-content" class="console-screen">
      <div class="hardware-strip">
        <span><i class="led on" /> SYSTEM ONLINE</span>
        <button
          v-if="playing"
          class="hardware-eject"
          :disabled="insertionLocked || loading"
          data-sound="back"
          aria-label="Eject cartridge and return to library"
          @click="router.push('/hub')"
        >
          <span aria-hidden="true">⏏</span> Eject
        </button>
        <span v-else>CH–001 / PERSONAL SAVE FILE</span>
      </div>
      <CrtScreen class="console-glass"
        ><LoadState :loading="loading" :error="error" @retry="run"><slot /></LoadState
      ></CrtScreen>
    </main>
    <footer class="xp-hud">
      <div class="level-badge">
        <span>LV</span><strong>{{ player.progress.current?.number ?? '—' }}</strong>
      </div>
      <div class="xp-info">
        <div>
          <b>{{ player.progress.current?.title ?? 'Unranked' }}</b
          ><span>{{
            player.progress.next
              ? `${player.progress.intoLevel.toLocaleString()} / ${player.progress.needed.toLocaleString()} XP`
              : catalog.levels.length
                ? 'MAX LEVEL'
                : 'NO LEVELS CONFIGURED'
          }}</span>
        </div>
        <div
          class="xp-track"
          role="progressbar"
          aria-label="Experience towards next level"
          :aria-valuenow="Math.round(player.progress.pct)"
          :aria-valuemin="0"
          :aria-valuemax="100"
        >
          <div :style="{ width: player.progress.pct + '%' }" />
        </div>
      </div>
      <div class="total-xp">
        <strong>{{ player.totalExp.toLocaleString() }}</strong
        ><small>LIFETIME XP</small>
      </div>
      <button
        class="text-button refresh"
        :disabled="loading"
        @click="refresh"
        aria-label="Refresh save data"
      >
        ↻
      </button>
    </footer>
    <div class="under-shell">
      <span>YOUR PROGRESS, PRESERVED.</span
      ><span class="speaker" aria-hidden="true">▰ ▰ ▰ ▰ ▰ ▰ ▰</span
      ><span>KEEP PLAYING. KEEP COLLECTING.</span>
    </div>
    <AchievementToast :ready="!loading && !error" />
  </div>
</template>
