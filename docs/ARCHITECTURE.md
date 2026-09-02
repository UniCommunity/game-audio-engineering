# Architecture

Gameplay posts named events. Unity/Unreal translate them. The audio engine mixes and spatializes. The dynamic mixer rebalances every block. Broadcast is a second sum for streams.

## Game Audio Middleware (diagram)

[![Game Audio Middleware — Authoring → Runtime → Show](assets/middleware_overview_thumb.png)](assets/middleware_overview_v3.svg)

Alt text: "Game audio middleware flow showing Soundtrack Editor → Audio Banks & Metadata → Platform Cook → Audio Engine → Game Application → Player; separate Broadcast/Show pipeline consumes stems and telemetry. Highlights Live Connect (preview-only) and timecode/NTP hints."

Figure: Game Audio Middleware — Authoring, cook, runtime, and show consumption. This diagram focuses on the in‑game middleware lifecycle (authoring → cook/build → runtime) and explicitly separates the Broadcast/Show pipeline (see docs/PRODUCTION_GUIDE.md for broadcast ingestion details and docs/CONTRACT.schema.json for the machine‑readable stems + parameters contract).

Long description / mapping: see the "Assets mapping" table below which maps each diagram box to repo paths (fmod_project/, data/events.json, python_oracle/, engine_integrations/, etc.).

## Audio Engine

Modules: event graph, voices, spatializer (distance + pan + ITD), buses, snapshots, soundscape director, **dynamic mixer**, limiter.

Buses: UI, SFX, Dialogue, Music, Ambience, Crowd, Commentary → DynamicMixer → Master → player_out and broadcast_send.

Game thread posts Play/Stop/SetRtpc/SetListener/SetSnapshot/IngestCrowdMic/SetDevice. Audio thread renders 256-frame blocks at 48 kHz.

## Dynamic mixer

`engine/dynamic_mixer.py` consumes:

- event priority tags from `data/events.json`
- `intensity` RTPC (scene energy)
- live crowd-mic RMS
- output device class (headset / pa / laptop)

It emits per-block gains for ambience, music, crowd, and game plus an AdaptiveEQ tilt and sidechain reduction. See [DYNAMIC_MIXING.md](DYNAMIC_MIXING.md).

## Integration

Same contract everywhere:

- Post(eventId, options)
- SetRtpc(name, value)
- SetSnapshot(name, fadeMs)
- SetListener(position, forward, up)
- IngestCrowdMic(rms)
- SetDevice(name)

Unity: `AudioApi` + `AudioEventBridge`.
Unreal: `UAudioEventSubsystem` + Blueprint `Post Audio Event`.

## Broadcast

Sidechain game + crowd to commentary. Player mix does not include commentary unless opted in. Crowd live input is shared state: player mix uses the dynamic balancer; broadcast uses `mix_broadcast` for dedicated stems and sidechain settings. The contract to broadcast is labeled in the diagram as: "stems + params (contract v1.x)" and is specified in `docs/CONTRACT.schema.json`.

## Tests

Latency p95 < 40 ms. Broadcast clarity ≥ 6 dB. Left/right energy matches source azimuth. VO and `critical` voices are never stolen. Ambience gain falls with intensity. Game gain floor ≥ 0.45 u.
