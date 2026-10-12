<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useCatalog } from '@/stores/catalog'
import { usePlayer } from '@/stores/player'
import { useSession } from '@/stores/session'
import { useAsync } from '@/composables/useAsync'
import * as api from '@/api/endpoints'
import { ApiError } from '@/api/client'
import type { PlayerAchievement, PlayerGame, Profile } from '@/api/types'
import Modal from '@/components/ui/Modal.vue'
import LoadState from '@/components/ui/LoadState.vue'
type Row = Record<string, unknown> & { id: number }
type Field = {
  key: string
  label: string
  type?: string
  source?: 'games' | 'achievements' | 'levels'
}
const editors: Record<string, { title: string; resource: string; fields: Field[] }> = {
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
      { key: 'game_id', label: 'Game', type: 'number', source: 'games' },
      { key: 'name', label: 'Name' },
      { key: 'description', label: 'Description', type: 'textarea' },
      { key: 'exp_value', label: 'XP value', type: 'number' },
    ],
  },
  levels: {
    title: 'Levels',
    resource: 'levels',
    fields: [
      { key: 'number', label: 'Level number', type: 'number' },
      { key: 'exp_required', label: 'Required XP', type: 'number' },
      { key: 'title', label: 'Title' },
    ],
  },
  grants: {
    title: 'Achievement grants',
    resource: 'player_achievements',
    fields: [
      { key: 'player_id', label: 'Player ID', type: 'number' },
      {
        key: 'achievement_id',
        label: 'Achievement',
        type: 'number',
        source: 'achievements',
      },
      { key: 'acquired_date', label: 'Acquired date', type: 'date' },
    ],
  },
  library: {
    title: 'Player libraries',
    resource: 'player_games',
    fields: [
      { key: 'player_id', label: 'Player ID', type: 'number' },
      { key: 'game_id', label: 'Game', type: 'number', source: 'games' },
    ],
  },
  players: {
    title: 'Player profiles',
    resource: '',
    fields: [
      { key: 'username', label: 'Username' },
      { key: 'first_name', label: 'First name' },
      { key: 'last_name', label: 'Last name' },
      { key: 'email', label: 'Email', type: 'email' },
      {
        key: 'level',
        label: 'Starting level',
        type: 'number',
        source: 'levels',
      },
      {
        key: 'password',
        label: 'Password (leave blank to preserve)',
        type: 'password',
      },
    ],
  },
}
const route = useRoute(),
  catalog = useCatalog(),
  player = usePlayer(),
  session = useSession()
const key = computed(() => String(route.params.editor ?? 'games'))
const config = computed(() => editors[key.value] ?? editors.games!)
const allLibrary = ref<PlayerGame[]>([]),
  allGrants = ref<PlayerAchievement[]>([])
const form = reactive<Record<string, string | number>>({}),
  editId = ref<number | null>(null),
  busy = ref(false),
  message = ref(''),
  error = ref(''),
  fieldErrors = ref<Record<string, unknown>>({}),
  deleting = ref<Row | null>(null),
  search = ref(''),
  gameFilter = ref('')
const snapshot = ref(''),
  playerId = ref<number | undefined>(),
  preservedRole = ref<number | null>(null)
