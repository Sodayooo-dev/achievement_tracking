import { request } from './client'
import type {
  Achievement,
  Game,
  Level,
  LoginResponse,
  PlayerAchievement,
  PlayerGame,
} from './types'
export const login = (username: string, password: string) =>
  request<LoginResponse>('login/', 'POST', { username, password }, true)
export const register = (body: unknown) => request('register/', 'POST', body, true)
export const getGames = () => request<Game[]>('games/')
export const getAchievements = () => request<Achievement[]>('achievements/')
export const getLevels = () => request<Level[]>('levels/')
export const getLibrary = () => request<PlayerGame[]>('player_games/')
export const getUnlocks = () => request<PlayerAchievement[]>('player_achievements/')
export const createRecord = (resource: string, body: unknown) =>
  request(`${resource}/new/`, 'POST', body)
export const updateRecord = (resource: string, id: number, body: unknown) =>
  request(`${resource ? resource + '/' : ''}${id}/update/`, 'PUT', body)
export const deleteRecord = (resource: string, id: number) =>
  request(`${resource ? resource + '/' : ''}${id}/delete/`, 'DELETE')
