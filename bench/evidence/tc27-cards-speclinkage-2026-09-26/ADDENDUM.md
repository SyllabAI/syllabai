# ADDENDUM — 2026-09-26T13:30Z: Gemini key restored, all 298 cards embedded

The operator supplied three candidate keys (`AQ.Ab8RN6…` format). Probe verdicts
(`gemini_key_probe.json`, `key_swap_record.json`):

| key (masked) | sandbox probe | from Render (us-east-2) | disposition |
|---|---|---|---|
| `AQ.Ab8RN6I...iQNA` | 400 "User location is not supported" | **WORKS** — search restored (5/5 queries, 5 hits each, 1.5-1.7s) | **LIVE on prod** (env swap + explicit deploy, was `dep-darq…` live 13:0xZ) |
| `AQ.Ab8RN6I...oasw` | 400 "User location is not supported" | untested from prod | spare (geo-block is a sandbox artifact, not a key fault) |
| `AQ.Ab8RN6K...02sA` | 403 "Your project has been denied access" | n/a | **DEAD — same project denial as the key this replaced** (it was itself live on Render before the swap) |

Note: the pre-swap live key on Render WAS the denied `...02sA` — the 500 outage root cause.

At-volume limit check for the live key: **298 sequential embeds (~30 RPM sustained, 9.4 min) + 10+
query embeddings — zero 429s, zero errors** (embed_state.jsonl, all `ok:true`, model
`gemini-embedding-001`, 768-dim). No meaningful rate limit observed at this load.

T-C27 remaining bar update: the embed blocker is CLEARED (298/298 card chunks embedded).
What remains for DONE: the recorded T-C13 bench (snap-003 re-freeze + gold-v2 regeneration,
operator-held) at the serving flip — i.e., when the cards (SUGGESTED) get teacher-validated
or otherwise enter the serving set.
