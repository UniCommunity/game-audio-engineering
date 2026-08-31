# Production Guide — Game ↔ Show Audio

This production guide explains how to operate, ingest, and troubleshoot game audio in live esports shows and venue productions. It is the operational complement to the canonical machine spec (docs/CONTRACT.schema.json) and is written for broadcast engineers, producers, and operations teams integrating the game output into a live show.

Table of contents
- Transport mapping (recommended transports & URIs)
- Time synchronization & latency handling
- Stem & parameter (telemetry) ingestion patterns
- Preflight checklist (rehearsal smoke tests)
- Live runbook (day-of steps and fallbacks)
- Troubleshooting & incident runbook
- Security & operational notes
- Example payloads and command snippets
- Contacts & roles

---

## Transport mapping (recommended)

Do not bake a single transport into the contract. Use the following recommended mapping table as actionable defaults for common stem purposes.

- Broadcast / Show multichannel stems (low-latency, multi-channel):
  - Recommended: Dante / AES67 / MADI (physical/network audio), or NDI for video+audio workflows
  - URI examples:
    - dante://10.0.0.12:10024/channel/1
    - aes67://10.0.0.20/stream1
    - ndi://host.domain/streamName
- Remote contribution / cloud transport:
  - Recommended: SRT (secure reliable transport) or RTP/SRTP for lower-latency contribution
  - URI example:
    - srt://ingest.example.net:1234?mode=caller
- Telemetry & parameters (small, frequent updates):
  - Recommended: WebSocket, UDP/TS (fast datagram), or a lightweight REST webhook for lower-rate updates
  - Example WebSocket: wss://telemetry.example.net/game/ingest
- Local IPC / debug:
  - Recommended: local Unix domain socket, named pipe, or loopback HTTP for local debugging

Notes:
- Provide a `transport_hint` field in the contract so ingest systems know the intended route.
- Where possible, prefer transports that support metadata/ancillary data (NDI) or dedicated multicast streams for linear show feeds (AES67).

---

## Time synchronization & latency handling

Syncing audio to video and other show events is critical. Use the following patterns:

1. Time references
   - Include both `timestamp` (ISO 8601 UTC) and an optional `game_time` or `frame_id` in the contract payload.
   - If available, include SMPTE timecode or a shared NTP/PTP reference for show infrastructure.

2. Latency hints & jitter
   - Provide `latency_budget_ms` and `transport_hint` in the contract root.
   - Ingesters should apply a jitter buffer and optional `latency_offset_ms` to align audio to the show timeline.

3. Recommended sync flow
   - Production: ensure all devices use the same NTP/PTP domain.
   - Ingest: compute difference between `timestamp` and local receive time; if difference > expected budget, flag for diagnostics.
   - For remote feeds, prefer a slightly larger jitter buffer and log the `latency_estimate_ms` in ingest telemetry.

4. Example sync fields
```json
{
  "timestamp": "2026-08-31T15:22:01.234Z",
  "game_time": "00:12:34.567",
  "latency_budget_ms": 300
}
```

---

## Stem & parameter ingestion patterns

1. Stem types & routing
   - Provide separate stems for major groups: game (core game audio), commentary (caster mics), crowd (arena mic array), music, and SFX groups if needed.
   - Ensure stems intended for broadcast are exported as dedicated channels (2-ch stereo or multichannel bus depending on the show).

2. Parameter telemetry
   - Parameters (middleware-neutral) include intensity, crowd_volume, player_health, and commentary_active.
   - Telemetry should be update-rate limited (e.g., 10–60 Hz) or event-driven to avoid overloading networks.

3. Object-based & spatial metadata
   - If you provide object-based audio (Ambisonics or object streams), include `spatial_metadata` with position/orientation and format descriptor.

4. File / data URIs
   - Use transport-specific URIs in `stems[].path` (see Transport mapping). For file handoff workflows (non-real-time), use signed HTTPS URLs with expiry.

---

## Preflight checklist (rehearsal smoke tests)

Run this checklist before a show. Record results in a runbook and tag bank/build versions.

1. Bank & build verification
   - FMOD/Wwise banks exist and match `integration/fmod/fmod_events.json` mapping.
   - Game build uses the expected banks and logs bank version on startup.

2. Contract & schema validation
   - Validate example contract payloads against docs/CONTRACT.schema.json.
   - Run tests:
```bash
python3 tests/test_audio.py
python3 tests/test_dynamic_mix.py
python3 -m pytest tests/test_contract_validation.py
```

3. Transport & routing
   - Validate stem routing:
     - Does the broadcast desk receive the expected Dante/AES67/NDI channels?
     - Are sample rates (recommended 48 kHz) and bit depth consistent?
   - Verify telemetry connectivity (WebSocket / UDP) and check update rates.

4. Sync & delay
   - Measure time offset between game `timestamp` and ingest `received_time`.
   - Adjust `latency_offset_ms` at ingest to align audio to video or show timeline.

5. Loudness & clarity tests
   - Run LUFS measurement on broadcast feed (target -14 LUFS for streaming, -24 LUFS for TV where applicable).
   - Run clarity test: ensure broadcast clarity_db ≥ 6 dB for commentary over game feed.

