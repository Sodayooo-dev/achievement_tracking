# Cartridge Hub

Vue 3, TypeScript, Pinia and Vue Router frontend for the Django achievement tracker. The approved QA improvements cover permissions/data validation, shared player controls, the loading animation, self-service library additions and the admin console.

## Run locally

Install backend requirements, apply migrations, and start Django at `http://127.0.0.1:8000`. From `frontend/`, run:

```sh
npm install
npm run dev
```

Vite proxies both `/api` and `/media` to Django. Open the URL Vite prints. Use Node 24.12+ or Node 22.18+.

Copy `.env.example` to `.env.local` if your Admin role ID differs from the verified ID 1. Registration defaults are now assigned by Django: `REGISTRATION_ROLE_ID=2` (User) and `REGISTRATION_LEVEL_ID=1`. The browser cannot choose privileged roles or staff/superuser flags. Password validators apply on registration and password updates.

The first rank requires 1,000 XP. The HUD deliberately displays Unranked below that threshold and calculates ranks from unique unlocked achievements.

## Player experience

- Fixed viewport console, internal CRT scrolling, corner chromatic aberration and responsive navigation.
- Searchable catalog with local artwork and **Add to my library**. Only the authenticated player's library is changed, and repeated additions are idempotent.
- Seven genre layouts with compact search/status/view controls. Secondary sorting lives in a Filters dialog (a phone sheet), leaving more room for objectives.
- A compact game bar opens full game information on demand. Eject stays in the hardware strip outside the scroller and is disabled during insertion/loading.
- Hover/focus previews stay within the visible glass. Select an achievement for full details; long descriptions scroll within the dialog. Escape closes it and restores focus. Mobile details open as a sheet.
- Ordinary locked objectives retain their names. Public-source secret descriptions remain concealed where the source does not provide requirements.
- Arrow/Home/End navigation follows the rendered grid. Inventory cells are at least 48 pixels wide, and the phone world map runs vertically.
- Cartridge insertion is non-skippable and runs while fresh per-game objectives and player progress load. Shared geometry cuts the cartridge at the slot mouth; the bezel hides inserted faces while exposed faces remain connected. One animation clock drives movement, phases and progress. If the server remains busy after seating, the indicator becomes indeterminate. Requests time out after 20 seconds and errors offer Retry.
- Existing catalog requests are shared/cached; manual refresh updates the catalog. Player responses are guarded against stale sessions.
- Token renewal is shared across concurrent 401 responses. A failed refresh leads to the existing session-expired screen. Passwords are not persisted.

The insertion sequence still runs with OS reduced motion, as explicitly requested earlier; other animations respect reduced motion. XP/unlocks remain administrator-verified. Self-reported completion and library archival are deferred.

## Admin console

The existing `/dev` route now opens an overview with record counts, recent grants and catalog-health flags. Workspaces cover Games, Achievements, Players, Grants, Libraries and Levels.

Lists use server pagination (20 rows) and search. Game links open a scoped achievement list. Edits open in a visible dialog with Save/Cancel controls. Unsaved edits prompt before cancellation/navigation, and safe drafts can be restored. Drafts omit passwords and cannot persist selected file bytes.

- Games: create/edit, local artwork preview/upload/removal, and direct links to objectives.
- Achievements: game filters, objective editing, XP validation and duplicate-as-draft.
- Players: administrator-only search/profile lookup, library/progress/recent history, safe profile editing. Pasted JSON snapshots are no longer needed.
- Grants: choose player, then an owned game, then a remaining objective. Existing unlocks are excluded. Date-only edits to legacy grants remain supported.
- Libraries: searchable player and game choices.
- Levels: ordered ranks with unique, increasing thresholds and nonnegative XP.
- Deletes: dependencies return a 409 response with counts. Existing progress is protected, and the signed-in administrator cannot delete their own account.

Bulk actions, CSV/JSON imports, audit history, archival and orphan-media cleanup are deferred to the separately proposed stage 4. Removing/replacing artwork updates its reference; unreferenced files are retained until a reviewed cleanup policy is implemented.

## API compatibility and data integrity

Existing CRUD routes remain available. List endpoints still return arrays by default. Requesting `?page=1&page_size=20` returns `{count,next,previous,results}`, where next/previous are page numbers. Supported query parameters include search, permitted ID filters, and ordering by a model field.

Added routes:

| Route | Purpose |
|---|---|
| `GET /api/me/` | Fresh current-player profile |
| `PUT /api/me/` | Safe own-profile updates |
| `POST /api/token/refresh/` | Access-token renewal |
| `POST /api/me/library/` | Add a catalog game using only game_id |
| `GET /api/players/` | Administrator-only player search/list |
| `GET /api/players/:id/` | Administrator-only player lookup |

