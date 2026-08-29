# Game Design Document — Adaptive Audio System

**Project:** Game Audio Engineering Kit  
**Status:** v0.1 reference design

## 1. Vision

Players locate and read the game through sound. Stream viewers hear a different mix: commentary first, crowd second, game SFX ducked. Designers trigger **events**, never raw files.

Targets:
- Trigger-to-DAC ≤ 40 ms
- Direction of 3D events is clear on headphones
- Music yields to dialogue
- OBS can take a broadcast stem without tapping the player master

## 2. Pillars

1. Event-driven (`sfx.piece.capture`, not `capture_03.wav`)
2. Bus-first mixing
3. Player mix ≠ stream mix
4. Quality is tested (latency, LUFS, position)
5. Unity and Unreal share one event contract

## 3. Layers

UI (2D), SFX (spatial if world), Dialogue (ducks music), Music, Ambience, Crowd (broadcast-heavy).

Soundscapes are named beds + RTPCs (`scape.match.time_pressure`). Intensity 0–1 drives music density and crowd.

## 4. Event catalogue

See `data/events.json`. Naming: `domain.object.action`.

## 5. Mix targets

- Player master true peak ≤ −1 dBTP
- Broadcast commentary on top; game bed extra −4 dB and sidechained
- Snapshots: Normal, Check, Victory, Defeat, Pause, BroadcastFocus

## 6. Spatial rules

One listener. Inverse-square attenuation. Equal-power pan + ITD on headphones. Do not spatialize UI, music, or commentary.

## 7. Accessibility

Mono fold-down. Separate sliders. Captions for VO. Optional crowd mute.

## 8. Acceptance

Covered by `tests/test_audio.py`.
