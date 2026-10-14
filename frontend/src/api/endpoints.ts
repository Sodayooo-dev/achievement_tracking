import { request } from './client'
import type {
  Achievement,
  Game,
  Level,
  LoginResponse,
  PlayerAchievement,
  PlayerGame,
  Profile,
} from './types'
export const login = (username: string, password: string) =>
  request<LoginResponse>('login/', 'POST', { username, password }, true)
export const register = (body: unknown) => request('register/', 'POST', body, true)
export const getGames = () => request<Game[]>('games/')
export const getAchievements = () => request<Achievement[]>('achievements/')
export const getGameAchievements = (id: number) =>
  request<Achievement[]>(`achievements/?game_id=${id}`)
export const getMe = () => request<Profile>('me/')
export const addToLibrary = (gameId: number) =>
  request<PlayerGame>('me/library/', 'POST', { game_id: gameId })
export interface Page<T> {
  count: number
  next: number | null
  previous: number | null
  results: T[]
}
export const getPage = <T>(resource: string, query: Record<string, string | number> = {}) =>
  request<Page<T>>(
    `${resource}/?${new URLSearchParams(Object.entries({ page: 1, ...query }).map(([k, v]) => [k, String(v)]))}`,
  )
export const getPlayer = (id: number) => request<Profile>(`players/${id}/`)
export const getLevels = () => request<Level[]>('levels/')
export const getLibrary = () => request<PlayerGame[]>('player_games/')
export const getUnlocks = () => request<PlayerAchievement[]>('player_achievements/')
export const createRecord = (resource: string, body: unknown) =>
  request(`${resource}/new/`, 'POST', body)
export const updateRecord = (resource: string, id: number, body: unknown) =>
  request(`${resource ? resource + '/' : ''}${id}/update/`, 'PUT', body)
export const deleteRecord = (resource: string, id: number) =>
  request(`${resource ? resource + '/' : ''}${id}/delete/`, 'DELETE')