6. Fallbacks
   - Ensure backup feed exists (e.g., direct NDI of broadcaster’s desk, or a local feed).
   - Document and test manual mute/unmute procedures for problematic stems.

---

## Live runbook (day-of show steps)

1. Pre-show (90–15 minutes)
   - Confirm versions: game build, FMOD/Wwise banks, and contract schema.
   - Start ingest services and verify stem reception on broadcast desk.
   - Run LUFS and clarity tests; record baseline levels.

2. Pre-match (15–5 minutes)
   - Start game run with test stimuli (synth stems) and verify telemetry.
   - Confirm crowd mic gating thresholds and noise gating behavior.
   - Confirm that EchoForge/AudioApi RTPC writes are visible on ingest telemetry.

3. Match start
   - Monitor `clarity_db`, LUFS, and `cue_rms` telemetry on a dashboard.
   - Keep a manual mute switch mapped for each stem on the console.

4. Match live operation
   - If the broadcast engineer needs more articulation of cues, use RTPC telemetry to automate ducking or trigger snapshots.
   - If latency drift occurs, switch to backup feed or apply ingest `latency_offset_ms`.

5. Post-match
   - Record logs: contract payloads, ingest timestamps, clarity/LUFS measurements, and bank versions.
   - Tag the game build and banks that were used.

---

## Troubleshooting & incident runbook

Common symptoms and first actions:

- Symptom: Crowd buries caster or player cues
  - Check: Is the broadcast using dedicated commentary stem or master mix?
  - Action: Route commentary-only stem to stream; increase commentary gain OR reduce crowd feed on stream; check `crowd_volume` RTPC.

- Symptom: Audio desync with video
  - Check: Compare `timestamp` in payload to ingest `received_time`.
  - Action: Apply `latency_offset_ms` at ingest. Verify PTP/NTP sync across devices.

- Symptom: Gate chattering on crowd mic
  - Check: Hysteresis settings (noiseThreshold + noiseHysteresis) in EchoForge or ingestion processing.
  - Action: Increase hysteresis or smoothing; if live, use manual muting fallback.

- Symptom: Missing events/RTPC values
  - Check: Are AudioApi posts being emitted by the client? Check logs for AudioApi.Ingest calls.
  - Action: If missing, switch to synthetic test stems and isolate whether the game or transport is the issue.

- Symptom: Clarity_db below threshold
  - Check: Verify broadcast is consuming the broadcast stem and sidechain compressor settings.
  - Action: Temporarily reduce game stem gain on broadcast desk; record observations and revert after fix.

Fast reproduction flow (for engineers)
1. Reproduce in Python oracle:
   - Use engine/example_synth.py to generate stems.
   - Run engine.DynamicMixer and verify last_report values.
2. Check runtime logs:
   - EchoForge/AudioApi log lines for RTPC writes and event posts.
3. Validate transport:
   - Ensure stems are routed and test ingest with `ffmpeg` / `ndi-test` / Dante Controller.

---

## Security & operational notes

- Never embed secrets or PII in contract metadata. Use short-lived signed URLs for file handoff.
- Use secure transports where possible (SRT with encryption, SRTP). For control channels (telemetry), prefer WebSocket over TLS (wss://).
- Limit who can post to ingest endpoints using API keys and IP allowlists. Rotate keys per-event as appropriate.
- Log and truncate telemetry payloads; do not store full audio stems unless required for postmortem.

---

## Example payloads & snippets

Minimal contract example (repeated for convenience):
```json
{
  "version": "1.0.0",
  "timestamp": "2026-08-31T15:22:01.234Z",
  "session_id": "match-2026-finals-game3",
  "stems": {
    "game": {
      "path": "dante://10.0.0.12:10024/channel/1",
      "channels": 2,
      "sample_rate": 48000,
      "purpose": "game"
    }
  },
  "parameters": {
    "intensity": {
      "value": 0.72,
      "unit": "normalized"
    }
  },
  "latency_budget_ms": 300
}
```

Schema validation command (example)
```bash
# validate example.json against CONTRACT.schema.json (using ajv or other validator)
ajv validate -s docs/CONTRACT.schema.json -d examples/example_contract.json
```

CI snippet (suggested)
- Validate schema → run Python oracle tests → run contract validation
```yaml
# pseudo-workflow step
- run: ajv validate -s docs/CONTRACT.schema.json -d examples/example_contract.json
- run: python3 tests/test_audio.py
- run: python3 tests/test_dynamic_mix.py
- run: python3 -m pytest tests/test_contract_validation.py
```

---

## Contacts & roles (example)

- Audio Designer: owns FMOD/Wwise banks and event definitions
- Audio Programmer: owns the AudioApi and runtime hooks (EchoForge)
- Broadcast Engineer: owns ingest, console routing, and show-level loudness
- QA/Test Engineer: owns CI tests and regression thresholds
- Producer/Ops: coordinates rehearsals and bank/build versions

---

## Appendix — Preflight quick checklist (single-page)

- Banks: verified & versioned
- Build: correct build deployed and logs bank version
- Schema: example payloads validate
- Transports: stems routed and active on desk
- Time: NTP/PTP sync confirmed
- Metrics: LUFS baseline & clarity_db baseline recorded
- Fallbacks: backup streams and manual mute mapped

---

End of production guide draft.
