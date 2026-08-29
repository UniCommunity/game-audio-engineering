# Architecture

Gameplay posts named events. Unity/Unreal translate them. The audio engine mixes and spatializes. Broadcast is a second sum for streams.

## Audio Engine

Modules: event graph, voices, spatializer (distance + pan + ITD), buses, snapshots, soundscape director, limiter.

Buses: UI, SFX, Dialogue, Music, Ambience, Crowd, Commentary → Master → player_out and broadcast_send.

Game thread posts Play/Stop/SetRtpc/SetListener/SetSnapshot. Audio thread renders 256-frame blocks at 48 kHz.

## Integration

Same contract everywhere:

- Post(eventId, options)
- SetRtpc(name, value)
- SetSnapshot(name, fadeMs)
- SetListener(position, forward, up)

Unity: `AudioApi` + `AudioEventBridge`.
Unreal: `UAudioEventSubsystem` + Blueprint `Post Audio Event`.

## Broadcast

Sidechain game + crowd to commentary. Player mix does not include commentary unless opted in.

## Tests

Latency p95 < 40 ms. Broadcast clarity ≥ 6 dB. Left/right energy matches source azimuth. VO voices are never stolen.
