# Cartridge Hub

A Vue 3 + TypeScript achievement tracker built on the existing Django API. Frontend implementation lives in `frontend/`. The only backend edit was the user-approved local database password update in `config/settings.py`.

## Run locally

Use Node 24.12+ (or Node 22.18+) and run these commands in `frontend/`:

```sh
npm install
npm run dev
```

Start your existing Django backend separately at `http://127.0.0.1:8000`. Vite forwards `/api` to it. Open the local URL printed by Vite. Backend startup and database configuration remain under your control.

Copy `.env.example` to `.env.local` to override the confirmed defaults:

```dotenv
VITE_ADMIN_ROLE_ID=1
VITE_DEFAULT_ROLE_ID=2
VITE_DEFAULT_LEVEL_ID=1
```

These reference the verified database rows: Admin = 1, User = 2, first level = 1. Restart Vite after changing them. Registration always uses the configured user role; there is no role selector. The first level, Noob, requires 1,000 XP; the HUD intentionally shows Unranked below that threshold, as confirmed.

## Included

- PRESS START title screen, login, registration and automatic sign-in; field errors and expired-session screen.
- Console shell, player identity, refresh control and XP calculated from unique unlocked achievements.
- Keyboard navigable cartridge library, completion stamps, searchable catalog and monthly save history.
- Seven lazy-loaded genre layouts: inventory, skill tree, world map, combat HUD, fighter selection, trophy cabinet and quest journal fallback.
- Deterministic pixel sprites, cartridge insertion, first-visit-safe unlock notifications, floating XP, level-up and perfect-completion banners.
- Admin creation, editing and deletion for games, achievements, levels, grants and library assignments. Player profiles can be updated using a supplied existing profile JSON snapshot; your own profile can be loaded from the session. Roles are preserved. Player deletion uses an entered ID.
- Responsive layouts, visible focus states, dialog focus trapping, live announcements, and reduced-motion support. Fonts are bundled from Fontsource and do not require a CDN.

Skill-tree connections visualize XP tiers, not gameplay prerequisites. Trophy tiers divide achievements by XP rank within a game. Unowned catalog games are read-only.

## Validation

```sh
npm test
npm run build
npm run format
```

Tests use mocked HTTP and the actual Pinia stores. They cover XP boundaries, genre mapping, sprite determinism, authentication headers, public versus authenticated 401 responses, stale requests, DRF errors, registration defaults and player data isolation. Tests never contact or mutate the backend.

Manual acceptance checks with your backend running:

1. Sign in as a player and check owned games, XP, catalog filtering and timeline against the database.
2. Open games across all seven genre groups. Check locked descriptions by keyboard and touch.
3. At 360px, 768px and desktop widths, check that navigation and all content fit. Check Arrow keys, Home/End, Enter and visible focus.
4. Sign in as an admin; exercise each editor against disposable records. Check delete cancellation, Escape, focus trapping and errors for referenced records.
5. Grant an achievement, refresh the recipient's session, and verify one notification, XP, and level/perfect banners. First visit should remain silent.
6. With reduced motion enabled, check that animations stop. With an expired token, check GAME OVER; invalid login credentials should stay on the title screen.

## Existing API constraints

No refresh or current-user route exists. Expired access tokens require signing in again. Players cannot add games or unlock achievements themselves. List responses are filtered by player ID in the frontend. Profile updates require snapshots because there is no player lookup/list route. Dependent deletes can fail under Django's PROTECT constraints.

The API accepts role IDs during registration; restricting that on the server remains an existing backend concern. The frontend always supplies the configured User role ID, but UI restrictions do not replace backend authorization.

For production, serve `dist/` after `npm run build`, configure SPA fallback to `index.html`, and forward `/api` to Django at the hosting layer. The Vite proxy applies to development only.

## Verification status

Type checking, production build and all 14 automated tests passed. A read-only database connection verified the password update and role/level IDs. With Django running, `/api/games/` and `/api/levels/` returned the expected 401 through the Vite proxy. The original browser-access blocker was resolved, and the updated viewport layout, internal scrolling, corner aberration, title screen and sound toggle were inspected in the live browser. Admin CRUD and all genre layouts still need the broader manual checks above.

## Seeded UI test account

The local database now has a normal user named `cartridge_tester` (player ID 7). It owns 18 games and has 133 unlocked achievements worth 13,485 XP (Pro). The catalog contains 22 games and 298 achievements. Minecraft and Baldur's Gate 3 are complete, three owned games are untouched, and the rest show partial progress. Save history spans April–October 2026. All seven genre layouts have populated fixtures, including unowned catalog entries.

Fixture achievements are prefixed `[UI Test]`; they are test objectives rather than official game achievements. Existing records are preserved. The additive seed script lives at `scripts/seed_ui_test_data.py` and can be rerun through Django shell without duplicating fixtures or resetting the test password. Credentials were supplied in the chat and are not stored in frontend source.

`scripts/verify_ui_test_data.py` verifies login, library, unlocks, completion and history through the real Vite proxy using `CARTRIDGE_TEST_PASSWORD` or a password prompt. This API verification passed against the seeded account.

## CRT immersion and audio

The console fills the viewport (`100dvh`), with the header, XP HUD and navigation outside the internal screen scroller. The title screen also keeps its hardware fixed and scrolls its save forms inside the glass. Screen content resets to the top when navigating. Short screens and mobile safe areas are accounted for.

The CRT glass uses rounded optical edges, static scanlines, corner shading and a masked SVG red/cyan channel split that fades to a sharp center. Forced-colors mode disables optical overlays. Selecting a cartridge plays a front-loading console sequence: the cartridge aligns with the horizontal slot, slides in with its label down, seats, and loads the selected game. Its travel follows the cartridge's projected depth vector, and a fixed clip plane at the slot hides only the inserted portion. The sequence cannot be skipped. Fresh catalog and player data loads concurrently; the game opens only after both the 2.35-second sequence and the requests finish. If the server takes longer, the cartridge stays inserted with a reading message. Errors offer Retry. Per the explicit animation request, this sequence plays even when OS reduced motion is enabled; other reduced-motion behavior is unchanged. Timers and Web Animations are canceled on unmount.

Sound effects are original, unmodified files from [Kenney's Interface Sounds](https://kenney.nl/assets/interface-sounds), licensed CC0. Six downloaded Ogg effects provide selection, buttons, cartridge seating, confirmation, errors and ejecting. No sound is generated or synthesized. Effects require user interaction and play quietly; the header sound button saves the player's preference. Source details and the original license are included under `public/audio/`.

The updated layout was inspected in the browser at desktop and mobile widths. Internal scrolling leaves document scroll at zero and keeps the XP HUD visible. The sound toggle, corner filter and corrected slot alignment were checked in the live UI. All 14 automated tests pass, including slow/fast server loading, retries, overlapping requests, user-interaction gating and stopping playback when muted.
