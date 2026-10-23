# ADR-038: The realtime plane is standalone, ephemeral, and boundary-strict — Bun-native WebSocket transport outside the serverless request plane, the identity law reused at the upgrade, and primitives that never decide

**Status: PROPOSED** (filed 2026-10-24 with the build opening of record already
LANDED — v2 PR #340, merge `684d9d8f994d61c6e4367a75068c26d3df501d25`, base
`69a4d21b1c`, head `c5b3b1d8f8`; operator words of record: initiation trace
`1a169faf8411d2cd` = "Initiate a real-time infrastructure project", build
opening trace `1a16a048c1b94319` = "Proceed"). The implementation is the
decision's working evidence; **the ACCEPT word stays the operator's** (the
ADR-036 precedent — this ADR does not self-accept). Until ACCEPT, this file is
the design posture of record for the F-188 line and its consumers.

## Context

The operator ruling (2026-10-23, trace `1a1693693b033a2d`) gated every
matchmaking/bracket/leaderboard surface on two arms: ADR-036 accepted (LIFTED,
trace `1a169835f503b151`) and realtime infrastructure of record. The F-186
descope flip (trace `1a169e8c0e52bebd`) parked the vs-classmate territory
behind those gates with the descope terms on the F-186 row notes, and the
initiation word (trace `1a169faf8411d2cd`) filed the gate-2 project of record
as **F-188** (tracker PR #48, ledger merge `6f20edd164`). The build opening
("Proceed", trace `1a16a048c1b94319`) mandated: transport choice, state
posture, prereg Q-battery, build PR.

Two hard constraints shaped the decision:

1. **The deployment reality of record:** `apps/api`'s entry is a Vercel
   serverless function (`apps/api/src/index.ts` default export = the fetch
   handler). A serverless function cannot hold a persistent bidirectional
   connection — the transport CANNOT live in the request plane.
2. **The filed posture of record (F-188 notes):** battle settlement stays
   computed-at-read never persisted (ADR-031 posture), zero gradebook surface,
   ADR-036's accepted on-the-wire k=5 distinct-learner rule governs any
   class-level surfacing the consumers build, and the line is INFRASTRUCTURE
   ONLY — nothing matchmaking-, bracket-, or leaderboard-shaped ships under it
   (the ruling's standing disclosure survives the initiation and the build).

## The decision

Four commitments, pinned by the prereg `syllabai-v2/docs/F188-REALTIME-PLAN.md`
(laws R1..R10, battery Q1..Q10 — committed WITH the implementation):

**1. The transport is a standalone long-lived plane (R1).** Bun-native
WebSocket on its own `Bun.serve` (`apps/api/src/realtime/server.ts`, path
`/realtime`, `REALTIME_PORT` default 8081), deliberately NOT mounted in the
Vercel entry (no index.ts touch, no double-bind — that file's own warning
stands). Run local: `bun run dev:realtime`. **Disclosed:** the production
hosting decision for the long-lived process is the operator's (any Bun-capable
box); the plane ships runnable of record, and the production latency p95
receipt is the deployed plane's own measurement. Rejected: a managed realtime
provider (an external dependency the project never adjudicated) and an
SSE/polling emulation (not the "persistent bidirectional transport" the row of
record names).

**2. The state posture is ephemeral, in-memory, process-local (R3).** Presence,
rooms, queues, and pending ghost envelopes (TTL 600 s, 64-per-target cap, oldest
evicted) live in memory and die with the process. Zero database persistence for
realtime state — the plane's ONLY database use is the identity revocation lookup
at the upgrade (the identity plane, not realtime state). No gradebook surface;
settlement untouched and still computed-at-read over the drill's own immutable
rows (ADR-031). **Disclosed:** a restart drops presence/rooms/queues and
undelivered envelopes — durability needs are consumer-line territory.

**3. The primitives never decide (R4).** Five families only: transport;
presence (userId + counts, identity-minimal); rooms (opaque string ids, join/
leave/broadcast, cap 32); a queue (a dumb FIFO — `take(n)` returns the n oldest
ids and removes them: a data structure, not a pairing verdict); and
store-and-forward envelopes (opaque payloads relayed byte-identical, sender
server-stamped, never client-claimed). No pairing, no rating, no eligibility,
no scoring, no bracket logic, no leaderboard anywhere in the module — the Q8
leakage census walks every emitted frame against a forbidden-field census and
the Q8b import census pins the file-level law (`protocol.ts` + `state.ts`
import nothing but `zod` + `./protocol`; `server.ts` imports the identity law
only). Consumers wrap authority laws around their own queue/room naming and
their own surfacing; any class-level surfacing they build is ADR-036 k=5
governed.

**4. The identity law is reused verbatim at the upgrade (R2).**
`createJwtAuthenticator` (JwtService parse + the fail-closed revocation check:
unknown user, disabled account, stale/null `ver` all reject) — no socket
resources on failure, Boot-shaped 401. `?bearer=` query is the disclosed
browser-compat leg (browsers cannot set headers on WebSocket). Caps of record
(frame 64 KiB / envelope 16 KiB / room 32 / queue 256 / pending 64 / burst 30/s
ping-exempt / stale sweep 90 s / hello window 10 s) are fail-closed and
battery-pinned.

## The build of record

`SyllabAI/syllabai-v2` PR #340 (branch `f188/realtime-plane-r0`, head
`c5b3b1d8f8`, base `69a4d21b1c`), merged as `684d9d8f994d61c6e4367a75068c26d3df501d25`.
Files: `docs/F188-REALTIME-PLAN.md`, `apps/api/src/realtime/{protocol,state,server}.ts`,
`apps/api/test/realtime/{state,wire}.test.ts`,
`.syllabai/receipts/F188-REALTIME/f188-realtime-build-run-001-r0.json`,
`apps/api/package.json` (the one existing-file touch: the `dev:realtime`
script). `index.ts`/hub/contracts/db untouched; zero new dependencies.

