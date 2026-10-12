import type { Level } from '@/api/types'
export function progression(levels: Level[], xp: number) {
  const sorted = [...levels].sort((a, b) => a.exp_required - b.exp_required)
  const current = sorted.filter((l) => l.exp_required <= xp).at(-1) ?? null
  const next = sorted.find((l) => l.exp_required > xp) ?? null
  const intoLevel = Math.max(0, xp - (current?.exp_required ?? 0))
  const needed = next ? next.exp_required - (current?.exp_required ?? 0) : 0
  return {
    current,
    next,
    intoLevel,
    needed,
    pct: needed ? Math.min(100, (intoLevel / needed) * 100) : current ? 100 : 0,
  }
}
