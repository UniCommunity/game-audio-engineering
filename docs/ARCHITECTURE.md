# Architecture

Gameplay posts named events. Unity/Unreal translate them. The audio engine mixes and spatializes. The dynamic mixer rebalances every block. Broadcast is a second sum for streams.

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

Sidechain game + crowd to commentary. Player mix does not include commentary unless opted in. Crowd live input is shared state: player mix uses the dynamic balancer; broadcast uses `mix_broadcast`.

## Tests

Latency p95 < 40 ms. Broadcast clarity ≥ 6 dB. Left/right energy matches source azimuth. VO and `critical` voices are never stolen. Ambience gain falls with intensity. Game gain floor ≥ 0.45 under loud crowd.
