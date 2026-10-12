import { ref } from 'vue'
import { readSaved, save } from './storage'

export type SoundCue = 'click' | 'select' | 'insert' | 'confirm' | 'error' | 'back'
const files: Record<SoundCue, string> = {
  click: 'click_001.ogg',
  select: 'select_001.ogg',
  insert: 'switch_001.ogg',
  confirm: 'confirmation_001.ogg',
  error: 'error_001.ogg',
  back: 'back_001.ogg',
}
export const soundEnabled = ref(readSaved('ch.sound', true))
const audio = new Map<SoundCue, HTMLAudioElement>()
let interacted = false
let lastSelect = 0

export function playSound(cue: SoundCue) {
  if (!soundEnabled.value || !interacted) return
  if (cue === 'select' && performance.now() - lastSelect < 90) return
  if (cue === 'select') lastSelect = performance.now()
  let clip = audio.get(cue)
  if (!clip) {
    clip = new Audio(`${import.meta.env.BASE_URL}audio/${files[cue]}`)
    clip.volume = cue === 'confirm' ? 0.28 : 0.2
    audio.set(cue, clip)
  }
  clip.currentTime = 0
  void clip.play().catch(() => {
    /* Autoplay restrictions or unavailable audio must never block UI. */
  })
}

export function toggleSound() {
  interacted = true
  soundEnabled.value = !soundEnabled.value
  save('ch.sound', soundEnabled.value)
  if (soundEnabled.value) playSound('click')
  else
    for (const clip of audio.values()) {
      clip.pause()
      clip.currentTime = 0
    }
}

export function installUiSounds() {
  function unlock() {
    interacted = true
  }
  function click(event: MouseEvent) {
    const target =
      event.target instanceof Element ? event.target.closest<HTMLElement>('button, a') : null
    if (!target || target.hasAttribute('disabled') || target.dataset.sound === 'silent') return
    if (target.matches('a[href^="http"]')) return
    const cue = target.dataset.sound as SoundCue | undefined
    playSound(cue && cue in files ? cue : target.matches('[data-cell]') ? 'insert' : 'click')
  }
  function key(event: KeyboardEvent) {
    unlock()
    if (
      ['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key) &&
      event.target instanceof Element &&
      event.target.matches('[data-cell]')
    )
      playSound('select')
  }
  document.addEventListener('pointerdown', unlock, { capture: true })
  document.addEventListener('keydown', key, { capture: true })
  document.addEventListener('click', click)
  return () => {
    document.removeEventListener('pointerdown', unlock, { capture: true })
    document.removeEventListener('keydown', key, { capture: true })
    document.removeEventListener('click', click)
    for (const clip of audio.values()) clip.pause()
  }
}
