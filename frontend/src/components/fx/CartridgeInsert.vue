<script setup lang="ts">
import { onMounted, onUnmounted, ref, useId } from 'vue'
import type { Game } from '@/api/types'
import { playSound } from '@/lib/sound'
import { cartridgePose, frontloader } from '@/lib/cartridgeProjection'
defineProps<{ game: Game; loading: boolean }>()
const emit = defineEmits<{ complete: [] }>()
const id = useId().replace(/[^a-zA-Z0-9_-]/g, '')
const phase = ref('ALIGNING CARTRIDGE'),
  finished = ref(false)
const pieces = ref<SVGGElement[]>([]),
  progress = ref<HTMLElement>()
const topShape = `cartridge-top-${id}`,
  sideShape = `cartridge-sides-${id}`
const aperture = `slot-aperture-${id}`
const topInside = `top-inside-${id}`,
  topOutside = `top-outside-${id}`
const sideInside = `side-inside-${id}`,
  sideOutside = `side-outside-${id}`
const seam = frontloader.seam,
  underside = seam + frontloader.thickness
const topPoints = frontloader.top.map((point) => point.join(',')).join(' ')
const [leadingLeft, leadingRight, trailingRight, trailingLeft] = frontloader.top
const points = (vertices: readonly (readonly number[])[]) =>
  vertices.map((point) => point.join(',')).join(' ')
const lowered = (point: readonly number[]) => [point[0]!, point[1]! + frontloader.thickness]
const leftFace = points([leadingLeft, trailingLeft, lowered(trailingLeft), lowered(leadingLeft)])
const rightFace = points([
  leadingRight,
  trailingRight,
  lowered(trailingRight),
  lowered(leadingRight),
])
const trailingFace = points([
  trailingLeft,
  trailingRight,
  lowered(trailingRight),
  lowered(trailingLeft),
])
const slotPath = `M${frontloader.slot.left} ${frontloader.slot.top}H${frontloader.slot.right}V${frontloader.slot.bottom}H${frontloader.slot.left}Z`
let frame = 0,
  deadline: ReturnType<typeof setTimeout>,
  started = 0
