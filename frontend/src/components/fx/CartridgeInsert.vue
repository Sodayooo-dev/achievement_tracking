<script setup lang="ts">
import { onMounted, onUnmounted, ref, useId } from 'vue'
import type { Game } from '@/api/types'
import { playSound } from '@/lib/sound'
defineProps<{ game: Game; loading: boolean }>()
const emit = defineEmits<{ complete: [] }>()
const phase = ref('ALIGNING CARTRIDGE')
const timers: ReturnType<typeof setTimeout>[] = []
const id = useId().replace(/[^a-zA-Z0-9_-]/g, '')
const clipId = `frontloader-mouth-${id}`
const cartridge = ref<SVGGElement>()
const progress = ref<HTMLElement>()
const animations: Animation[] = []
const finished = ref(false)
function finish() {
  if (finished.value) return
  finished.value = true
  timers.forEach(clearTimeout)
  emit('complete')
}
onMounted(() => {
  // The cartridge's travel follows its projected depth vector (100, 64).
  // The fixed clip plane passes through the slot, not through the console's silhouette.
  // This explicitly requested sequence runs even when OS reduced motion is on.
  // No page motion, screen flashes, or global accessibility preferences are changed.
  if (cartridge.value)
    animations.push(
      cartridge.value.animate(
        [
          { transform: 'translate(25px, 16px)', opacity: 0, offset: 0 },
          { transform: 'translate(0px, 0px)', opacity: 1, offset: 0.18 },
          { transform: 'translate(0px, 0px)', opacity: 1, offset: 0.3 },
          { transform: 'translate(-100px, -64px)', opacity: 1, offset: 0.73 },
          { transform: 'translate(-98px, -62.72px)', opacity: 1, offset: 0.8 },
          { transform: 'translate(-216px, -138.24px)', opacity: 1, offset: 1 },
        ],
        { duration: 1750, easing: 'ease-in-out', fill: 'forwards' },
      ),
    )
  if (progress.value)
    animations.push(
      progress.value.animate([{ width: '0%' }, { width: '100%' }], {
        duration: 2250,
        easing: 'steps(8, end)',
        fill: 'forwards',
      }),
    )
  timers.push(
    setTimeout(() => {
      phase.value = 'CARTRIDGE LOCKED'
      playSound('insert')
    }, 1500),
  )
  timers.push(
    setTimeout(() => {
      phase.value = 'READING SAVE DATA'
      playSound('confirm')
    }, 1800),
  )
  timers.push(setTimeout(finish, 2350))
})
onUnmounted(() => {
  timers.forEach(clearTimeout)
  animations.forEach((animation) => animation.cancel())
})
</script>
<template>
  <div class="insert-screen cartridge-sequence" role="status" aria-live="polite">
    <p class="eyebrow">A NEW WORLD, ONE CARTRIDGE AWAY</p>
    <div class="insertion-machine frontloader-machine" aria-hidden="true">
      <svg viewBox="0 0 600 330" class="frontloader-illustration">
        <defs>
          <clipPath :id="clipId" clipPathUnits="userSpaceOnUse">
            <!-- y + (24/99)x = 230.909: the top surface enters this fixed mouth plane. -->
            <path d="M0 230.9091 600 85.4545 600 330 0 330Z" />
          </clipPath>
        </defs>
        <ellipse cx="285" cy="245" rx="230" ry="22" fill="#000" opacity=".2" />
        <g stroke="#1e1b18" stroke-width="3" stroke-linejoin="round">
          <path d="M42 76 164 166 164 223 42 134Z" fill="#99968b" />
          <path d="M42 76 270 30 395 112 164 166Z" fill="#ddd9cf" />
          <path d="M55 79 270 42 380 112 165 154Z" fill="none" stroke="#9b978b" stroke-width="2" />
          <path d="M164 166 395 112 395 169 164 223Z" fill="#c9c5bc" />
          <path d="M232 164 353 135 353 159 232 188Z" fill="#11130f" />
          <path d="M239 168 347 142" fill="none" stroke="#5a5b50" stroke-width="2" />
          <path d="M55 115 151 185M55 126 151 196" fill="none" stroke="#716d63" stroke-width="2" />
          <path d="M80 79 155 63M85 85 160 69M90 91 165 75" stroke="#8c877b" stroke-width="2" />
          <path d="M176 185 211 177 211 188 176 196Z" fill="#6b685d" />
          <path d="M176 202 204 195" stroke="#716d63" stroke-width="2" />
          <circle cx="221" cy="190" r="3" fill="#d7263d" stroke="none" />
        </g>
        <text
          x="182"
          y="129"
          fill="#777064"
          font-size="8"
          transform="rotate(-13 182 129)"
          letter-spacing="2"
        >
          CARTRIDGE HUB
        </text>
        <g :clip-path="`url(#${clipId})`">
          <g
            ref="cartridge"
            class="frontloader-cartridge"
            stroke="#1e1b18"
            stroke-width="3"
            stroke-linejoin="round"
          >
            <path d="M343 236 442 212 542 276 443 300Z" fill="#ddd9cf" />
            <path d="M343 236 443 300 443 310 343 246Z" fill="#969185" />
            <path d="M443 300 542 276 542 286 443 310Z" fill="#b7b0a3" />
            <path
              d="M357 240 439 221 527 275 445 295Z"
              fill="none"
              stroke="#aaa393"
              stroke-width="2"
            />
            <path
              d="M375 250 434 236M383 256 442 242M391 262 450 248"
              stroke="#928b7e"
              stroke-width="2"
            />
            <path d="M451 300 535 280 535 285 451 305Z" fill="#d7263d" stroke="none" />
          </g>
        </g>
        <path d="M355 135 355 159M231 164 231 188" stroke="#eee9df" stroke-width="3" />
        <path d="M232 188 353 159" stroke="#716d63" stroke-width="3" />
        <text x="395" y="318" fill="#b9c3ac" font-size="10" letter-spacing="1">
          LABEL FACES DOWN ↓
        </text>
      </svg>
    </div>
    <p class="insertion-game-title">{{ game.title }}</p>
    <h2>{{ phase }}</h2>
    <p v-if="finished && loading" class="save-reading-note">Fetching your latest progress…</p>
    <div class="boot-progress" aria-hidden="true"><span ref="progress" /></div>
  </div>
</template>
