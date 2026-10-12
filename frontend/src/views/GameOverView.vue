<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '@/stores/session'
const router = useRouter(),
  session = useSession(),
  seconds = ref(10),
  paused = ref(false)
let timer: ReturnType<typeof setInterval>
function pause() {
  paused.value = true
}
function quit() {
  session.logout()
  void router.push('/')
}
onMounted(() => {
  session.expire()
  timer = setInterval(() => {
    if (!paused.value && --seconds.value <= 0) {
      clearInterval(timer)
      void router.push('/')
    }
  }, 1000)
  window.addEventListener('keydown', pause)
  window.addEventListener('pointerdown', pause)
})
onUnmounted(() => {
  clearInterval(timer)
  window.removeEventListener('keydown', pause)
  window.removeEventListener('pointerdown', pause)
})
</script>
<template>
  <main class="error-page">
    <span class="eyebrow">CONNECTION TO SAVE FILE LOST</span>
    <h1>GAME<br /><span class="red">OVER</span></h1>
    <p>Session expired. Your achievements are safe.</p>
    <h2>Continue?</h2>
    <div>
      <RouterLink class="button primary" to="/">Continue →</RouterLink
      ><button @click="quit">Quit</button>
    </div>
    <small>{{ paused ? 'Take your time, player.' : `Returning to title in ${seconds}s` }}</small>
  </main>
</template>
