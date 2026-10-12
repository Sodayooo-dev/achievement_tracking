<script setup lang="ts">
import type { Game } from '@/api/types'
import { genreToTheme } from '@/lib/genre'
import PixelIcon from '@/components/ui/PixelIcon.vue'
defineProps<{
  game: Game
  completion: { got: number; total: number; pct: number }
  index: number
}>()
</script>
<template>
  <RouterLink
    :to="`/play/${game.id}`"
    data-cell
    :tabindex="index === 0 ? 0 : -1"
    class="cartridge"
    :class="[genreToTheme(game.genre), { perfect: completion.total > 0 && completion.pct === 100 }]"
    :aria-label="`${game.title}, ${completion.got} of ${completion.total} achievements`"
    ><div class="cartridge-top">
      <span>CH / {{ String(game.id).padStart(3, '0') }}</span
      ><span>▼</span>
    </div>
    <div class="cartridge-label">
      <div class="label-top">
        <span>{{ game.genre }}</span
        ><span>{{ completion.pct === 100 ? '★ PERFECT' : 'PLAY' }}</span>
      </div>
      <PixelIcon :name="game.title" />
      <h3>{{ game.title }}</h3>
      <p>{{ game.publisher }}</p>
      <div class="label-bottom"><span>CARTRIDGE HUB</span><span>®</span></div>
    </div>
    <div class="cartridge-bottom">
      <span
        >{{ completion.got }}<span class="muted"> / {{ completion.total }}</span>
        <span class="star">★</span></span
      ><strong>{{ Math.round(completion.pct) }}%</strong>
    </div>
    <div class="mini-progress">
      <i :style="{ width: completion.pct + '%' }" />
    </div>
    <div class="cartridge-ridges" aria-hidden="true"
  /></RouterLink>
</template>
