# AGENTS.md — Phase 8: Landing Page, AI Assistant, Visual System, Maps Fix

The search/results view (map + property list) is functionally solid. This phase adds
what's missing to feel like a real product: a proper landing/home page (Zillow-style),
placeholder AI assistant entry points, a real colour system, and a fix for the Google
Maps API key issue. This phase touches routing (new home page) as well as visual design
— it is broader than the last polish pass, but still does not touch backend logic,
data-fetching, or filter behaviour beyond what's explicitly listed below.

---

## 1. Fix the Google Maps API key issue FIRST

Before any new UI work, diagnose and fix the map loading problem:

1. Confirm `VITE_GOOGLE_MAPS_KEY` (or whatever the actual env var is named — check
   `frontend/.env` and `frontend/.env.example`) is set to a real, valid key, not a
   placeholder string left over from scaffolding.
2. Open the browser console on the current app and report the exact error shown near
   the map component — Google Maps API key errors are usually explicit
   (`InvalidKeyMapError`, `RefererNotAllowedMapError`, `ApiNotActivatedMapError`, or
   similar) and tell us exactly what's wrong, rather than guessing.
3. Common causes to check, in order:
   - Key exists in `.env` but Vite wasn't restarted after adding it (`VITE_` env vars
     are baked in at build/dev-server start, not read live — a restart is required)
   - Key exists but the Maps JavaScript API isn't enabled for that key in Google Cloud
     Console
   - Key has HTTP referrer restrictions that don't include `localhost` — check the
     key's restrictions in Google Cloud Console if using one
   - Billing isn't enabled on the Google Cloud project (Maps JS API requires it even
     for free-tier usage)
4. **Important context**: Phase 6 previously migrated the map itself from Google Maps
   to Leaflet + OpenStreetMap specifically to remove the Google Maps API key
   dependency. If the current codebase still has a Google Maps API key requirement
   somewhere, that migration may be incomplete, or there may be two different map
   implementations partially present. Check whether `MapContainer.tsx` is actually
   using Leaflet or Google Maps JS API right now, and report which one it finds — this
   needs to be resolved as ONE consistent implementation, not a mix. If Leaflet is the
   intended approach per Phase 6/7, no Google Maps API key should be required at all —
   fixing this may mean removing leftover Google Maps code entirely rather than
   supplying a working key.

Report back what you find before proceeding — this determines whether the rest of the
app needs a Google Maps key or not.

---

## 2. New landing/home page

Add a new route (`/` — the search/map view moves to `/search`) that mirrors the
structure of a Zillow-style homepage:

```
frontend/src/pages/
├── HomePage.tsx          # NEW — the landing page
└── SearchPage.tsx        # existing map+list view, now at /search
```

### HomePage layout
- Full-width hero section with a background image or a solid brand-colour gradient
  (do not source a stock photo without checking with me first — a clean gradient or
  abstract map-pattern background is a safer default than an unlicensed photo)
- Large heading, e.g. "Find your place in Dublin" (or similar — something that reflects
  TerraPulse's actual positioning, not a direct copy of Zillow's copy)
- A prominent search bar, centered, matching the reference image's style: large
  rounded input, placeholder text like "Enter an area, e.g. Dublin 8, Ranelagh...",
  with a search icon/button
- **AI Assistant entry point** next to/near the search bar (see Section 3) — a
  secondary button or icon button positioned adjacent to the search bar, visually
  related to but distinct from the plain search action
- Below the hero: a few supporting sections — this can be simple, e.g. "Browse by
  area" with a handful of area cards (pull real area names from `/v1/areas`, do not
  hardcode placeholder area names), or "How TerraPulse works" with 3 short feature
  callouts (price prediction, safety scores, AI-verified livability signals) — keep
  this section light, 1-2 sections is enough, this is not the main event
- Submitting the search bar navigates to `/search?location=<value>` and the existing
  SearchPage reads that query param to initialise its view

---

## 3. AI Assistant entry points (placeholder/UI only in this phase)

