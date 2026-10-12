export interface Level {
  id: number
  number: number
  exp_required: number
  title: string
}
export interface Game {
  id: number
  title: string
  publisher: string
  genre: string
}
export interface Achievement {
  id: number
  game_id: number
  name: string
  description: string
  exp_value: number
}
export interface PlayerGame {
  id: number
  player_id: number
  game_id: number
}
export interface PlayerAchievement {
  id: number
  player_id: number
  achievement_id: number
  acquired_date: string
}
export interface Profile {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: number
  level: number
}
export interface LoginResponse {
  profile: Profile
  tokens: { access: string; refresh: string }
}
export interface ThemeItem extends Achievement {
  unlocked: boolean
  acquired_date?: string
}
