export function pixelIcon(name: string) {
  let seed = 2166136261
  for (const c of name) seed = Math.imul(seed ^ c.charCodeAt(0), 16777619) >>> 0
  const cells: { x: number; y: number }[] = []
  for (let y = 0; y < 8; y++)
    for (let x = 0; x < 4; x++) {
      seed ^= seed << 13
      seed ^= seed >>> 17
      seed ^= seed << 5
      if (seed & 1) cells.push({ x, y }, { x: 7 - x, y })
    }
  return cells
}
