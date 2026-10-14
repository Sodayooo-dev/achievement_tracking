<script setup lang="ts">
import { computed, nextTick, onUnmounted, ref, useId } from 'vue'
type Option = { value: string | number; label: string }
const props = withDefaults(
  defineProps<{
    modelValue: string | number
    options: Option[]
    label: string
    placeholder?: string
    disabled?: boolean
    required?: boolean
  }>(),
  { placeholder: 'Select…' },
)
const emit = defineEmits<{ 'update:modelValue': [value: string | number] }>()
const open = ref(false),
  search = ref(''),
  active = ref(0),
  root = ref<HTMLElement>(),
  input = ref<HTMLInputElement>(),
  popup = ref<HTMLElement>()
const position = ref<Record<string, string>>({ left: '0px', top: '0px', width: '260px' })
const id = `select-${useId()}`
const chosen = computed(() =>
  props.options.find((o) => String(o.value) === String(props.modelValue)),
)
const visible = computed(() =>
  props.options.filter((o) => o.label.toLowerCase().includes(search.value.toLowerCase())),
)
async function toggle() {
  if (props.disabled) return
  open.value = !open.value
  search.value = ''
  active.value = 0
  if (open.value) {
    const rect = root.value!.getBoundingClientRect(),
      glass = root.value?.closest('.crt-glass')?.getBoundingClientRect()
    const bounds = glass ?? {
      left: 0,
      right: window.innerWidth,
      top: 0,
      bottom: window.innerHeight,
    }
    const width = Math.min(Math.max(220, rect.width), bounds.right - bounds.left - 24)
    const availableBelow = bounds.bottom - rect.bottom - 12
    const height = Math.max(64, Math.min(280, bounds.bottom - bounds.top - 24))
    position.value = {
      left: `${Math.max(bounds.left + 12, Math.min(rect.left, bounds.right - width - 12))}px`,
      top: `${availableBelow >= height ? rect.bottom + 6 : Math.max(bounds.top + 12, rect.top - height - 6)}px`,
      width: `${width}px`,
      maxHeight: `${height}px`,
    }
    await nextTick()
    input.value?.focus()
  }
}
function select(option: Option) {
  emit('update:modelValue', option.value)
  close()
}
function close() {
  open.value = false
  root.value?.querySelector<HTMLButtonElement>('button')?.focus()
}
function keys(e: KeyboardEvent) {
  if (!open.value) {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault()
      void toggle()
    }
    return
  }
  if (e.key === 'Escape') {
    e.preventDefault()
    e.stopPropagation()
    close()
  }
  if (e.key === 'Tab') {
    close()
    return
  }
  if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(e.key)) {
    e.preventDefault()
    active.value =
      e.key === 'Home'
        ? 0
        : e.key === 'End'
          ? visible.value.length - 1
          : Math.max(
              0,
              Math.min(visible.value.length - 1, active.value + (e.key === 'ArrowDown' ? 1 : -1)),
            )
    void nextTick(() =>
      document.getElementById(`${id}-${active.value}`)?.scrollIntoView({ block: 'nearest' }),
    )
  }
  if (e.key === 'Enter') {
    e.preventDefault()
    const option = visible.value[active.value]
    if (option) select(option)
  }
}
function outside(e: PointerEvent) {
  if (
    open.value &&
    !root.value?.contains(e.target as Node) &&
    !popup.value?.contains(e.target as Node)
  )
    open.value = false
}
function scroll(e: Event) {
  if (!popup.value?.contains(e.target as Node)) open.value = false
}
document.addEventListener('pointerdown', outside)
document.addEventListener('scroll', scroll, true)
onUnmounted(() => {
  document.removeEventListener('pointerdown', outside)
  document.removeEventListener('scroll', scroll, true)
})
</script>
<template>
  <div ref="root" class="game-select" @keydown="keys">
    <button
      type="button"
      class="select-trigger"
      :disabled="disabled"
      :aria-label="label"
      :aria-expanded="open"
      aria-haspopup="listbox"
      :aria-controls="`${id}-list`"
      @click="toggle"
    >
      <span>{{ chosen?.label ?? placeholder }}</span
      ><span aria-hidden="true">▾</span>
    </button>
    <Teleport to="body"
      ><div v-if="open" ref="popup" class="select-popup" :style="position" @keydown="keys">
        <input
          ref="input"
          v-model="search"
          type="search"
          role="combobox"
          :aria-label="`Search ${label.toLowerCase()}`"
          :aria-controls="`${id}-list`"
          :aria-expanded="true"
          :aria-activedescendant="visible.length ? `${id}-${active}` : undefined"
          aria-autocomplete="list"
          placeholder="Type to search…"
          @input="active = 0"
        />
        <ul :id="`${id}-list`" role="listbox" :aria-label="label">
          <li
            v-for="(option, index) in visible"
            :id="`${id}-${index}`"
            :key="option.value"
            role="option"
            :aria-selected="String(option.value) === String(modelValue)"
            :class="{ highlighted: index === active }"
            @mouseenter="active = index"
            @mousedown.prevent
            @click="select(option)"
          >
            <span>{{ option.label }}</span
            ><span v-if="String(option.value) === String(modelValue)">✓</span>
          </li>
          <li v-if="!visible.length" class="select-empty" role="presentation">
            No matching options.
          </li>
        </ul>
      </div></Teleport
    >
  </div>
</template>
