# Game Audio Engineering Kit

Sound engineering stack for game development:

1. **Audio Engine** — mixing, spatialization, dynamic soundscapes
2. **Dynamic Mixer** — player-action priority, environment scaling, arena crowd, adaptive EQ
3. **EchoForge (Unity)** — live crowd-mic RMS, noise gate, and in-scene adaptive mix
4. **FMOD Adaptive Mixing** — Studio events, global parameters, snapshots, DSP driven by live game data
5. **Integration Layer** — Unity + Unreal plugins that post *events*, not files
6. **Broadcast Layer** — separate esports mix (commentary + crowd + ducked game)
7. **Testing Suite** — latency, clarity, positional accuracy, dynamic-mix contracts

Docs:

- [docs/GDD.md](docs/GDD.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DYNAMIC_MIXING.md](docs/DYNAMIC_MIXING.md)
- [docs/FMOD_ADAPTIVE_MIXING.md](docs/FMOD_ADAPTIVE_MIXING.md)

## Layout

```
data/events.json
engine/audio_engine.py
engine/dynamic_mixer.py
src/audio_engine/Unity/EchoForgeAudioEngine.cs
integration/fmod/fmod_events.json
integration/fmod/unity/FmodAudioManager.cs
integration/fmod/unreal/FmodAudioSubsystem.*
broadcast/broadcast_mixer.py
integration/unity/
integration/unreal/
tests/
```

The Python engine is a **reference implementation**. Production titles keep the same event ids and swap the renderer for native mixer, FMOD, or Wwise.

## Run tests

```bash
python3 tests/test_audio.py
python3 tests/test_dynamic_mix.py
```

## FMOD Adaptive Mixing

Designers author Events, Parameters, Snapshots and DSP in FMOD Studio. Programmers call a small API.

- Guide: [docs/FMOD_ADAPTIVE_MIXING.md](docs/FMOD_ADAPTIVE_MIXING.md)
- Event / parameter map: [integration/fmod/fmod_events.json](integration/fmod/fmod_events.json)
- Unity manager (includes `InitializeFmod`): [integration/fmod/unity/FmodAudioManager.cs](integration/fmod/unity/FmodAudioManager.cs)
- Unreal subsystem: [integration/fmod/unreal/FmodAudioSubsystem.h](integration/fmod/unreal/FmodAudioSubsystem.h)

```csharp
FmodAudioManager.Instance.InitializeFmod();
FmodAudioManager.Instance.SetIntensity(0.7f);
FmodAudioManager.Instance.IngestCrowdMic(0.55f);
FmodAudioManager.Instance.Post("sfx.gunfire", muzzle);
FmodAudioManager.Instance.SetSnapshot("broadcast_focus");
```

Strategy:

1. Create Events for gunfire, crowd ambience, announcer VO, footsteps, music beds.
2. Define global Parameters: `intensity`, `crowd_volume`, `player_health`, `commentary_active`.
3. Link them in Studio — music tempo vs intensity, crowd ducks commentary, snapshots own DSP.
4. Integrate the official Unity / Unreal FMOD plugin and initialize from the audio manager.

## Dynamic Mixing Module

- [engine/dynamic_mixer.py](engine/dynamic_mixer.py)
- [src/audio_engine/Unity/EchoForgeAudioEngine.cs](src/audio_engine/Unity/EchoForgeAudioEngine.cs)

EchoForge can feed `crowd_volume` / `intensity` into FMOD via `FmodAudioManager.IngestCrowdMic`.

## Broadcast

`mix_broadcast(stems)` sidechains game + crowd to commentary. Do not reuse the player master for OBS.

Repo: https://github.com/UniCommunity/game-audio-engineering
