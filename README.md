# Game Audio Engineering Kit

Sound engineering stack for game development and esports: named events, adaptive mixing, FMOD on Unity / Unreal / Godot, a separate broadcast stem, and tests that treat clarity as a regression.

**summary:** [docs/SUMMARY.md](docs/SUMMARY.md)

## Layers

1. **Audio Engine** — mixing, spatialization, dynamic soundscapes
2. **Dynamic Mixer** — player-action priority, environment scaling, arena crowd, adaptive EQ
3. **EchoForge (Unity)** — live crowd-mic RMS, noise gate, in-scene adaptive mix
4. **FMOD Adaptive Mixing** — Studio events, parameters, snapshots, DSP (Unity, Unreal, Godot)
5. **Integration Layer** — plugins that post *events*, not files
6. **Broadcast Layer** — commentary + crowd + ducked game for OBS
7. **Testing Suite** — latency, position, broadcast clarity, priority voices

## Docs

- [docs/SUMMARY.md](docs/SUMMARY.md) — stack overview mapped to this repo
- [docs/GDD.md](docs/GDD.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DYNAMIC_MIXING.md](docs/DYNAMIC_MIXING.md)
- [docs/FMOD_ADAPTIVE_MIXING.md](docs/FMOD_ADAPTIVE_MIXING.md)
- [docs/FMOD_GODOT.md](docs/FMOD_GODOT.md)

## FMOD

```csharp
FmodAudioManager.Instance.InitializeFmod();
FmodAudioManager.Instance.SetIntensity(0.7f);
FmodAudioManager.Instance.Post("sfx.gunfire", muzzle);
```

```gdscript
FmodAudio.initialize_fmod()
FmodAudio.set_intensity(0.7)
FmodAudio.ingest_crowd_mic(0.55)
FmodAudio.set_snapshot("commentary")
```

Managers: `integration/fmod/unity`, `integration/fmod/unreal`, `integration/fmod/godot`.

## Tests

```bash
python3 tests/test_audio.py
python3 tests/test_dynamic_mix.py
```

Repo: https://github.com/UniCommunity/game-audio-engineering

---

## Maintainer note — architecture clarification and recommended changes


- The Fusion Problem: Interactive audio (in-engine, low latency, event-driven) and broadcast audio (linear, production-mixed, often hardware-assisted) have different control surfaces, latency expectations, and toolchains. Treating them as a single undifferentiated layer risks leaking implementation details between teams and encourages fragile coupling (e.g., trying to run a broadcast console inside a game engine).
- Clear contracts (event lists, RTPCs, stems) enable independent authoring and testing: designers can author events and parameters for the in-game experience; broadcast engineers can consume stems and RTPC-driven metadata to build a show mix.

EchoForge naming and scope
- "EchoForge" reads as a project-specific name (and is implemented here as a Unity runtime hook). It is not a standard middleware name like FMOD or Wwise. Keep EchoForge in the repo as an example runtime hook (see `src/audio_engine/Unity/EchoForgeAudioEngine.cs`), but document it as a local implementation example rather than an alternative middleware. For external-facing documentation, prefer neutral terms such as "Engine runtime hook" or "Unity adaptive mixer example" so readers do not assume a separate commercial product.

Dual-Pipeline architecture 
1) Interactive Gameplay Audio Pipeline (The Game)
- Integration & API Layer: engine-specific scripts/plugins that post event IDs and RTPCs (Unity C#, Unreal, Godot GDScript). These should not embed broadcast-specific routing.
- Audio Engine & Middleware: FMOD/Wwise handling events, RTPC-driven DSP, snapshots, and internal routing.
- Spatialization & Propagation: HRTF and occlusion (Oculus Spatializer, SteamAudio, Project Acoustics) used for in-game positional accuracy.
- Dynamic Gameplay Mixer: in-engine adaptive routing and priority logic (the behavior implemented in `engine/dynamic_mixer.py`). This mixer keeps critical gameplay audio clear and responsive.

2) Esports Broadcast & Venue Pipeline (The Show)
- Venue & Crowds Processing: external hardware/software (mic arrays, PA processing) for live crowd feeds with gating, noise reduction and anti-feedback.
- Broadcast Mixer: OBS / vMix / production consoles for blending game stems with live commentary, remote contributions and studio feeds, applying loudness control and show-style processing.
- Comms & Matrix Layer: low-latency intercom and comms (Clear-Com, Riedel) for production and player communications that must remain isolated from broadcast audience feeds.

3) Shared Integration & Quality Layer
- Shared Integration Layer (contract): an explicit contract (events.json + fmod_events.json) that defines event names, parameters and snapshot exposures which both pipelines use.
- Unified Quality & Testing Suite: signal-level tests (latency, clarity_db, LUFS compliance), automated regression thresholds and per-block mixer reports. These live in `tests/` and are exercised by the Python oracle (`engine/audio_engine.py`).

Practical next steps for the repo
- Mark EchoForge as an example Unity runtime hook in the README and docs (link to `src/audio_engine/Unity/EchoForgeAudioEngine.cs`).
- Add a short "How the pipelines connect" section that explains the expected artifact the game emits for broadcast (stereo stems: game, crowd, commentary + RTPC metadata) and how broadcast ingestion should treat them.
- Add a short compliance note pointing to LUFS/LKFS monitoring and target levels for streaming vs. TV.

References and further reading
- FMOD Studio docs / Wwise documentation — for middleware mapping and studio-side mixer best practices.
- Stevens & Raybould — "Principles of Game Audio" for interactive vs. linear mixing theory.
- AES papers on esports audio — for venue mic arrays, crowd processing and broadcast mixing challenges.


