export function gridKeys(event: KeyboardEvent, columns: number) {
  const container = event.currentTarget as HTMLElement
  const cells = Array.from(container.querySelectorAll<HTMLElement>('[data-cell]'))
  const index = cells.indexOf(document.activeElement as HTMLElement)
  if (index < 0) return
  const moves: Record<string, number> = {
    ArrowRight: index + 1,
    ArrowLeft: index - 1,
    ArrowDown: index + columns,
    ArrowUp: index - columns,
    Home: 0,
    End: cells.length - 1,
  }
  const next = moves[event.key]
  if (next === undefined) return
  event.preventDefault()
  cells.forEach(
    (cell, i) => (cell.tabIndex = i === Math.max(0, Math.min(cells.length - 1, next)) ? 0 : -1),
  )
  cells[Math.max(0, Math.min(cells.length - 1, next))]?.focus()
}
