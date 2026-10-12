import { onMounted, onUnmounted, ref } from 'vue'
export function useReducedMotion() {
  const query = window.matchMedia('(prefers-reduced-motion: reduce)'),
    reduced = ref(query.matches)
  function change() {
    reduced.value = query.matches
  }
  onMounted(() => query.addEventListener('change', change))
  onUnmounted(() => query.removeEventListener('change', change))
  return reduced
}
