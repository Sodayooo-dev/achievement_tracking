import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import type { Profile } from '@/api/types'
import * as api from '@/api/endpoints'
import { readSaved, save } from '@/lib/storage'
import { setAccessToken } from '@/api/client'
export const useSession = defineStore('session', () => {
  const access = ref(readSaved<string>('ch.access', ''))
  const profile = ref(readSaved<Profile | null>('ch.profile', null))
  setAccessToken(access.value)
  const isLoggedIn = computed(() => Boolean(access.value && profile.value?.id))
  const isAdmin = computed(
    () => profile.value?.role === Number(import.meta.env.VITE_ADMIN_ROLE_ID ?? 1),
  )
  async function login(username: string, password: string) {
    const result = await api.login(username, password)
    access.value = result.tokens.access
    setAccessToken(access.value)
    profile.value = result.profile
    save('ch.access', access.value)
    save('ch.profile', profile.value)
  }
  async function register(form: Record<string, string>) {
    await api.register({
      ...form,
      role: Number(import.meta.env.VITE_DEFAULT_ROLE_ID ?? 2),
      level: Number(import.meta.env.VITE_DEFAULT_LEVEL_ID ?? 1),
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
  }
})
