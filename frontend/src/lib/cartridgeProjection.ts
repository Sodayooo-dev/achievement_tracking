// One projection and one shared mouth boundary for every rendered cartridge section.
export const frontloader = {
  slot: { left: 180, right: 400, top: 176, bottom: 194 },
  seam: 185,
  thickness: 8,
  top: [
    [200, 244],
    [380, 244],
    [395, 344],
    [185, 344],
  ],
  duration: 2350,
} as const

export function cartridgePose(elapsed: number) {
  const time = Math.max(0, elapsed)
  const travel = Math.max(0, Math.min(1, (time - 450) / 1250))
  const eased = travel * travel * (3 - 2 * travel)
  return {
    y: -180 * eased,
    opacity: Math.min(1, time / 160),
    progress: Math.min(1, time / frontloader.duration),
    phase:
      time < 450
        ? 'ALIGNING CARTRIDGE'
        : time < 1700
          ? 'INSERTING CARTRIDGE'
          : time < 1900
            ? 'CARTRIDGE LOCKED'
            : 'READING SAVE DATA',
  }
}
