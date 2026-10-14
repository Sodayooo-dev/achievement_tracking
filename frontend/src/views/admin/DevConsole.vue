<script setup lang="ts">
import { computed, onUnmounted, reactive, ref, watch } from 'vue'
import { onBeforeRouteLeave, onBeforeRouteUpdate, useRoute } from 'vue-router'
import { useCatalog } from '@/stores/catalog'
import { useSession } from '@/stores/session'
import * as api from '@/api/endpoints'
import { request, ApiError } from '@/api/client'
import type { PlayerAchievement, PlayerGame, Profile } from '@/api/types'
import { readSaved, save } from '@/lib/storage'
import Modal from '@/components/ui/Modal.vue'
import GameSelect from '@/components/ui/GameSelect.vue'
import GameArtwork from '@/components/ui/GameArtwork.vue'
type Row = Record<string, unknown> & { id: number }
type Field = {
  key: string
  label: string
  type?: string
  source?: 'games' | 'achievements' | 'levels' | 'players'
  optional?: boolean
}
const editors: Record<string, { title: string; resource: string; fields: Field[] }> = {
  overview: { title: 'Overview', resource: '', fields: [] },
  games: {
    title: 'Games',
    resource: 'games',
    fields: [
      { key: 'title', label: 'Title' },
      { key: 'publisher', label: 'Publisher' },
      { key: 'genre', label: 'Genre' },
    ],
  },
  achievements: {
    title: 'Achievements',
    resource: 'achievements',
    fields: [
      { key: 'game_id', label: 'Game', source: 'games' },
      { key: 'name', label: 'Name' },
      { key: 'description', label: 'Objective', type: 'textarea' },
      { key: 'exp_value', label: 'XP', type: 'number' },
    ],
  },
  players: {
    title: 'Players',
    resource: 'players',
    fields: [
      { key: 'username', label: 'Username' },
      { key: 'first_name', label: 'First name', optional: true },
      { key: 'last_name', label: 'Last name', optional: true },
      { key: 'email', label: 'Email', type: 'email', optional: true },
      { key: 'level', label: 'Profile starting level', source: 'levels' },
      {
        key: 'password',
        label: 'New password (leave blank to preserve)',
        type: 'password',
        optional: true,
      },
    ],
  },
  grants: {
    title: 'Achievement grants',
    resource: 'player_achievements',
    fields: [
      { key: 'player_id', label: 'Player', source: 'players' },
      { key: 'achievement_id', label: 'Achievement', source: 'achievements' },
      { key: 'acquired_date', label: 'Acquired date', type: 'date' },
    ],
  },
  library: {
    title: 'Player libraries',
    resource: 'player_games',
    fields: [
      { key: 'player_id', label: 'Player', source: 'players' },
      { key: 'game_id', label: 'Game', source: 'games' },
    ],
  },
  levels: {
    title: 'Levels',
    resource: 'levels',
    fields: [
      { key: 'number', label: 'Level number', type: 'number' },
      { key: 'title', label: 'Rank title' },
      { key: 'exp_required', label: 'Required lifetime XP', type: 'number' },
    ],
  },
}
const route = useRoute(),
  catalog = useCatalog(),
  session = useSession()
const key = computed(() => String(route.params.editor ?? 'overview'))
const config = computed(() => editors[key.value] ?? editors.overview!)
const rows = ref<Row[]>([]),
  count = ref(0),
  page = ref(1),
  search = ref(''),
  gameFilter = ref<string | number>('')
const loading = ref(false),
  busy = ref(false),
  message = ref(''),
  error = ref(''),
  fieldErrors = ref<Record<string, unknown>>({})
const editing = ref(false),
  editId = ref<number | null>(null),
  form = reactive<Record<string, string | number>>({}),
  baseline = ref('')
const deleting = ref<Row | null>(null),
  dependencies = ref<Record<string, number>>({})
const confirmAction = ref<null | (() => void)>(null)
const imageFile = ref<File | null>(null),
  imagePreview = ref(''),
  removeImage = ref(false),
  fileInput = ref<HTMLInputElement>()
