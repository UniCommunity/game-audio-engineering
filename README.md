# Game Audio Engineering Kit

Sound engineering stack for game development:

1. **Audio Engine** — mixing, spatialization, dynamic soundscapes
2. **Dynamic Mixer** — player-action priority, environment scaling, arena crowd, adaptive EQ
3. **EchoForge (Unity)** — live crowd-mic RMS, noise gate, and in-scene adaptive mix
4. **FMOD Adaptive Mixing** — Studio events, parameters, snapshots, DSP (Unity, Unreal, Godot)
5. **Integration Layer** — plugins that post *events*, not files
6. **Broadcast Layer** — separate esports mix
7. **Testing Suite**

Docs:

- [docs/GDD.md](docs/GDD.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/DYNAMIC_MIXING.md](docs/DYNAMIC_MIXING.md)
- [docs/FMOD_ADAPTIVE_MIXING.md](docs/FMOD_ADAPTIVE_MIXING.md)
- [docs/FMOD_GODOT.md](docs/FMOD_GODOT.md)

## FMOD + Godot

- Guide: [docs/FMOD_GODOT.md](docs/FMOD_GODOT.md)
- Autoload manager: [integration/fmod/godot/fmod_audio_manager.gd](integration/fmod/godot/fmod_audio_manager.gd)
- Event map: [integration/fmod/godot/fmod_event_map.gd](integration/fmod/godot/fmod_event_map.gd)
- Goals table: [data/fmod-feature-goals.csv](data/fmod-feature-goals.csv)

```gdscript
FmodAudio.initialize_fmod()
FmodAudio.set_intensity(0.7)
FmodAudio.ingest_crowd_mic(0.55)
FmodAudio.post("sfx.gunfire", muzzle)
FmodAudio.set_snapshot("commentary")
```

Workflow: design Events in Studio → expose `intensity` / `crowd_volume` / `player_health` → init runtime in the Godot audio manager → trigger Events + Snapshots (`combat`, `crowd`, `commentary`) → refine with Live Update.

DSP (noise gate, compressor, spectral sidechain) is authored on the Crowd / Mic bus. Godot only writes parameters.

Unity / Unreal managers remain under `integration/fmod/unity` and `integration/fmod/unreal`.

Repo: https://github.com/UniCommunity/game-audio-engineering
