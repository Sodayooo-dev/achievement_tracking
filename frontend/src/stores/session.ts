import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Profile } from '@/api/types'
import * as api from '@/api/endpoints'
import { readSaved, save } from '@/lib/storage'
import { setAccessToken } from '@/api/client'
export const useSession = defineStore('session', () => {
  const access = ref(readSaved<string>('ch.access', ''))
  const profile = ref(readSaved<Profile | null>('ch.profile', null))
  setAccessToken(access.value, readSaved<string>('ch.refresh', ''))
  function adoptAccess(value: string) {
    access.value = value
  }
  async function loadProfile() {
    const id = profile.value?.id
    const result = await api.getMe()
    if (profile.value?.id !== id) return
    profile.value = result
    save('ch.profile', profile.value)
  }
  const isLoggedIn = computed(() => Boolean(access.value && profile.value?.id))
  const isAdmin = computed(
    () => profile.value?.role === Number(import.meta.env.VITE_ADMIN_ROLE_ID ?? 1),
  )
  async function login(username: string, password: string) {
    const result = await api.login(username, password)
    access.value = result.tokens.access
    setAccessToken(access.value, result.tokens.refresh)
    save('ch.refresh', result.tokens.refresh)
    profile.value = result.profile
    save('ch.access', access.value)
    save('ch.profile', profile.value)
  }
  async function register(form: Record<string, string>) {
    await api.register({
      ...form,
    })
    try {
      await login(form.username!, form.password!)
    } catch {
      throw new Error('Your account was created, but sign-in failed. Use Continue to sign in.')
    }
  }
  function logout() {
    access.value = ''
    setAccessToken('')
    profile.value = null
    save('ch.access', '')
    save('ch.profile', null)
    save('ch.refresh', '')
  }
  return {
    access,
    profile,
    isLoggedIn,
    isAdmin,
    login,
    register,
    logout,
    expire: logout,
    adoptAccess,
    loadProfile,
  }
})