Regular players receive only their own library and unlock rows; admin lists retain authorized access across players. Ordinary players cannot create global games or award XP.

New migrations enforce unique player/game and player/achievement pairs, nonnegative achievement XP, positive level numbers and unique/nonnegative level thresholds. API validation additionally enforces increasing thresholds and library ownership for new/reassigned grants. The live audit found no duplicates or invalid thresholds/XP. Two existing grants outside their players' libraries were preserved, along with all progress.

Apply all Django migrations when setting up another database. Audit existing duplicates/negative values before deploying constraints to a different dataset; migrations intentionally do not delete or rewrite progress.

## Artwork and real catalog

All 24 current official images are included in `backend/media/game_icons/` (about 1.4 MB), and PostgreSQL stores their file paths. Rendering uses local `/media/game_icons/...` URLs. API responses expose these paths through both image and the compatible image_url property.

Admin uploads accept PNG, JPEG and WebP up to 5 MB and 16 megapixels. The original bytes are preserved. Missing artwork falls back to a deterministic pixel icon.

The catalog contains 24 real games and 2,117 achievement definitions. Most sources are public Steam Community lists and publisher-uploaded Steam header artwork. Minecraft and Gran Turismo use the referenced platform/wiki/trophy snapshots. Provenance and metadata snapshots are under `data/`; unknown secret requirements are not invented. Existing converted definitions retain their original IDs and XP; newly imported definitions use 100 app XP.

The original import and local-artwork localization can be rerun from `backend/`:

```powershell
./.venv/Scripts/python.exe -B manage.py shell -c "from pathlib import Path; exec(Path('../frontend/scripts/import_real_catalog.py').read_text(encoding='utf-8'))"
./.venv/Scripts/python.exe -B manage.py shell -c "from pathlib import Path; exec(Path('../frontend/scripts/localize_game_artwork.py').read_text(encoding='utf-8'))"
```

Existing local files are reused. The original definition backup remains in `data/before_real_catalog.json`. No accounts, assignments or grants are deleted by the import.

## Audio

Six unmodified effects from [Kenney Interface Sounds](https://kenney.nl/assets/interface-sounds), licensed CC0, are bundled under `public/audio/`. No audio is synthesized or generated. Playback requires user interaction; the header toggle persists the mute preference. Original attribution/license files are included.

## Validation

From `frontend/`:

```sh
npm test
npm run build
npm run format
```

20 frontend tests cover cartridge geometry/timing, shared refresh/retry, stale authentication, catalog caching, loading coordination, sound gating, XP, genre selection, API errors, registration and player isolation.

From `backend/`:

```powershell
./.venv/Scripts/python.exe -B ../frontend/scripts/run_upload_tests.py
```

14 backend tests use in-memory SQLite and temporary artwork, never PostgreSQL. They exercise privilege rejection, password validation, player data isolation, self-library identity/idempotency, admin lookup, negative/duplicate data, protected deletes, pagination/detail responses, JWT refresh, artwork validation/removal/replacement and upload permissions.

Browser QA used a disposable local server to inspect admin search, scoped pagination, editing/saving, dirty-form protection, grant selection/saving, player lookup and library additions. All seven themes passed narrow-phone checks for visible previews, 44-pixel targets and a fixed outer document. Escape/focus restoration and natural insertion frames were inspected.

A reproducible disposable browser environment can be started from `backend/`:

```powershell
./.venv/Scripts/python.exe -B ../frontend/scripts/run_browser_qa.py
```

Then run a separate frontend from `frontend/`:

```powershell
$env:CARTRIDGE_API_TARGET='http://127.0.0.1:8001'
npm run dev -- --host 127.0.0.1 --port 5175 --strictPort
```

This creates only temporary SQLite accounts/media, which are removed on server exit. The script contains clearly identified disposable test credentials; it must not be used as a production server. Reset CARTRIDGE_API_TARGET afterward or use a fresh shell for the regular frontend.

The regular test account `cartridge_tester` (player ID 7) still owns 18 games and has 133 unlocks / 13,485 XP. Its credentials are not stored in frontend source. `scripts/verify_ui_test_data.py` performs read-only live verification using CARTRIDGE_TEST_PASSWORD or an interactive prompt. These unlocks represent simulated test progress, not a platform account integration.

## Production hosting

Serve `dist/` with SPA fallback, proxy `/api` to Django, and serve `/media/` from persistent backend media storage. Django's development media server and Vite proxies are development-only. Back up PostgreSQL and the media directory together. Configure production secrets, hosts and DEBUG separately before deployment.