Add TWO visual entry points for an AI assistant. **Neither needs to be functionally
wired to a real LLM in this phase** — build the UI shell, a basic open/close
interaction, and a static or canned response, and flag clearly that real integration
(connecting to the agent layer's LLM client) is a follow-up phase, not this one.

### 3a. Inline assistant button near the search bar (home page + search page header)
- A distinct button/icon (e.g. sparkle icon) labeled something like "Ask AI" or "AI
  Search" positioned next to the main search input on both the home page hero and the
  `SearchHeader` on the results page
- Clicking it can either expand an inline input ("Try: 'safe areas under €400k near
  transport'") or open the chat widget from 3b — pick whichever is simpler to implement
  cleanly, tell me which you chose

### 3b. Floating chat widget (bottom-right, persistent across pages)
```
frontend/src/components/ai-assistant/
├── ChatWidgetButton.tsx     # floating circular button, bottom-right, fixed position,
│                              #   brand-coloured, icon (chat bubble or sparkle),
│                              #   subtle shadow, hover scale/lift effect
├── ChatWidgetPanel.tsx       # expands on click — a chat panel (400px wide,
│                              #   ~500-600px tall, anchored bottom-right), with a
│                              #   header ("TerraPulse Assistant"), a scrollable
│                              #   message area, and an input box at the bottom
├── ChatMessage.tsx            # individual message bubble, styled differently for
│                              #   user vs. assistant messages
└── useChatWidget.ts            # local state only in this phase — open/closed,
                                 #   message list held in React state, NOT persisted,
                                 #   NOT connected to a real backend/LLM endpoint yet
```
- On open, show one canned assistant message, e.g. "Hi! I can help you find areas that
  match what you're looking for. (AI search coming soon — for now, try the filters on
  the search page!)" — be honest in the placeholder copy that this is not fully live
  yet, don't fake a working feature
- If the user types and sends a message, respond with a second canned message
  acknowledging input but stating this is a preview — do not attempt real intent
  parsing or connect to any LLM endpoint in this phase
- This is explicitly scaffolding for a future phase where this widget gets wired to a
  real endpoint (likely reusing patterns from the `agents_layer` LLM client) — build the
  UI shell well since it will be reused, but do not build fake "AI" logic that pretends
  to be smarter than it is

---

## 4. Colour and visual system — apply it properly this time

If `theme.ts` (or Tailwind config) from the last polish phase exists, extend it; if it
doesn't exist yet or wasn't fully applied, build/complete it now:

- **Primary brand colour**: pick one (e.g. a strong indigo/blue or teal — something
  distinct from Zillow's blue so TerraPulse doesn't read as a copy) and use it
  consistently for: the "TerraPulse" wordmark accent, primary buttons, active nav state,
  the AI assistant button, selected-card highlight, and link colours
- **Score colours**: Safety/Affordability/Livability numbers should have colour
  coding based on value (e.g. green for high scores, amber for mid, red for low) —
  check if this exists currently; from the screenshots the score numbers appear plain
  black regardless of value, which is a missed opportunity for at-a-glance scanning
- **Review flag colour**: keep amber/warning, but ensure it's pulled from the same
  palette definition, not a one-off value
- **Background/surface hierarchy**: page background, card background, and header
  background should be subtly distinct (e.g. very light grey page background, white
  cards) rather than everything being flat white, which currently makes the UI feel
  slightly flat
- Apply this system across HomePage, SearchPage, property cards, and the new AI
  assistant components — consistency across old and new components is the actual goal
  of this section, not just making new components pretty

---

## 5. Navigation tabs — make them functional where reasonable

The header nav ("For Sale", "Areas", "Insights") currently exists visually but isn't
functional per your report. For this phase:
- "For Sale" → routes to `/search` (this is real and easy, do it)
- "Areas" → can route to a simple new page listing all areas from `/v1/areas` as cards
  (name, area_type, maybe average price if easily available) — this is a genuinely
  useful, low-effort real page, build it if time allows
- "Insights" → placeholder is fine for this phase, can show a simple "Coming soon" state
  rather than being a dead link with no feedback — do not fully build this out yet
- "Sign in" → remains a visual-only placeholder, no auth logic (unchanged from before)

---

## 6. What "done" looks like for this phase

- [ ] Root cause of the Google Maps API key issue identified and reported; either fixed
      with a real key, or (more likely, given Phase 6) confirmed that Leaflet is the
      correct implementation and any leftover Google Maps code/dependency is removed
- [ ] New `/` home page exists with hero, search bar, AI assistant entry point, and at
      least one supporting section using real area data
- [ ] Searching from the home page navigates to `/search` with the query reflected
- [ ] Floating chat widget button appears bottom-right on all pages, opens/closes a
      chat panel, shows canned responses, clearly labeled as a preview — no fake "AI"
      claims
- [ ] Inline "Ask AI" entry point exists near the main search bar
- [ ] A real, applied colour system exists — score numbers are colour-coded by value,
      brand colour is used consistently, background/surface hierarchy is visible
- [ ] "For Sale" nav tab is functional; "Areas" tab is functional if time allows,
      otherwise clearly placeholder; "Insights" shows a "coming soon" state rather than
      doing nothing
- [ ] No backend/data-fetching/filter logic changes beyond what's explicitly listed
      above (Maps fix, and the new `/v1/areas`-backed Areas page if built)

---

## 7. Working agreement

- Fix and report on the Maps API issue before starting any new visual work — this is
  the one item in this phase that might reveal a real functional bug, not just polish.
- Do not connect the AI assistant to a real LLM endpoint in this phase — canned/preview
  responses only, clearly labeled as such. Real integration is a future phase.
- Do not build real authentication.
- If adding the home page reveals routing conflicts with the existing single-page setup
  (e.g. if `SearchPage` currently assumes it's mounted at `/`), tell me before making
  structural routing changes beyond adding the new route.
- Pick a distinct brand colour rather than closely copying Zillow's blue — tell me what
  you chose.