const players = ref<Profile[]>([]),
  playerSearch = ref(''),
  playerLibrary = ref<PlayerGame[]>([]),
  playerUnlocks = ref<PlayerAchievement[]>([]),
  grantGame = ref<string | number>('')
const totals = ref({ players: 0, libraries: 0, grants: 0 })
const recentGrants = ref<PlayerAchievement[]>([])
const userId = session.profile?.id
let objectUrl = '',
  sequence = 0,
  searchTimer: ReturnType<typeof setTimeout>,
  playerTimer: ReturnType<typeof setTimeout>,
  ownerSequence = 0,
  playerSequence = 0,
  hydrating = false
const draftKey = computed(() => `ch.draft.${userId}.${key.value}`)
const draft = ref<null | { id: number | null; form: Record<string, string | number> }>(null)
const dirty = computed(
  () =>
    editing.value &&
    (JSON.stringify(form) !== baseline.value || Boolean(imageFile.value) || removeImage.value),
)
function discardImage() {
  if (objectUrl) URL.revokeObjectURL(objectUrl)
  objectUrl = ''
  imageFile.value = null
  imagePreview.value = ''
  if (fileInput.value) fileInput.value.value = ''
}
function close(force = false) {
  if (dirty.value && !force) {
    confirmAction.value = () => close(true)
    return
  }
  editing.value = false
  discardImage()
  save(draftKey.value, null)
  draft.value = null
}
function fieldError(name: string) {
  const value = fieldErrors.value[name]
  return Array.isArray(value) ? value.join(' ') : String(value ?? '')
}
function filtersKey() {
  return `ch.adminFilters.${userId}.${key.value}`
}
async function load() {
  const ticket = ++sequence
  loading.value = true
  error.value = ''
  try {
    await catalog.load()
    if (key.value === 'overview') {
      const [p, l, g] = await Promise.all([
        api.getPage<Profile>('players', { page_size: 1 }),
        api.getPage<PlayerGame>('player_games', { page_size: 1 }),
        api.getPage<PlayerAchievement>('player_achievements', {
          page_size: 5,
          ordering: '-acquired_date',
        }),
      ])
      if (ticket !== sequence) return
      totals.value = { players: p.count, libraries: l.count, grants: g.count }
      recentGrants.value = g.results
      rows.value = []
      count.value = 0
    } else {
      const query: Record<string, string | number> = {
        page: page.value,
        page_size: 20,
        search: search.value,
      }
      if (gameFilter.value && ['achievements', 'library'].includes(key.value))
        query.game_id = gameFilter.value
      const result = await api.getPage<Row>(config.value.resource, query)
      if (ticket !== sequence) return
      rows.value = result.results
      count.value = result.count
    }
  } catch (e) {
    if (ticket === sequence)
      error.value = e instanceof Error ? e.message : 'Could not load records.'
  } finally {
    if (ticket === sequence) loading.value = false
  }
}
async function findPlayers() {
  const ticket = ++playerSequence
  try {
    const result = await api.getPage<Profile>('players', {
      search: playerSearch.value,
      page_size: 100,
    })
    if (ticket === playerSequence) players.value = result.results
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not find players.'
  }
}
watch(playerSearch, () => {
  clearTimeout(playerTimer)
  playerTimer = setTimeout(() => void findPlayers(), 250)
})
watch([search, gameFilter], () => {
  page.value = 1
  save(filtersKey(), { search: search.value, game: gameFilter.value })
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => void load(), 200)
})
watch(page, () => void load())
watch(
  [key, () => route.query.game],
  () => {
    sequence++
    editing.value = false
    discardImage()
    message.value = ''
    page.value = 1
    const filters = readSaved<{ search: string; game: string | number }>(filtersKey(), {
      search: '',
      game: '',
    })
    search.value = filters.search
    gameFilter.value = String(route.query.game ?? filters.game)
    draft.value = readSaved(draftKey.value, null)
    void load()
  },
  { immediate: true },
)
watch(
  form,
  () => {
    if (editing.value && dirty.value && !busy.value) {
      const safe = { ...form }
      delete safe.password
      save(draftKey.value, { id: editId.value, form: safe })
    }
  },
  { deep: true },
)
function safeLeave() {
  if (busy.value) return false
  if (!dirty.value) return true
  return new Promise<boolean>((resolve) => {
    confirmAction.value = () => {
      close(true)
      resolve(true)
    }
    cancelLeave = () => resolve(false)
  })
}
let cancelLeave: (() => void) | null = null
function cancelConfirmation() {
  confirmAction.value = null
  cancelLeave?.()
  cancelLeave = null
}
function confirmDiscard() {
  const action = confirmAction.value
  confirmAction.value = null
  cancelLeave = null
  action?.()
}
function askDelete(row: Row) {
  deleting.value = row
  dependencies.value = {}
  error.value = ''
}
onBeforeRouteLeave(safeLeave)
onBeforeRouteUpdate(safeLeave)
function unload(e: BeforeUnloadEvent) {
  if (dirty.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}
window.addEventListener('beforeunload', unload)
onUnmounted(() => {
  discardImage()
  clearTimeout(searchTimer)
  clearTimeout(playerTimer)
  window.removeEventListener('beforeunload', unload)
})
async function open(row?: Row, duplicate = false) {
  hydrating = true
  discardImage()
  removeImage.value = false
  fieldErrors.value = {}
  error.value = ''
  editId.value = duplicate ? null : (row?.id ?? null)
  Object.keys(form).forEach((name) => delete form[name])
  for (const f of config.value.fields)
    form[f.key] = row && f.type !== 'password' ? String(row[f.key] ?? '') : ''
  if (!row && gameFilter.value && key.value === 'achievements') form.game_id = gameFilter.value
  if (duplicate) form.name = String(form.name).slice(0, 88) + ' (copy)'
  if (key.value === 'grants' && !row) {
    const d = new Date()
    form.acquired_date = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }
  imagePreview.value = String(row?.image_url ?? '')
  grantGame.value = ''
  baseline.value = JSON.stringify(form)
  editing.value = true
  if (['grants', 'library', 'players'].includes(key.value)) {
    await findPlayers()
    if (form.player_id) await ownerChanged()
    if (key.value === 'players' && row) {
      form.player_id = row.id
      await ownerChanged()
      delete form.player_id
      baseline.value = JSON.stringify(form)
    }
  }
  hydrating = false
}
async function restore() {
  const savedDraft = draft.value
  if (!savedDraft) return
  await open()
  editId.value = savedDraft.id
  Object.assign(form, savedDraft.form)
  if (key.value === 'games' && editId.value)
    imagePreview.value = catalog.games.find((g) => g.id === editId.value)?.image_url ?? ''
  if (form.player_id) await ownerChanged()
}
async function ownerChanged() {
  const id = Number(form.player_id),
    ticket = ++ownerSequence
  playerLibrary.value = []
  playerUnlocks.value = []
  if (!id) return
  try {
    const [library, unlocks] = await Promise.all([
      request<PlayerGame[]>(`player_games/?player_id=${id}`),
      request<PlayerAchievement[]>(`player_achievements/?player_id=${id}`),
    ])
    if (ticket !== ownerSequence) return
    playerLibrary.value = library
    playerUnlocks.value = unlocks
    if (key.value === 'grants' && form.achievement_id) {
      const a = catalog.achievements.find((a) => a.id === Number(form.achievement_id))
      grantGame.value = a?.game_id ?? ''
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load player progress.'
  }
}
watch(
  () => form.player_id,
  () => {
    if (!hydrating && editing.value && ['grants', 'library'].includes(key.value)) {
      form.achievement_id = ''
      grantGame.value = ''
      void ownerChanged()
    }
  },
)
const ownedGames = computed(() =>
  catalog.games.filter((g) => playerLibrary.value.some((l) => l.game_id === g.id)),
)
function options(source: string) {
  if (source === 'players')
    return players.value.map((p) => ({ value: p.id, label: `${p.username} · #${p.id}` }))
  if (source === 'games') return catalog.games.map((g) => ({ value: g.id, label: g.title }))
  if (source === 'levels')
    return catalog.levelsSorted.map((l) => ({
      value: l.id,
      label: `LV ${l.number} · ${l.title} · ${l.exp_required.toLocaleString()} XP`,
    }))
  return catalog.achievements
    .filter(
      (a) =>
        a.game_id === Number(grantGame.value) &&
        (a.id === Number(form.achievement_id) ||
          !playerUnlocks.value.some((u) => u.achievement_id === a.id)),
    )
    .map((a) => ({ value: a.id, label: `${a.name} · ${a.exp_value} XP` }))
}
function selectImage(event: Event) {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  discardImage()
  if (
    !['image/png', 'image/jpeg', 'image/webp'].includes(file.type) ||
    file.size > 5 * 1024 * 1024
  ) {
    fieldErrors.value.image = ['Choose a PNG, JPG or WebP up to 5 MB.']
    return
  }
  imageFile.value = file
  objectUrl = URL.createObjectURL(file)
  imagePreview.value = objectUrl
  removeImage.value = false
  delete fieldErrors.value.image
}
async function submit() {
  fieldErrors.value = {}
  error.value = ''
  for (const f of config.value.fields)
    if (!f.optional && (form[f.key] === '' || form[f.key] === undefined))
      fieldErrors.value[f.key] = ['This field is required.']
  if (Object.keys(fieldErrors.value).length) return
  busy.value = true
  try {
    const data: Record<string, string | number | boolean> = {}
    for (const f of config.value.fields) {
      if (f.type === 'password' && !form[f.key]) continue
      data[f.key] = f.source || f.type === 'number' ? Number(form[f.key]) : (form[f.key] ?? '')
    }
    if (key.value === 'games') data.remove_image = removeImage.value
    let payload: unknown = data
    if (imageFile.value) {
      const multipart = new FormData()
      for (const [name, value] of Object.entries(data)) multipart.append(name, String(value))
      multipart.append('image', imageFile.value)
      payload = multipart
    }
    const resource = key.value === 'players' ? '' : config.value.resource
    if (editId.value) await api.updateRecord(resource, editId.value, payload)
    else await api.createRecord(resource, payload)
    if (key.value === 'players' && editId.value === session.profile?.id) await session.loadProfile()
    close(true)
    await catalog.load(true)
    await load()
    message.value = 'Saved. Your changes are live.'
  } catch (e) {
    if (e instanceof ApiError) {
      fieldErrors.value = e.fields
      error.value = e.message
    } else error.value = e instanceof Error ? e.message : 'Save failed.'
  } finally {
    busy.value = false
  }
}
async function remove() {
  if (!deleting.value) return
  busy.value = true
  dependencies.value = {}
  try {
    await api.deleteRecord(key.value === 'players' ? '' : config.value.resource, deleting.value.id)
    deleting.value = null
    await catalog.load(true)
    await load()
    message.value = 'Record deleted.'
  } catch (e) {
    if (e instanceof ApiError) {
      dependencies.value = (e.fields.dependencies as Record<string, number>) ?? {}
      error.value = e.message
    } else error.value = e instanceof Error ? e.message : 'Deletion failed.'
  } finally {
    busy.value = false
  }
}
function rowName(row: Row) {
  if (row.username) return String(row.username)
  if (row.title || row.name) return String(row.title ?? row.name)
  if (row.achievement_id)
    return (
      catalog.achievements.find((a) => a.id === row.achievement_id)?.name ??
      `Achievement #${row.achievement_id}`
    )
  return catalog.games.find((g) => g.id === row.game_id)?.title ?? `Record #${row.id}`
}
function related(row: Row) {
  if (row.player_id)
    return `Player #${row.player_id}${row.acquired_date ? ' · ' + row.acquired_date : ''}`
  if (row.exp_value !== undefined)
    return `${row.exp_value} XP · ${catalog.games.find((g) => g.id === row.game_id)?.title ?? ''}`
  if (row.publisher) return String(row.publisher) + ' · ' + String(row.genre)
  if (row.exp_required !== undefined)
    return `LV ${row.number} · ${Number(row.exp_required).toLocaleString()} XP`
  return String(row.email ?? '')
}
const emptyGames = computed(() =>
  catalog.games.filter((g) => !catalog.achievements.some((a) => a.game_id === g.id)),
)
const missingArtwork = computed(() => catalog.games.filter((g) => !g.image_url))
const metadataFlags = computed(() =>
  catalog.games.filter(
    (g) =>
      g.title.toLowerCase().includes('mobile legends') &&
      (g.publisher === 'Mojang' || g.genre === 'Sandbox'),
  ),
)
const previewXp = computed(() =>
  playerUnlocks.value.reduce(
    (sum, u) => sum + (catalog.achievements.find((a) => a.id === u.achievement_id)?.exp_value ?? 0),
    0,
  ),
)
</script>
<template>
  <section class="page-content">
    <div class="page-heading">
      <div>
        <p class="eyebrow">CONTROL ROOM / ADMINISTRATOR</p>
        <h1>Admin console<span class="red">.</span></h1>
        <p>Manage the catalog. Look after the players.</p>
      </div>
      <span class="admin-stamp">ADMIN ONLY</span>
    </div>
    <div class="dev-layout">
      <nav class="dev-tools" aria-label="Admin workspaces">
        <RouterLink
          v-for="(editor, name) in editors"
          :key="name"
          :to="`/dev/${name}`"
          :class="{ selected: key === name }"
          ><span>▸</span>{{ editor.title }}</RouterLink
        >
      </nav>
      <div class="dev-workspace">
        <p v-if="message" class="success-message" role="status">{{ message }}</p>
        <p v-if="error" class="field-error" role="alert">{{ error }}</p>
        <template v-if="key === 'overview'">
          <div class="admin-summary">
            <div>
              <strong>{{ catalog.games.length }}</strong
              ><small>Games</small>
            </div>
            <div>
              <strong>{{ catalog.achievements.length }}</strong
              ><small>Achievements</small>
            </div>
            <div>
              <strong>{{ totals.players }}</strong
              ><small>Players</small>
            </div>
            <div>
              <strong>{{ totals.grants }}</strong
              ><small>Granted achievements</small>
            </div>
          </div>
          <h2>Catalog health</h2>
          <div class="admin-health">
            <p v-if="!emptyGames.length && !missingArtwork.length && !metadataFlags.length">
              All games have artwork and objectives.
            </p>
            <p v-for="game in emptyGames" :key="'empty' + game.id">
              {{ game.title }} has no objectives.
              <RouterLink :to="`/dev/achievements?game=${game.id}`">Add achievements →</RouterLink>
            </p>
            <p v-for="game in missingArtwork" :key="'art' + game.id">
              {{ game.title }} needs artwork.
            </p>
            <p v-for="game in metadataFlags" :key="'meta' + game.id">
              Review {{ game.title }}: publisher/genre appears inconsistent. Existing metadata is
              preserved.
            </p>
          </div>
          <h2>Recent grants</h2>
          <div class="admin-health">
            <p v-for="grant in recentGrants" :key="grant.id">
              {{ grant.acquired_date }} · Player #{{ grant.player_id }} ·
              {{ catalog.achievements.find((a) => a.id === grant.achievement_id)?.name }}
            </p>
            <p v-if="!recentGrants.length">No achievements granted yet.</p>
          </div>
          <p class="results-count">
            {{ totals.libraries }} library assignments · Unlocks remain admin-verified.
          </p>
        </template>
        <template v-else>
          <div class="admin-list-toolbar">
            <h2>
              {{ config.title }} <span>({{ count }})</span>
            </h2>
            <button v-if="key !== 'players'" class="primary" @click="open()">
              + New
              {{
                config.title === 'Achievements'
                  ? 'achievement'
                  : key === 'games'
                    ? 'game'
                    : 'record'
              }}</button
            ><button v-if="draft" @click="restore">Restore draft</button>
          </div>
          <div class="filters">
            <label
              >Search<input
                v-model="search"
                type="search"
                :placeholder="`Search ${config.title.toLowerCase()}…`" /></label
            ><label v-if="['achievements', 'library'].includes(key)"
              >Game<GameSelect
                v-model="gameFilter"
                label="Filter records by game"
                :options="[{ value: '', label: 'All games' }, ...options('games')]"
            /></label>
          </div>
          <p v-if="loading" role="status">Reading records…</p>
          <button v-if="error && !editing" @click="load">Retry</button>
          <div class="record-list" :aria-busy="loading">
            <article v-for="row in rows" :key="row.id">
              <GameArtwork
                v-if="key === 'games'"
                class="record-thumbnail"
                :title="rowName(row)"
                :url="String(row.image_url ?? '')"
              />
              <div>
                <small>#{{ row.id }}</small>
                <h3>{{ rowName(row) }}</h3>
                <p>{{ related(row) }}</p>
                <p v-if="key === 'achievements'">{{ String(row.description).slice(0, 150) }}</p>
              </div>
              <div class="record-actions">
                <button @click="open(row)">Edit</button
                ><button v-if="key === 'achievements'" @click="open(row, true)">Duplicate</button
                ><RouterLink
                  v-if="key === 'games'"
                  class="button"
                  :to="`/dev/achievements?game=${row.id}`"
                  >Objectives</RouterLink
                ><button
                  class="danger"
                  :disabled="busy || (key === 'players' && row.id === session.profile?.id)"
                  @click="askDelete(row)"
                >
                  Delete…
                </button>
              </div>
            </article>
            <p v-if="!loading && !rows.length" class="inspect-hint">No matching records.</p>
          </div>
          <div class="admin-pagination">
            <button :disabled="page <= 1 || loading" @click="page--">← Previous</button
            ><span>Page {{ page }} / {{ Math.max(1, Math.ceil(count / 20)) }}</span
            ><button :disabled="page * 20 >= count || loading" @click="page++">Next →</button>
          </div>
        </template>
      </div>
    </div>
    <Modal
      v-if="editing"
      :title="
        editId
          ? `Edit ${config.title.toLowerCase()} · #${editId}`
          : `New ${config.title.toLowerCase()}`
      "
      @close="!busy && close()"
    >
      <div class="admin-editor">
        <p v-if="error" class="field-error" role="alert">{{ error }}</p>
        <div v-if="key === 'players'" class="player-overview">
          <h3>Player progress</h3>
          <p>
            {{ playerLibrary.length }} games · {{ playerUnlocks.length }} unlocks ·
            {{ previewXp.toLocaleString() }} lifetime XP
          </p>
          <p>Library: {{ ownedGames.map((g) => g.title).join(', ') || 'Empty' }}</p>
          <p
            v-for="unlock in [...playerUnlocks]
              .sort((a, b) => b.acquired_date.localeCompare(a.acquired_date))
              .slice(0, 5)"
            :key="unlock.id"
          >
            {{ unlock.acquired_date }} ·
            {{ catalog.achievements.find((a) => a.id === unlock.achievement_id)?.name }}
          </p>
        </div>
        <form class="editor-form" @submit.prevent="submit">
          <label v-if="['grants', 'library'].includes(key)" class="game-upload"
            >Find a player<input
              v-model="playerSearch"
              type="search"
              placeholder="Search username or email…"
          /></label>
          <template v-for="field in config.fields" :key="field.key">
            <label
              >{{ field.label
              }}<GameSelect
                v-if="field.source"
                v-model="form[field.key]!"
                :label="field.label"
                :options="options(field.source)"
                :disabled="busy || (field.source === 'achievements' && !grantGame)"
              /><textarea
                v-else-if="field.type === 'textarea'"
                v-model="form[field.key]"
                :required="!field.optional"
                :disabled="busy"
              /><input
                v-else
                v-model="form[field.key]"
                :type="field.type ?? 'text'"
                :required="!field.optional"
                :min="field.key === 'number' ? 1 : 0"
                :step="field.type === 'number' ? 1 : undefined"
                :disabled="busy"
                :autocomplete="field.type === 'password' ? 'new-password' : 'off'"
                :aria-invalid="Boolean(fieldErrors[field.key])"
              /><small v-if="fieldErrors[field.key]" class="field-error">{{
                fieldError(field.key)
              }}</small></label
            >
            <label v-if="key === 'grants' && field.key === 'player_id'"
              >Game in this player's library<GameSelect
                v-model="grantGame"
                label="Grant game"
                :options="ownedGames.map((g) => ({ value: g.id, label: g.title }))"
                :disabled="!form.player_id || busy"
                @update:model-value="form.achievement_id = ''"
              /><small v-if="form.player_id && !ownedGames.length"
                >Add a game in Player libraries first.</small
              ></label
            >
          </template>
          <template v-if="key === 'games'"
            ><label class="game-upload"
              >Game artwork<input
                ref="fileInput"
                type="file"
                accept="image/png,image/jpeg,image/webp"
                :disabled="busy"
                @change="selectImage"
              /><small>PNG, JPG or WebP · Up to 5 MB / 16 megapixels · Stored locally</small
              ><small v-if="fieldErrors.image" class="field-error">{{
                fieldError('image')
              }}</small></label
            >
            <div v-if="imagePreview && !removeImage" class="game-image-preview">
              <GameArtwork :title="String(form.title || 'Artwork preview')" :url="imagePreview" />
            </div>
            <label v-if="editId" class="game-upload"
              ><input v-model="removeImage" type="checkbox" :disabled="busy" /> Remove current
              artwork</label
            ></template
          >
          <p v-if="key === 'levels'" class="game-upload results-count">
            Ranks use lifetime XP. Thresholds must increase with level number. Players below the
            first threshold remain Unranked.
          </p>
          <p v-if="key === 'grants'" class="game-upload results-count">
            Already unlocked achievements are excluded. A game must be in the selected player's
            library.
          </p>
          <small v-if="fieldErrors.non_field_errors" class="field-error">{{
            fieldError('non_field_errors')
          }}</small>
          <div class="editor-actions">
            <button class="primary" :disabled="busy">
              {{ busy ? 'Saving…' : 'Save changes →' }}</button
            ><button type="button" :disabled="busy" @click="close()">Cancel</button>
          </div>
        </form>
      </div></Modal
    >
    <Modal
      v-if="deleting"
      :title="`Delete ${rowName(deleting)}?`"
      @close="!busy && (deleting = null)"
      ><p>
        This permanently removes the record. Existing references will block deletion to preserve
        progress.
      </p>
      <p v-if="error" class="field-error" role="alert">{{ error }}</p>
      <ul v-if="Object.keys(dependencies).length">
        <li v-for="(n, label) in dependencies" :key="label">{{ n }} {{ label }}</li>
      </ul>
      <div class="modal-actions">
        <button :disabled="busy" @click="deleting = null">Keep it</button
        ><button
          class="danger"
          :disabled="busy || Object.keys(dependencies).length > 0"
          @click="remove"
        >
          {{ busy ? 'Deleting…' : 'Delete permanently' }}
        </button>
      </div></Modal
    >
    <Modal v-if="confirmAction" title="Discard unsaved changes?" @close="cancelConfirmation"
      ><p>Your current edits have not been saved.</p>
      <div class="modal-actions">
        <button @click="cancelConfirmation">Keep editing</button
        ><button class="danger" @click="confirmDiscard">Discard changes</button>
      </div></Modal
    >
  </section>
</template>
