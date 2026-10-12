<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
defineProps<{ title: string }>()
const emit = defineEmits<{ close: [] }>()
const dialog = ref<HTMLElement>()
const previous = document.activeElement as HTMLElement | null
function keys(e: KeyboardEvent) {
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
  document.addEventListener('keydown', keys)
})
onUnmounted(() => {
  document.removeEventListener('keydown', keys)
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
        aria-labelledby="modal-title"
      >
        <button class="modal-close" aria-label="Close dialog" @click="emit('close')">×</button>
        <h2 id="modal-title">{{ title }}</h2>
        <slot />
      </section></div
  ></Teleport>
</template>