function render(elapsed: number) {
  const pose = cartridgePose(elapsed)
  for (const piece of pieces.value) {
    piece.setAttribute('transform', `translate(0 ${pose.y})`)
    piece.style.opacity = String(pose.opacity)
  }
  if (progress.value) progress.value.style.width = `${pose.progress * 100}%`
  if (phase.value !== pose.phase) {
    phase.value = pose.phase
    if (pose.phase === 'CARTRIDGE LOCKED') playSound('insert')
    if (pose.phase === 'READING SAVE DATA') playSound('confirm')
  }
}
function finish() {
  if (finished.value) return
  render(frontloader.duration)
  finished.value = true
  cancelAnimationFrame(frame)
  clearTimeout(deadline)
  emit('complete')
}
function tick(time: number) {
  const elapsed = time - started
  render(elapsed)
  if (elapsed >= frontloader.duration) finish()
  else frame = requestAnimationFrame(tick)
}
onMounted(() => {
  started = performance.now()
  render(0)
  frame = requestAnimationFrame(tick)
  deadline = setTimeout(finish, frontloader.duration)
})
onUnmounted(() => {
  cancelAnimationFrame(frame)
  clearTimeout(deadline)
})
</script>
<template>
  <div class="insert-screen cartridge-sequence" role="status" aria-live="polite">
    <p class="eyebrow">A NEW WORLD, ONE CARTRIDGE AWAY</p>
    <div class="insertion-machine frontloader-machine" aria-hidden="true">
      <svg viewBox="0 0 580 400" class="frontloader-illustration">
        <defs>
          <clipPath :id="aperture" clipPathUnits="userSpaceOnUse">
            <rect
              :x="frontloader.slot.left"
              :y="frontloader.slot.top"
              :width="frontloader.slot.right - frontloader.slot.left"
              :height="frontloader.slot.bottom - frontloader.slot.top"
            />
          </clipPath>
          <clipPath :id="topInside" clipPathUnits="userSpaceOnUse">
            <rect x="0" y="0" width="580" :height="seam" />
          </clipPath>
          <clipPath :id="topOutside" clipPathUnits="userSpaceOnUse">
            <rect x="0" :y="seam" width="580" :height="400 - seam" />
          </clipPath>
          <clipPath :id="sideInside" clipPathUnits="userSpaceOnUse">
            <rect x="0" y="0" width="580" :height="underside" />
          </clipPath>
          <clipPath :id="sideOutside" clipPathUnits="userSpaceOnUse">
            <rect x="0" :y="underside" width="580" :height="400 - underside" />
          </clipPath>
          <g :id="topShape" stroke="#28251f" stroke-width="2" stroke-linejoin="round">
            <polygon :points="topPoints" fill="#ddd9cf" />
            <path d="M208 254 372 254 385 333 195 333Z" fill="none" stroke="#aaa393" />
            <path d="M216 270H365M214 278H366M213 286H368" stroke="#928b7e" />
          </g>
          <g :id="sideShape" stroke="#28251f" stroke-width="2" stroke-linejoin="round">
            <polygon :points="leftFace" fill="#969185" />
            <polygon :points="rightFace" fill="#a59f91" />
            <polygon :points="trailingFace" fill="#b7b0a3" />
            <rect
              :x="trailingLeft[0] + 9"
              :y="trailingLeft[1] + frontloader.thickness * 0.375"
              :width="trailingRight[0] - trailingLeft[0] - 18"
              :height="frontloader.thickness * 0.375"
              fill="#d7263d"
              stroke="none"
            />
          </g>
        </defs>
        <ellipse cx="290" cy="243" rx="240" ry="18" fill="#000" opacity=".18" />
        <!-- Rear/top and the dark cavity are behind every cartridge fragment. -->
        <g stroke="#28251f" stroke-width="3" stroke-linejoin="round">
          <path d="M90 65H490L520 160H60Z" fill="#ddd9cf" />
          <path d="M100 76H480L505 150H75Z" fill="none" stroke="#aaa393" stroke-width="2" />
          <path d="M112 88H204M109 98H201M106 108H198" stroke="#928b7e" stroke-width="2" />
          <path d="M60 160H520V230H60Z" fill="#c9c5bc" />
          <path :d="slotPath" fill="#10120e" />
        </g>
        <text x="290" y="133" text-anchor="middle" fill="#777064" font-size="9" letter-spacing="2">
          CARTRIDGE HUB
        </text>
        <!-- Inserted fragments occupy only the real aperture. Their cut edges share
             the exact same boundaries as the exposed fragments below. -->
        <g :clip-path="`url(#${aperture})`">
          <g
            v-for="section in [
              { clip: topInside, shape: topShape },
              { clip: sideInside, shape: sideShape },
            ]"
            :key="section.clip"
            :clip-path="`url(#${section.clip})`"
          >
            <g ref="pieces"><use :href="`#${section.shape}`" /></g>
          </g>
        </g>
        <!-- The bezel covers only the inserted geometry; the exposed cartridge is
             drawn in front of it, including the portion projected over the front face. -->
        <path
          :d="`M60 160H520V230H60Z ${slotPath}`"
          fill="#c9c5bc"
          fill-rule="evenodd"
          stroke="#28251f"
          stroke-width="3"
          stroke-linejoin="round"
        />
        <rect
          x="86"
          y="189"
          width="42"
          height="15"
          fill="#777367"
          stroke="#28251f"
          stroke-width="2"
        />
        <circle cx="151" cy="202" r="3.5" fill="#d7263d" />
        <path d="M86 215H125" stroke="#928b7e" stroke-width="2" />
        <g
          v-for="section in [
            { clip: topOutside, shape: topShape },
            { clip: sideOutside, shape: sideShape },
          ]"
          :key="section.clip"
          :clip-path="`url(#${section.clip})`"
        >
          <g ref="pieces"><use :href="`#${section.shape}`" /></g>
        </g>
        <path
          :d="`M${frontloader.slot.left} ${frontloader.slot.top}H${frontloader.slot.right}`"
          stroke="#777367"
          stroke-width="2"
        />
        <text x="290" y="390" text-anchor="middle" fill="#b9c3ac" font-size="10" letter-spacing="1">
          LABEL FACES DOWN ↓
        </text>
      </svg>
    </div>
    <p class="insertion-game-title">{{ game.title }}</p>
    <h2>{{ phase }}</h2>
    <p v-if="finished && loading" class="save-reading-note">Fetching your latest progress…</p>
    <div class="boot-progress" :class="{ 'is-reading': finished && loading }" aria-hidden="true">
      <span ref="progress" />
    </div>
  </div>
</template>
