import { ref } from 'vue'
export function useAsync(task: () => Promise<unknown>) {
  const loading = ref(false),
    error = ref('')
  let invocation = 0
  async function run() {
    const current = ++invocation
    loading.value = true
    error.value = ''
    try {
      await task()
    } catch (e) {
      if (current === invocation)
        error.value = e instanceof Error ? e.message : 'Something went wrong.'
    } finally {
      if (current === invocation) loading.value = false
    }
  }
  return { loading, error, run }
}
