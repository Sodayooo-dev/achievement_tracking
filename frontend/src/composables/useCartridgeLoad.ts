import { computed, ref } from 'vue'
import { useAsync } from './useAsync'

export function useCartridgeLoad(fetchProgress: () => Promise<unknown>) {
  const animationDone = ref(false)
  const { loading, error, run } = useAsync(fetchProgress)
  const inserting = computed(() => !animationDone.value || loading.value)
  function loadGame() {
    animationDone.value = false
    return run()
  }
  function animationFinished() {
    animationDone.value = true
  }
  return { loading, error, inserting, loadGame, animationFinished }
}
