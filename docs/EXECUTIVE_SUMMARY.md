# Executive Summary — Sound Engineering Stack for Game Development and Esports

A modern game-audio stack has to do two jobs that used to fight each other: **immersion** for players and **intelligibility** for competitors and broadcast. This kit treats those as one control problem. Gameplay posts named events. A reference mixer, EchoForge, and FMOD/Wwise-style middleware share the same ids. The player master and the esports stem are different sums.

This document elaborates the project executive summary and maps every layer onto the repository.

Related: [GDD](GDD.md) · [Architecture](ARCHITECTURE.md) · [Dynamic mixing](DYNAMIC_MIXING.md) · [FMOD](FMOD_ADAPTIVE_MIXING.md) · [FMOD + Godot](FMOD_GODOT.md)

## 1. Core audio middleware

FMOD and Wwise are renderers of a shared contract, not the contract itself.

- Catalogue: `data/events.json`
- FMOD map: `integration/fmod/fmod_events.json`
- Unity / Unreal / Godot FMOD managers under `integration/fmod/`
- Engine-agnostic API: `integration/unity/AudioApi.cs`, `integration/unreal/`
- Reference renderer: `engine/audio_engine.py`

Designers author Events, Parameters, Snapshots and DSP. Programmers post ids and write `intensity`, `crowd_volume`, `player_health`, `commentary_active`.

## 2. Adaptive mixing layer

- Event analysis and priority boost: `engine/dynamic_mixer.py`
- Critical cues (footsteps, reload, commentary) are steal-protected
- `intensity` scales ambience/music with floors so the space does not vanish
- Crowd RMS becomes `crowd_volume` with a game-gain floor (~0.45)
- Snapshots: `normal`, `arena_hot`, `broadcast_focus`, `victory`, `check`
- Unity scene hook: `src/audio_engine/Unity/EchoForgeAudioEngine.cs`

## 3. Spatial audio and calibration

Reference spatializer: inverse-square, equal-power pan, ITD. Device EQ for headset / PA / laptop. Latency budget trigger-to-peak < 40 ms (`tests/test_audio.py`). UI, music, commentary stay 2D.

## 4. Noise management

EchoForge gate with hysteresis on the arena mic. Sidechain compressors on beds. FMOD Noise Gate / Compressor / spectral sidechain authored on the Crowd/Mic bus. Game code only writes `crowd_volume`.

## 5. Voice and communication

Player mix ducks music under dialogue. Broadcast mix (`broadcast/broadcast_mixer.py`) sidechains game + crowd to commentary and reports `clarity_db` (≥ 6 dB). Do not send the player master to OBS.

## 6. Analytics and feedback

Shipped: per-block mixer report and automated latency / spatial / clarity / steal tests. Specified, not shipped: designer dashboard, perception studies, ML that writes RTPCs. Any model must set the same parameter names.

## 7. Repository and workflow

```
data/  engine/  src/audio_engine/  broadcast/  integration/  docs/  tests/
```

CI gate: `python3 tests/test_audio.py && python3 tests/test_dynamic_mix.py`.

Workflow: design Events → expose parameters → integrate runtime (Unity/Unreal/Godot) → trigger Events + Snapshots → Live Update + tests.

## Strategic value

- Players: readable cues, surviving ambience, device-matched EQ
- Esports: crowd in the room without burying the caster; dedicated broadcast stem
- Developers: one event list, three engines, a Python oracle

Repo: https://github.com/UniCommunity/game-audio-engineering