Battery run-001 of record: typecheck GREEN; realtime battery 34/34 (7,100
expect calls) — Q6's 500-connection/125-room zero-cross-talk leg, Q7's loopback
echo p50 5.05 ms / p95 5.39 ms over 200 pings (the smoke bound; production p95
is the deployed plane's own receipt), Q8's full-scenario leakage census, Q9's
burst-then-close leg, Q10's frozen-clock determinism. **Upstream disclosure of
record (the diff-only-red merge judgment):** v2 main's verify lane was already
red at base with exactly one test (`cie-phase4 roster floors`) and the hub
lane's corpus-verify gate was already red at base; the PR's Test failure set
equaled that base set and both red steps matched the base's own — golden
selftest, retrieval eval, and the zero-core census gate ran GREEN (locally
where CI had skipped them behind the upstream red). Zero failures attributable
to the realtime lane; the upstream reds are not this lane's content to fix.

## Consequences

- The realtime-infra arm of the matchmaking/brackets gate moves from PROJECTED
  (F-188 filed) to **BUILT (primitives landed)** — the arm lifts when the plane
  SERVES in a deployment of record (the operator's hosting decision + a serving
  receipt). Then the descoped F-186 territory (descope terms trace
  `1a169e8c0e52bebd`, place-of-record on the F-186 row notes) files its own
  consumer line(s) against these primitives — live matchmaking on the queue
  primitive, async ghost opponents on the envelope primitive, class brackets on
  the consumers' own filings.
- The ACCEPT word on THIS ADR stays the operator's. A REJECT would pull the
  plane out of `apps/api` (the module is fully fenced: three source files, two
  test files, one doc, one script line, one receipt — nothing else touched).
- The consumers inherit the disclosures, not exceptions: ephemeral state (their
  durability needs are their own lines), best-effort envelopes (their delivery
  guarantees are their own laws), and the identity-minimal wire (their
  surfacing stays ADR-036 k=5 governed).
