<script setup lang="ts">
import { onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSession } from '@/stores/session'
import { usePlayer } from '@/stores/player'
import ConsoleFrame from '@/components/shell/ConsoleFrame.vue'
import SoundControl from '@/components/ui/SoundControl.vue'
import { installUiSounds } from '@/lib/sound'
const route = useRoute(),
  router = useRouter(),
  session = useSession(),
  player = usePlayer()
function expire() {
  session.expire()
  player.reset()
  void router.push('/game-over')
}
window.addEventListener('session-expired', expire)
const removeUiSounds = installUiSounds()
onUnmounted(() => {
  window.removeEventListener('session-expired', expire)
  removeUiSounds()
})
</script>
<template>
  <ConsoleFrame v-if="session.isLoggedIn && route.meta.auth"><RouterView /></ConsoleFrame
  ><RouterView v-else />
  <SoundControl v-if="!route.meta.auth && route.path !== '/'" class="standalone-sound-control" />
</template>
