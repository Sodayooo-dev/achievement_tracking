<script lang="ts">
let openDialogs = 0
</script>
<script setup lang="ts">
import { onMounted, onUnmounted, ref, useId } from 'vue'
defineProps<{ title: string }>()
const emit = defineEmits<{ close: [] }>()
const dialog = ref<HTMLElement>()
const titleId = `modal-title-${useId()}`
const previous = document.activeElement as HTMLElement | null
function keys(e: KeyboardEvent) {
  if (!dialog.value?.contains(document.activeElement)) return
  if (e.key === 'Escape') emit('close')
  if (e.key !== 'Tab') return
  const controls = Array.from(
    dialog.value?.querySelectorAll<HTMLElement>(
      'button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex="0"]',
    ) ?? [],
  )
  if (e.shiftKey && document.activeElement === controls[0]) {
    e.preventDefault()
    controls.at(-1)?.focus()
  } else if (!e.shiftKey && document.activeElement === controls.at(-1)) {
    e.preventDefault()
    controls[0]?.focus()
  }
}
onMounted(() => {
  dialog.value?.querySelector<HTMLElement>('button')?.focus()
  openDialogs++
  document.getElementById('app')?.setAttribute('inert', '')
  document.addEventListener('keydown', keys)
})
onUnmounted(() => {
  document.removeEventListener('keydown', keys)
  openDialogs--
  if (!openDialogs) document.getElementById('app')?.removeAttribute('inert')
  previous?.focus()
})
</script>
<template>
  <Teleport to="body"
    ><div class="modal-backdrop" @click.self="emit('close')">
      <section
        ref="dialog"
        class="modal"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
      >
        <button class="modal-close" aria-label="Close dialog" @click="emit('close')">×</button>
        <h2 :id="titleId">{{ title }}</h2>
        <slot />
      </section></div
  ></Teleport>
</template>
