import { test, after } from 'node:test'
import assert from 'node:assert/strict'
import { fileURLToPath } from 'node:url'
import { build } from 'vite'
import { createPinia, setActivePinia } from 'pinia'

// Bundle application TypeScript with the project's existing toolchain. Tests use mocked HTTP only.
await build({
  configFile: false,
  logLevel: 'error',
  root: fileURLToPath(new URL('..', import.meta.url)),
  resolve: { alias: { '@': fileURLToPath(new URL('../src', import.meta.url)) } },
  build: {
    lib: {
      entry: fileURLToPath(new URL('./entry.ts', import.meta.url)),
      formats: ['es'],
      fileName: () => 'core.mjs',
    },
    outDir: 'node_modules/.tmp/core-tests',
    emptyOutDir: false,
    rolldownOptions: { external: ['vue', 'pinia'] },
  },
})
const saved = new Map()
globalThis.localStorage = {
  getItem: (key) => saved.get(key) ?? null,
  setItem: (key, value) => saved.set(key, value),
}
globalThis.window = new EventTarget()
const {
  progression,
  genreToTheme,
  pixelIcon,
  request,
  ApiError,
  setAccessToken,
  useSession,
  useCatalog,
  usePlayer,
  playSound,
  toggleSound,
  soundEnabled,
  installUiSounds,
  useCartridgeLoad,
  cartridgePose,
  frontloader,
} = await import('../node_modules/.tmp/core-tests/core.mjs')
test('cartridge crosses a shared aperture continuously and fits its full travel', () => {
  assert.ok(frontloader.slot.top < frontloader.seam)
  assert.ok(frontloader.seam + frontloader.thickness < frontloader.slot.bottom)
  let previousY = 0
  const [leadingLeft, leadingRight, trailingRight, trailingLeft] = frontloader.top
  for (let elapsed = 0; elapsed <= frontloader.duration; elapsed += 10) {
    const { y } = cartridgePose(elapsed)
    assert.ok(y <= previousY)
    previousY = y
    const localSeam = frontloader.seam - y
    if (localSeam >= leadingLeft[1] && localSeam <= trailingLeft[1]) {
      const ratio = (localSeam - leadingLeft[1]) / (trailingLeft[1] - leadingLeft[1])
      assert.ok(
        leadingLeft[0] + (trailingLeft[0] - leadingLeft[0]) * ratio - 1 >= frontloader.slot.left,
      )
      assert.ok(
        leadingRight[0] + (trailingRight[0] - leadingRight[0]) * ratio + 1 <=
          frontloader.slot.right,
      )
    }
  }
  const seated = cartridgePose(frontloader.duration)
  assert.ok(
    Math.max(...frontloader.top.map((p) => p[1])) + frontloader.thickness + seated.y + 1 <
      frontloader.slot.top,
  )
})
test('insertion labels and mechanical progress follow the same timeline', () => {
  assert.equal(cartridgePose(0).phase, 'ALIGNING CARTRIDGE')
  assert.equal(cartridgePose(450).phase, 'INSERTING CARTRIDGE')
  assert.equal(cartridgePose(1700).phase, 'CARTRIDGE LOCKED')
  assert.equal(cartridgePose(1900).phase, 'READING SAVE DATA')
  assert.equal(cartridgePose(frontloader.duration).progress, 1)
  assert.equal(cartridgePose(frontloader.duration + 1000).y, -180)
})
const originalFetch = globalThis.fetch
test('multipart artwork uploads preserve FormData and let the browser set its boundary', async () => {
  setAccessToken('upload-token')
  const data = new FormData()
  data.append('title', 'Test game')
  data.append('image', new Blob(['fixture'], { type: 'image/png' }), 'icon.png')
  globalThis.fetch = async (_url, options) => {
    assert.equal(options.body, data)
    assert.equal(options.headers['Content-Type'], undefined)
    assert.equal(options.headers.Authorization, 'Bearer upload-token')
    return Response.json({ image_url: '/media/game_icons/icon.png' })
  }
  assert.equal((await request('games/new/', 'POST', data)).image_url, '/media/game_icons/icon.png')
})
test('simultaneous authenticated 401s share one refresh and retry with the new token', async () => {
  setAccessToken('expired', 'refresh-fixture')
  let renewals = 0
  globalThis.fetch = async (url, init) => {
    if (url.includes('token/refresh')) {
      renewals++
      await Promise.resolve()
      return Response.json({ access: 'renewed' })
    }
    return init.headers.Authorization === 'Bearer renewed'
      ? Response.json({ ok: true })
      : Response.json({}, { status: 401 })
  }
  const results = await Promise.all([request('games/'), request('levels/')])
  assert.equal(renewals, 1)
  assert.ok(results.every((result) => result.ok))
  setAccessToken('')
})
test('a refresh response cannot overwrite a newer login', async () => {
  setAccessToken('old', 'old-refresh')
  let complete, started
  const ready = new Promise((resolve) => {
    started = resolve
  })
  const delayed = new Promise((resolve) => {
    complete = resolve
  })
  globalThis.fetch = async (url) => {
    if (url.includes('token/refresh')) {
      started()
      await delayed
      return Response.json({ access: 'stale' })
    }
    return Response.json({}, { status: 401 })
  }
  const oldRequest = request('games/')
  await ready
  setAccessToken('new-login')
  complete()
  await assert.rejects(oldRequest)
  globalThis.fetch = async (_url, init) => {
    assert.equal(init.headers.Authorization, 'Bearer new-login')
    return Response.json({})
  }
  await request('games/')
  setAccessToken('')
})
test('catalog shares pending requests and reuses cached data until explicit refresh', async () => {
  setActivePinia(createPinia())
  let calls = 0
  globalThis.fetch = async () => {
    calls++
    return Response.json([])
  }
  const catalog = useCatalog()
  await Promise.all([catalog.load(), catalog.load()])
  assert.equal(calls, 3)
  await catalog.load()
  assert.equal(calls, 3)
  await catalog.load(true)
  assert.equal(calls, 6)
})
test('cartridge loading waits for slow server data after animation completion', async () => {
  let resolveData
  const data = new Promise((resolve) => {
    resolveData = resolve
  })
  const state = useCartridgeLoad(() => data)
  const pending = state.loadGame()
  state.animationFinished()
  assert.equal(state.inserting.value, true)
  assert.equal(state.loading.value, true)
  resolveData()
  await pending
  assert.equal(state.inserting.value, false)
})
test('fast server data cannot bypass insertion; failed requests allow retry', async () => {
  let fail = false
  const state = useCartridgeLoad(async () => {
    if (fail) throw new Error('Connection interrupted')
  })
  await state.loadGame()
  assert.equal(state.inserting.value, true)
  state.animationFinished()
  assert.equal(state.inserting.value, false)
  fail = true
  await state.loadGame()
  state.animationFinished()
  assert.equal(state.inserting.value, false)
  assert.equal(state.error.value, 'Connection interrupted')
  fail = false
  await state.loadGame()
  assert.equal(state.error.value, '')
  assert.equal(state.inserting.value, true)
  state.animationFinished()
  assert.equal(state.inserting.value, false)
})
test('an older fetch cannot release the loading screen while a newer one is pending', async () => {
  const resolvers = []
  const state = useCartridgeLoad(() => new Promise((resolve) => resolvers.push(resolve)))
  const first = state.loadGame(),
    second = state.loadGame()
  state.animationFinished()
  resolvers[0]()
  await first
  assert.equal(state.inserting.value, true)
  resolvers[1]()
  await second
  assert.equal(state.inserting.value, false)
})
const originalAudio = globalThis.Audio
const originalDocument = globalThis.document
after(() => {
  globalThis.fetch = originalFetch
  globalThis.Audio = originalAudio
  globalThis.document = originalDocument
})
const levels = [
  { id: 2, number: 2, title: 'Veteran', exp_required: 100 },
  { id: 1, number: 1, title: 'Novice', exp_required: 0 },
  { id: 3, number: 3, title: 'Legend', exp_required: 300 },
]
test('downloaded sound effects wait for interaction, and muting stops active playback', () => {
  const clips = []
  globalThis.document = new EventTarget()
  globalThis.Audio = class {
    currentTime = 0
    paused = true
    volume = 1
    constructor(source) {
      this.source = source
      clips.push(this)
    }
    play() {
      this.paused = false
      return Promise.resolve()
    }
    pause() {
      this.paused = true
    }
  }
  const cleanup = installUiSounds()
  playSound('click')
  assert.equal(clips.length, 0)
  document.dispatchEvent(new Event('pointerdown'))
  playSound('click')
  assert.equal(clips.length, 1)
  assert.ok(clips[0].source.endsWith('/audio/click_001.ogg'))
  assert.equal(clips[0].volume, 0.2)
  toggleSound()
  assert.equal(soundEnabled.value, false)
  assert.equal(clips[0].paused, true)
  playSound('confirm')
  assert.equal(clips.length, 1)
  toggleSound()
  assert.equal(soundEnabled.value, true)
  assert.equal(clips[0].paused, false)
  cleanup()
  assert.equal(clips[0].paused, true)
})
test('XP uses thresholds, handles exact boundaries and max level', () => {
  assert.equal(progression(levels, 99).current.id, 1)
  const atBoundary = progression(levels, 100)
  assert.equal(atBoundary.current.id, 2)
  assert.equal(atBoundary.intoLevel, 0)
  assert.equal(atBoundary.needed, 200)
  assert.equal(progression(levels, 200).pct, 50)
  const max = progression(levels, 350)
  assert.equal(max.next, null)
  assert.equal(max.pct, 100)
})
test('empty levels and XP below the first threshold do not invent a level', () => {
  assert.equal(progression([], 0).current, null)
  assert.equal(progression([{ id: 1, number: 1, title: 'First', exp_required: 50 }], 25).pct, 50)
})
test('all seven genres, case-insensitive keywords, and first-match precedence', () => {
  for (const [genre, key] of [
    ['Survival RPG', 'inventory'],
    ['Role-playing', 'skilltree'],
    ['Platformer', 'worldmap'],
    ['FPS', 'killfeed'],
    ['Brawler', 'charselect'],
    ['Driving', 'trophy'],
    ['Puzzle', 'questlog'],
  ])
    assert.equal(genreToTheme(genre), key)
})
test('pixel sprites are stable, mirrored and within an 8×8 grid', () => {
  const cells = pixelIcon('Diamond hunter')
  assert.deepEqual(cells, pixelIcon('Diamond hunter'))
  assert.notDeepEqual(cells, pixelIcon('First steps'))
  for (const cell of cells) {
    assert.ok(cell.x >= 0 && cell.x < 8 && cell.y >= 0 && cell.y < 8)
    assert.ok(cells.some((c) => c.x === 7 - cell.x && c.y === cell.y))
  }
})
test('authenticated request sends Bearer token and parses lists', async () => {
  setAccessToken('test-token')
  let options
  globalThis.fetch = async (url, init) => {
    assert.equal(url, '/api/games/')
    options = init
    return Response.json([{ id: 1 }])
  }
  assert.deepEqual(await request('games/'), [{ id: 1 }])
  assert.equal(options.headers.Authorization, 'Bearer test-token')
})
test('login 401 stays on login while authenticated 401 expires the session', async () => {
  let expired = 0
  const listener = () => expired++
  window.addEventListener('session-expired', listener)
  globalThis.fetch = async (_url, init) => {
    if (_url.includes('login')) assert.equal(init.headers.Authorization, undefined)
    return Response.json({ message: 'Invalid credentials' }, { status: 401 })
  }
  await assert.rejects(
    request('login/', 'POST', {}, true),
    (e) => e instanceof ApiError && e.status === 401,
  )
  assert.equal(expired, 0)
  await assert.rejects(request('games/'))
  assert.equal(expired, 1)
  window.removeEventListener('session-expired', listener)
})
test('an old request cannot expire a newly signed-in session', async () => {
  setAccessToken('old-token')
  let expired = 0
  const listener = () => expired++
  window.addEventListener('session-expired', listener)
  globalThis.fetch = async () => {
    setAccessToken('new-token')
    return Response.json({}, { status: 401 })
  }
  await assert.rejects(request('games/'))
  assert.equal(expired, 0)
  window.removeEventListener('session-expired', listener)
})
test('DRF field errors, forbidden responses, no-content deletes and network failures', async () => {
  globalThis.fetch = async () => Response.json({ username: ['Already taken.'] }, { status: 400 })
  await assert.rejects(
    request('register/', 'POST', {}, true),
    (e) => e.fields.username[0] === 'Already taken.',
  )
  globalThis.fetch = async () => Response.json({}, { status: 403 })
  await assert.rejects(request('games/'), /Developer access only/)
  globalThis.fetch = async () => new Response(null, { status: 204 })
  assert.equal(await request('games/1/delete/', 'DELETE'), null)
  globalThis.fetch = async () => {
    throw new TypeError('offline')
  }
  await assert.rejects(request('games/'), (e) => e.status === 0)
})
test('registration leaves role and starting level to the server, then signs in', async () => {
  setActivePinia(createPinia())
  let payload
  globalThis.fetch = async (url, init) => {
    if (url.includes('register')) {
      payload = JSON.parse(init.body)
      return Response.json({ id: 7 })
    }
    return Response.json({
      profile: { id: 7, username: 'sam', role: 2, level: 1 },
      tokens: { access: 'player-token', refresh: 'unused' },
    })
  }
  const session = useSession()
  await session.register({ username: 'sam', password: 'test-only' })
  assert.equal(payload.role, undefined)
  assert.equal(payload.level, undefined)
  assert.equal(session.isLoggedIn, true)
  assert.equal(session.isAdmin, false)
  session.logout()
  assert.equal(session.isLoggedIn, false)
  assert.equal(JSON.parse(saved.get('ch.access')), '')
})
test('player data is scoped to identity and duplicate grants cannot inflate XP', async () => {
  setActivePinia(createPinia())
  const session = useSession(),
    catalog = useCatalog(),
    player = usePlayer()
  session.profile = { id: 7, username: 'sam', role: 2, level: 1 }
  catalog.games = [
    { id: 1, title: 'Test game', publisher: 'Studio', genre: 'Sandbox' },
    { id: 2, title: 'Other game', publisher: 'Studio', genre: 'RPG' },
  ]
  catalog.levels = levels
  catalog.achievements = [
    { id: 11, game_id: 1, name: 'First steps', description: 'Play', exp_value: 100 },
    { id: 12, game_id: 1, name: 'Final boss', description: 'Finish', exp_value: 200 },
  ]
  globalThis.fetch = async (url) =>
    Response.json(
      url.includes('player_games')
        ? [
            { id: 1, player_id: 7, game_id: 1 },
            { id: 2, player_id: 8, game_id: 2 },
          ]
        : [
            { id: 1, player_id: 7, achievement_id: 11, acquired_date: '2026-10-01' },
            { id: 2, player_id: 7, achievement_id: 11, acquired_date: '2026-10-02' },
            { id: 3, player_id: 8, achievement_id: 12, acquired_date: '2026-10-03' },
          ],
    )
  await player.load()
  assert.equal(player.library.length, 1)
  assert.equal(player.unlocks.length, 2)
  assert.equal(player.totalExp, 100)
  assert.deepEqual(player.completion(1), { got: 1, total: 2, pct: 50 })
  assert.equal(player.ownedGames[0].id, 1)
  assert.equal(player.progress.current.id, 2)
  player.reset()
  assert.equal(player.totalExp, 0)
  assert.equal(player.ownedGames.length, 0)
})
