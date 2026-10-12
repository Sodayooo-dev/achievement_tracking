export type ThemeKey =
  'inventory' | 'skilltree' | 'worldmap' | 'killfeed' | 'charselect' | 'trophy' | 'questlog'
export function genreToTheme(genre: string): ThemeKey {
  const rules: [RegExp, ThemeKey][] = [
    [/sandbox|survival|craft/i, 'inventory'],
    [/rpg|role/i, 'skilltree'],
    [/platform/i, 'worldmap'],
    [/shoot|fps|tps/i, 'killfeed'],
    [/fight|brawl/i, 'charselect'],
    [/rac|sport|driv/i, 'trophy'],
  ]
  return rules.find(([pattern]) => pattern.test(genre))?.[1] ?? 'questlog'
}
export const themeNames: Record<ThemeKey, string> = {
  inventory: 'Inventory',
  skilltree: 'Skill tree',
  worldmap: 'World map',
  killfeed: 'Combat HUD',
  charselect: 'Fighter select',
  trophy: 'Trophy case',
  questlog: 'Quest log',
}