const {
  loading,
  error: loadError,
  run,
} = useAsync(async () => {
  await catalog.load()
  ;[allLibrary.value, allGrants.value] = await Promise.all([api.getLibrary(), api.getUnlocks()])
  await player.load()
})
void run()
const rows = computed<Row[]>(() => {
  let source: unknown[] =
    key.value === 'games'
      ? catalog.games
      : key.value === 'achievements'
        ? catalog.achievements
        : key.value === 'levels'
          ? catalog.levels
          : key.value === 'grants'
            ? allGrants.value
            : key.value === 'library'
              ? allLibrary.value
              : []
  return (source as Row[]).filter(
    (row) =>
      (!gameFilter.value || row.game_id === Number(gameFilter.value)) &&
      JSON.stringify(row).toLowerCase().includes(search.value.toLowerCase()),
  )
})
const suggestions = computed(() =>
  [...new Set([...allLibrary.value, ...allGrants.value].map((row) => row.player_id))].sort(
    (a, b) => a - b,
  ),
)
function options(source: string) {
  return source === 'games'
    ? catalog.games.map((g) => ({ id: g.id, label: g.title }))
    : source === 'achievements'
      ? catalog.achievements.map((a) => ({
          id: a.id,
          label: `${catalog.games.find((g) => g.id === a.game_id)?.title ?? a.game_id} / ${a.name}`,
        }))
      : catalog.levelsSorted.map((l) => ({
          id: l.id,
          label: `LV ${l.number} ${l.title}`,
        }))
}
function reset() {
  Object.keys(form).forEach((k) => delete form[k])
  for (const field of config.value.fields) form[field.key] = ''
  editId.value = null
  preservedRole.value = null
  error.value = ''
  fieldErrors.value = {}
  if (key.value === 'grants') {
    const now = new Date()
    form.acquired_date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  }
}
watch(
  key,
  () => {
    reset()
    message.value = ''
    search.value = ''
    gameFilter.value = ''
    snapshot.value = ''
    playerId.value = undefined
  },
  { immediate: true },
)
function edit(row: Row) {
  reset()
  editId.value = row.id
  for (const field of config.value.fields) form[field.key] = String(row[field.key] ?? '')
}
function loadProfile(profile: Profile) {
  if (
    !Number.isInteger(profile.id) ||
    !Number.isInteger(profile.role) ||
    !profile.username ||
    !Number.isInteger(profile.level)
  )
    throw new Error('Snapshot needs id, username, role, and level.')
  editId.value = profile.id
  playerId.value = profile.id
  preservedRole.value = profile.role
  for (const field of config.value.fields)
    form[field.key] =
      field.key === 'password' ? '' : String(profile[field.key as keyof Profile] ?? '')
  error.value = ''
}
function importProfile() {
  try {
    loadProfile(JSON.parse(snapshot.value))
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Invalid profile JSON.'
  }
}
function ownProfile() {
  if (session.profile) loadProfile(session.profile)
}
function showError(e: unknown, deletingRecord = false) {
  if (e instanceof ApiError) {
    fieldErrors.value = e.fields
    error.value =
      deletingRecord && e.status >= 500
        ? 'This record may still be referenced. Remove its achievements, grants, or library assignments first, then retry.'
        : e.message
  } else error.value = e instanceof Error ? e.message : 'Request failed.'
}
async function submit() {
  busy.value = true
  error.value = ''
  fieldErrors.value = {}
  message.value = ''
  try {
    const body: Record<string, string | number> = {}
    for (const field of config.value.fields) {
      if (field.key === 'password' && !form.password) continue
      body[field.key] = field.type === 'number' ? Number(form[field.key]) : (form[field.key] ?? '')
    }
    if (key.value === 'players') {
      if (!editId.value || preservedRole.value === null)
        throw new Error('Load an existing profile snapshot first.')
      body.role = preservedRole.value
    }
    if (editId.value) await api.updateRecord(config.value.resource, editId.value, body)
    else await api.createRecord(config.value.resource, body)
    if (key.value === 'players' && editId.value === session.profile?.id) {
      const { password: _password, ...profileFields } = body
      session.profile = { ...session.profile, ...profileFields } as Profile
      const { save } = await import('@/lib/storage')
      save('ch.profile', session.profile)
    }
    reset()
    await run()
    message.value = 'Save complete. Your changes are live.'
  } catch (e) {
    showError(e)
  } finally {
    busy.value = false
  }
}
async function remove() {
  if (!deleting.value) return
  busy.value = true
  error.value = ''
  message.value = ''
  try {
    const id = deleting.value.id
    await api.deleteRecord(config.value.resource, id)
    deleting.value = null
    if (key.value === 'players' && id === session.profile?.id) {
      window.dispatchEvent(new Event('session-expired'))
      return
    }
    if (editId.value === id) reset()
    await run()
    message.value = 'Record deleted.'
  } catch (e) {
    showError(e, true)
    deleting.value = null
  } finally {
    busy.value = false
  }
}
const rowName = (row: Row) =>
  String(row.title ?? row.name ?? (row.player_id ? `Player ${row.player_id}` : `Record ${row.id}`))
