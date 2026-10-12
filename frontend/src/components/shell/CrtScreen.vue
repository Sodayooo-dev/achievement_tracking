<script setup lang="ts">
import { nextTick, ref, useId, watch } from 'vue'
import { useRoute } from 'vue-router'
defineProps<{ label?: string }>()
const scrollArea = ref<HTMLElement>(),
  route = useRoute()
const filterId = `crt-chromatic-${useId().replace(/[^a-zA-Z0-9_-]/g, '')}`
const cornerMask = `${import.meta.env.BASE_URL}crt-corner-mask.svg`
watch(
  () => route.fullPath,
  async () => {
    await nextTick()
    scrollArea.value?.scrollTo({ top: 0, left: 0, behavior: 'instant' })
  },
)
</script>
<template>
  <div class="crt-glass">
    <svg class="crt-filter-definitions" aria-hidden="true" focusable="false" width="0" height="0">
      <defs>
        <filter
          :id="filterId"
          x="-2%"
          y="-2%"
          width="104%"
          height="104%"
          color-interpolation-filters="sRGB"
        >
          <feColorMatrix
            in="SourceGraphic"
            type="matrix"
            values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0"
            result="red-channel"
          />
          <feOffset in="red-channel" dx="1" dy="0.3" result="red-shift" />
          <feColorMatrix
            in="SourceGraphic"
            type="matrix"
            values="0 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 1 0"
            result="cyan-channel"
          />
          <feOffset in="cyan-channel" dx="-1" dy="-0.3" result="cyan-shift" />
          <feBlend in="red-shift" in2="cyan-shift" mode="screen" result="split-channels" />
          <feImage
            :href="cornerMask"
            x="0"
            y="0"
            width="100%"
            height="100%"
            preserveAspectRatio="none"
            result="corner-mask"
          />
          <feComposite
            in="split-channels"
            in2="corner-mask"
            operator="in"
            result="chromatic-corners"
          />
          <feComposite in="SourceGraphic" in2="corner-mask" operator="out" result="sharp-center" />
          <feComposite
            in="chromatic-corners"
            in2="sharp-center"
            operator="arithmetic"
            k1="0"
            k2="1"
            k3="1"
            k4="0"
          />
        </filter>
      </defs>
    </svg>
    <div
      ref="scrollArea"
      class="crt-scroll"
      :style="{ filter: `url(#${filterId})` }"
      tabindex="0"
      role="region"
      :aria-label="label ?? 'Console screen content'"
    >
      <slot />
    </div>
    <div class="crt-optics" aria-hidden="true">
      <i class="crt-corner top-left" /><i class="crt-corner top-right" />
      <i class="crt-corner bottom-left" /><i class="crt-corner bottom-right" />
    </div>
  </div>
</template>
