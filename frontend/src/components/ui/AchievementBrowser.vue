<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref } from 'vue'
import type { Game, ThemeItem } from '@/api/types'
import { themes } from '@/themes/registry'
import type { ThemeKey } from '@/lib/genre'
import GameSelect from './GameSelect.vue'
import Modal from './Modal.vue'
import AchievementDetail from '@/themes/AchievementDetail.vue'
import { gridKeys } from '@/composables/useGridKeys'
const props = defineProps<{
  game: Game
  items: ThemeItem[]
  theme: ThemeKey
  completion: { got: number; total: number; pct: number }
}>()
const search = ref(''),
  status = ref('all'),
  sort = ref('default'),
  layout = ref('theme')
const filtersOpen = ref(false)
const hovered = ref<ThemeItem | null>(null),
  pinned = ref<ThemeItem | null>(null),
  tooltip = ref<HTMLElement>()
const position = ref<Record<string, string>>({ left: '0px', top: '0px', width: '300px' })
let trigger: HTMLElement | null = null,
  timer: ReturnType<typeof setTimeout>
const visible = computed(() => {
  const list = props.items.filter(
    (a) =>
      (status.value === 'all' || a.unlocked === (status.value === 'unlocked')) &&
      `${a.name} ${a.description}`.toLowerCase().includes(search.value.toLowerCase()),
  )
  return sort.value === 'name'
    ? list.sort((a, b) => a.name.localeCompare(b.name))
    : sort.value === 'xp'
      ? list.sort((a, b) => b.exp_value - a.exp_value)
      : list
})
function dismiss() {
  clearTimeout(timer)
  hovered.value = null
  trigger?.removeAttribute('aria-describedby')
}
function leave() {
  clearTimeout(timer)
  timer = setTimeout(dismiss, 180)
}
function keep() {
  clearTimeout(timer)
}
function clearFilters() {
  search.value = ''
  status.value = 'all'
}
async function inspect(e: Event, pin = false) {
  const target = (e.target as HTMLElement).closest<HTMLElement>('[data-achievement-id]')
  if (!target || pinned.value) return
  const item = props.items.find((a) => a.id === Number(target.dataset.achievementId))
  if (!item) return
  clearTimeout(timer)
  if (pin) {
    dismiss()
    pinned.value = item
    return
  }
  trigger?.removeAttribute('aria-describedby')
  trigger = target
  target.setAttribute('aria-describedby', 'achievement-preview')
  hovered.value = item
  await placeTooltip()
}
async function placeTooltip() {
  if (!trigger || !hovered.value) return
  const glass = trigger.closest('.crt-glass')!.getBoundingClientRect(),
    anchor = trigger.getBoundingClientRect()
  const width = Math.min(340, glass.width - 28)
  position.value.width = `${width}px`
  position.value.maxHeight = `${Math.min(300, glass.height - 24)}px`
  await nextTick()
  const height = tooltip.value?.getBoundingClientRect().height ?? 190
  const x = Math.max(glass.left + 14, Math.min(anchor.left, glass.right - width - 14))
  const y =
    anchor.bottom + height + 14 < glass.bottom
      ? anchor.bottom + 8
      : Math.max(glass.top + 12, anchor.top - height - 8)
  position.value = {
    ...position.value,
    left: `${x}px`,
    top: `${Math.min(y, glass.bottom - height - 12)}px`,
  }
}
function scrolled(event: Event) {
  if (tooltip.value?.contains(event.target as Node)) return
  if (document.activeElement === trigger) void placeTooltip()
  else dismiss()
}
function gridNavigation(event: KeyboardEvent) {
  if (!event.defaultPrevented) gridKeys(event)
}
function keys(e: KeyboardEvent) {
  if (e.key === 'Escape') dismiss()
}
document.addEventListener('keydown', keys)
document.addEventListener('scroll', scrolled, true)
onUnmounted(() => {
  dismiss()
  document.removeEventListener('keydown', keys)
  document.removeEventListener('scroll', scrolled, true)
})
</script>
<template>
  <div class="achievement-browser">
    <div class="achievement-filters compact-controls">
      <label class="achievement-search"
        ><span class="sr-only">Search achievements</span
        ><input v-model="search" type="search" placeholder="Search objectives…"
      /></label>
      <div class="status-switch" role="group" aria-label="Achievement status">
        <button
          v-for="option in [
            { value: 'all', label: 'All' },
            { value: 'locked', label: 'Locked' },
            { value: 'unlocked', label: 'Unlocked' },
          ]"
          :key="option.value"
          :aria-pressed="status === option.value"
          @click="status = option.value"
        >
          {{ option.label }}
        </button>
      </div>
      <div class="control-actions">
        <div class="view-switch" role="group" aria-label="Achievement view">
          <button
            aria-label="Genre screen"
            :aria-pressed="layout === 'theme'"
            @click="layout = 'theme'"
          >
            ▦</button
          ><button
            aria-label="Compact list"
            :aria-pressed="layout === 'list'"
            @click="layout = 'list'"
          >
            ☷
          </button>
        </div>
        <button
          class="secondary-filter-button"
          :aria-expanded="filtersOpen"
          aria-haspopup="dialog"
          @click="filtersOpen = true"
        >
          Filters<span v-if="sort !== 'default'" class="filter-dot" aria-label="Custom sort active"
            >●</span
          >
        </button>
      </div>
    </div>
    <p class="results-count compact-results">
      {{ visible.length }} / {{ items.length }} objectives<span
        >Select an objective for details</span
      >
    </p>
    <Modal v-if="filtersOpen" title="Display options" @close="filtersOpen = false"
      ><div class="secondary-filters">
        <label
          >Sort objectives<GameSelect
            v-model="sort"
            label="Achievement sort"
            :options="[
              { value: 'default', label: 'Original order' },
              { value: 'name', label: 'Name A–Z' },
              { value: 'xp', label: 'XP, highest first' },
            ]" /></label
        ><button class="primary" @click="filtersOpen = false">Done</button>
      </div></Modal
    >
    <div
      @pointerover="inspect"
      @pointerout="leave"
      @focusin="inspect"
      @focusout="leave"
      @click="inspect($event, true)"
      @keydown="gridNavigation"
    >
      <div v-if="!visible.length" class="state">
        <h2>No matching objectives.</h2>
        <button @click="clearFilters">Clear filters</button>
      </div>
      <div v-else-if="layout === 'list'" class="objective-list">
        <button
          v-for="item in visible"
          :key="item.id"
          :data-achievement-id="item.id"
          data-cell
          :class="{ unlocked: item.unlocked }"
        >
          <span>{{ item.unlocked ? '✓' : '◇' }}</span
          ><span
            ><b>{{ item.name }}</b
            ><small>{{ item.unlocked ? 'Unlocked' : 'Locked' }}</small></span
          ><strong>{{ item.exp_value }} XP</strong>
        </button>
      </div>
      <component
        :is="themes[theme]"
        v-else
        :game="game"
        :items="visible"
        :all-items="items"
        :completion="completion"
      />
    </div>
    <Teleport to="body"
      ><div
        v-if="hovered && !pinned"
        id="achievement-preview"
        ref="tooltip"
        role="tooltip"
        class="achievement-tooltip"
        :style="position"
        @pointerenter="keep"
        @pointerleave="leave"
      >
        <AchievementDetail :item="hovered" />
        <p class="preview-hint">Select for full details</p>
      </div></Teleport
    >
    <Modal v-if="pinned" :title="pinned.name" @close="pinned = null"
      ><AchievementDetail :item="pinned"
    /></Modal>
  </div>
</template>