</script>
<template>
  <section class="page-content">
    <div class="page-heading">
      <div>
        <p class="eyebrow">DEVELOPER ACCESS / LEVEL EDITOR</p>
        <h1>The dev console<span class="red">.</span></h1>
        <p>Build the worlds. Set the milestones. Reward the players.</p>
      </div>
      <span class="admin-stamp">ADMIN ONLY</span>
    </div>
    <div class="dev-layout">
      <nav class="dev-tools" aria-label="Developer tools">
        <RouterLink
          v-for="(editor, name) in editors"
          :key="name"
          :to="`/dev/${name}`"
          :class="{ selected: key === name }"
          ><span>▸</span>{{ editor.title }}</RouterLink
        >
      </nav>
      <LoadState :loading="loading" :error="loadError" @retry="run"
        ><div class="dev-workspace">
          <p v-if="message" class="success-message" role="status">✓ {{ message }}</p>
          <p v-if="error" class="field-error" role="alert">{{ error }}</p>
          <div class="editor-heading">
            <h2>{{ config.title }}</h2>
            <button class="text-button" @click="reset">
              {{ editId ? 'Cancel edit' : 'Clear form' }}
            </button>
          </div>
          <div v-if="key === 'players'" class="profile-import">
            <p>
              Player profiles cannot be fetched by this API. Load your own profile or paste an
              existing profile JSON snapshot to preserve its role.
            </p>
            <button @click="ownProfile">Edit my profile</button
            ><label
              >Existing profile JSON<textarea
                v-model="snapshot"
                placeholder='{"id": 2, "username": "player", "role": 2, "level": 1}'
              /></label
            ><button :disabled="!snapshot" @click="importProfile">Load snapshot</button>
            <div class="player-delete">
              <label
                >Player ID to delete<input v-model.number="playerId" type="number" min="1" /></label
              ><button
                class="danger"
                :disabled="!playerId || busy"
                @click="
                  deleting = {
                    id: Number(playerId),
                    name: `Player ${playerId}`,
                  }
                "
              >
                Delete player…
              </button>
            </div>
          </div>
          <form class="editor-form" @submit.prevent="submit">
            <h3>{{ editId ? `EDIT RECORD #${editId}` : 'NEW RECORD' }}</h3>
            <label v-for="field in config.fields" :key="field.key"
              >{{ field.label
              }}<select v-if="field.source" v-model="form[field.key]" required>
                <option disabled value="">Select {{ field.label.toLowerCase() }}</option>
                <option v-for="option in options(field.source)" :key="option.id" :value="option.id">
                  {{ option.label }} (#{{ option.id }})
                </option></select
              ><textarea
                v-else-if="field.type === 'textarea'"
                v-model="form[field.key]"
                required
              /><input
                v-else
                v-model="form[field.key]"
                :type="field.type ?? 'text'"
                :min="field.type === 'number' ? (field.key === 'player_id' ? 1 : 0) : undefined"
                :step="field.type === 'number' ? 1 : undefined"
                :list="field.key === 'player_id' ? 'player-ids' : undefined"
                :required="
                  !['first_name', 'last_name', 'email'].includes(field.key) &&
                  !(key === 'players' && field.key === 'password')
                "
                :autocomplete="field.type === 'password' ? 'new-password' : 'off'"
                :aria-invalid="Boolean(fieldErrors[field.key])"
              /><small v-if="fieldErrors[field.key]" class="field-error">{{
                (fieldErrors[field.key] as string[]).join(' ')
              }}</small></label
            ><datalist id="player-ids">
              <option v-for="id in suggestions" :key="id" :value="id" /></datalist
            ><button
              class="primary"
              :disabled="busy || (key === 'players' && preservedRole === null)"
            >
              {{ busy ? 'Saving…' : editId ? 'Save changes →' : 'Create record +' }}
            </button>
          </form>
          <template v-if="key !== 'players'"
            ><div class="filters">
              <label
                >Search records<input
                  v-model="search"
                  type="search"
                  placeholder="Search records…" /></label
              ><label v-if="key === 'achievements' || key === 'library'"
                >Game<select v-model="gameFilter">
                  <option value="">All games</option>
                  <option v-for="game in catalog.games" :key="game.id" :value="game.id">
                    {{ game.title }}
                  </option>
                </select></label
              >
            </div>
            <div class="record-list">
              <article v-for="row in rows" :key="row.id">
                <div>
                  <small>#{{ row.id }}</small>
                  <h3>{{ rowName(row) }}</h3>
                  <p
                    v-for="field in config.fields.filter(
                      (f) => f.key !== 'title' && f.key !== 'name',
                    )"
                    :key="field.key"
                  >
                    <b>{{ field.label }}:</b>
                    {{
                      field.source
                        ? (options(field.source).find((o) => o.id === row[field.key])?.label ??
                          row[field.key])
                        : row[field.key]
                    }}
                  </p>
                </div>
                <div class="record-actions">
                  <button :disabled="busy" @click="edit(row)">Edit</button
                  ><button class="danger" :disabled="busy" @click="deleting = row">Delete…</button>
                </div>
              </article>
              <p v-if="!rows.length" class="inspect-hint">No records found.</p>
            </div></template
          >
        </div></LoadState
      >
    </div>
    <Modal
      v-if="deleting"
      :title="`Delete ${rowName(deleting)}?`"
      @close="!busy && (deleting = null)"
      ><p>This can’t be undone. Referenced records may need to be removed first.</p>
      <div class="modal-actions">
        <button :disabled="busy" @click="deleting = null">Keep it</button
        ><button class="danger" :disabled="busy" @click="remove">
          {{ busy ? 'Deleting…' : 'Delete permanently' }}
        </button>
      </div></Modal
    >
  </section>
</template>
