<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSession } from '@/stores/session'
import { ApiError } from '@/api/client'
import CrtScreen from '@/components/shell/CrtScreen.vue'
import SoundControl from '@/components/ui/SoundControl.vue'
import { playSound } from '@/lib/sound'
const session = useSession(),
  router = useRouter()
const started = ref(false),
  mode = ref<'login' | 'register'>('login'),
  busy = ref(false),
  error = ref(''),
  fields = ref<Record<string, unknown>>({})
const form = reactive({
  username: '',
  password: '',
  first_name: '',
  last_name: '',
})
function start(e: KeyboardEvent) {
  if (e.key === 'Enter' && !started.value) {
    e.preventDefault()
    started.value = true
  }
}
onMounted(() => window.addEventListener('keydown', start))
onUnmounted(() => window.removeEventListener('keydown', start))
function switchMode(value: 'login' | 'register') {
  mode.value = value
  error.value = ''
  fields.value = {}
}
async function submit() {
  busy.value = true
  error.value = ''
  fields.value = {}
  try {
    if (mode.value === 'login') await session.login(form.username, form.password)
    else await session.register(form)
    await router.push('/hub')
    playSound('confirm')
  } catch (e) {
    playSound('error')
    if (e instanceof ApiError) {
      fields.value = e.fields
      error.value = e.status === 401 ? 'Username or password is invalid.' : e.message
    } else error.value = e instanceof Error ? e.message : 'Unable to load your save file.'
  } finally {
    busy.value = false
  }
}
</script>
<template>
  <main class="title-page">
    <div class="title-top">
      <span>CARTRIDGE HUB™</span><span>PLAYER ACHIEVEMENT SYSTEM / 01</span><SoundControl />
    </div>
    <section class="title-console">
      <div class="console-brand">
        <span class="led" :class="{ on: busy }" /><span>CARTRIDGE HUB</span
        ><span class="model">CH–001</span>
      </div>
      <CrtScreen class="title-screen" label="Title screen and save slots">
        <div class="screen-corner">INSERT COIN? NAH. JUST YOU.</div>
        <div class="pixel-emblem" aria-hidden="true">✦</div>
        <p class="eyebrow">EVERY UNLOCK HAS A STORY</p>
        <h1>CARTRIDGE<br /><span>HUB</span></h1>
        <p class="title-description">
          Your games. Your milestones.<br />One very satisfying collection.
        </p>
        <button v-if="!started" class="start-button" @click="started = true">
          PRESS START <span>↵</span>
        </button>
        <div
          v-else
          class="save-panel"
          :class="{ 'invalid-save': error === 'Username or password is invalid.' }"
        >
          <div class="save-tabs">
            <button :class="{ selected: mode === 'login' }" @click="switchMode('login')">
              01 / Continue</button
            ><button :class="{ selected: mode === 'register' }" @click="switchMode('register')">
              02 / New game
            </button>
          </div>
          <form @submit.prevent="submit" :aria-busy="busy">
            <h2>
              {{ mode === 'login' ? 'CONTINUE YOUR GAME' : 'CREATE A SAVE FILE' }}
            </h2>
            <label
              v-for="key in mode === 'login'
                ? (['username', 'password'] as const)
                : (['username', 'password', 'first_name', 'last_name'] as const)"
              :key="key"
              >{{ key.replace('_', ' ')
              }}<span v-if="key === 'first_name' || key === 'last_name'" class="muted">
                (optional)</span
              ><input
                v-model="form[key]"
                :type="key === 'password' ? 'password' : 'text'"
                :autocomplete="
                  key === 'password'
                    ? mode === 'login'
                      ? 'current-password'
                      : 'new-password'
                    : key === 'username'
                      ? 'username'
                      : key === 'first_name'
                        ? 'given-name'
                        : 'family-name'
                "
                :required="key === 'username' || key === 'password'"
                :aria-invalid="Boolean(fields[key])"
                :aria-describedby="fields[key] ? `error-${key}` : undefined"
              /><small v-if="fields[key]" :id="`error-${key}`" class="field-error">{{
                Array.isArray(fields[key]) ? (fields[key] as string[]).join(' ') : fields[key]
              }}</small></label
            >
            <p v-if="error" class="field-error" role="alert">{{ error }}</p>
            <button class="primary" :disabled="busy">
              {{ busy ? 'Loading save…' : mode === 'login' ? 'Let’s play →' : 'Begin adventure →' }}
            </button>
          </form>
        </div>
        <div class="screen-bottom">
          <span>NO HIGH SCORE TOO SMALL</span><span>★ SAVE YOUR PROGRESS</span>
        </div>
      </CrtScreen>
      <div class="console-controls">
        <span class="speaker" aria-hidden="true">▰ ▰ ▰ ▰ ▰</span
        ><span class="controller-decoration" aria-hidden="true">✚ <i>A</i><i>B</i></span
        ><span class="serial">BUILT FOR THE COMPLETIONIST IN YOU</span>
      </div>
    </section>
    <footer class="title-footer">A LITTLE NOSTALGIA. A LOT OF ACHIEVEMENTS.</footer>
  </main>
</template>
