# Game Audio Engineering Kit

Sound engineering stack for game development and esports: named events, adaptive mixing, FMOD on Unity / Unreal / Godot, a separate broadcast stem, and tests that treat clarity as a regression.

**Executive summary:** [docs/EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md)

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
