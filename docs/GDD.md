# Game Design Document — Adaptive Audio System

**Project:** Game Audio Engineering Kit  
**Status:** v0.2 reference design (dynamic mixing)

## 1. Vision

Players locate and read the game through sound. Stream viewers hear a different mix: commentary first, crowd second, game SFX ducked. Designers trigger **events**, never raw files. The mix itself is alive: it follows player actions, scene intensity, and the arena.

Targets:
- Trigger-to-DAC ≤ 40 ms
- Direction of 3D events is clear on headphones
- Music and weather yield to footsteps, reloads, and dialogue
- Live crowd is present without burying competitive cues
- OBS can take a broadcast stem without tapping the player master

## 2. Pillars

1. Event-driven (`sfx.footstep`, not `step_03.wav`)
2. Bus-first mixing
3. Player mix ≠ stream mix
4. Dynamic mixing from action + environment + crowd
5. Quality is tested (latency, LUFS, position, heat, crowd floor)
6. Unity and Unreal share one event contract

## 3. Layers

UI (2D), SFX (spatial if world), Dialogue (ducks music), Music, Ambience, Crowd (broadcast-heavy).

Soundscapes are named beds + RTPCs (`scape.match.time_pressure`). Intensity 0–1 drives music density, ambience level, and the dynamic mixer.

Priority tags on events: `critical`, `high`, `medium`, `low`, `bed`.

## 4. Event catalogue

See `data/events.json`. Naming: `domain.object.action`.

Competitive defaults:
- `sfx.footstep`, `sfx.reload` → critical
- `sfx.gunfire`, `sfx.spell.cast` → high
- `ambience.rain`, `ambience.wind` → low
- `music.state.explore`, `ambience.hall` → bed

## 5. Mix targets

- Player master true peak ≤ −1 dBTP
- Broadcast commentary on top; game bed extra −4 dB and sidechained
- Snapshots: Normal, Check, Victory, Defeat, Pause, BroadcastFocus, ArenaHot
- Game-gain floor under live crowd ≥ 0.45 linear
- Ambience never fully muted (floor 0.18) so the space still exists

## 6. Spatial rules

One listener. Inverse-square attenuation. Equal-power pan + ITD on headphones. Do not spatialize UI, music, or commentary.

## 7. Accessibility

Mono fold-down. Separate sliders. Captions for VO. Optional crowd mute. Device EQ presets for headset / PA / laptop.

## 8. Acceptance

Covered by `tests/test_audio.py` and `tests/test_dynamic_mix.py`.
