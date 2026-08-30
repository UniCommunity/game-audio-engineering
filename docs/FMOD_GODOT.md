# FMOD Adaptive Mixing for Godot

Same catalogue as Unity/Unreal/Python. Godot talks to FMOD Studio through an autoload audio manager.

- Manager: [`integration/fmod/godot/fmod_audio_manager.gd`](../integration/fmod/godot/fmod_audio_manager.gd)
- Path map: [`integration/fmod/godot/fmod_event_map.gd`](../integration/fmod/godot/fmod_event_map.gd)
- Shared events: [`integration/fmod/fmod_events.json`](../integration/fmod/fmod_events.json)
- Goals: [`data/fmod-feature-goals.csv`](../data/fmod-feature-goals.csv)

Works with FMOD for Godot (`FMODRuntime`, `FMODStudioModule`) and utopia-rise fmod-gdextension (`Fmod` / `FmodServer`).

## Integration workflow

1. Design adaptive events in FMOD Studio.
2. Expose parameters for gameplay variables.
3. Integrate the FMOD runtime in Godot (plugin + autoload `FmodAudio`).
4. Trigger events and snapshots from game state.
5. Profile and refine with Live Update and the profiler / spectrum tools.

## Initialize FMOD in the audio manager

Autoload `fmod_audio_manager.gd` as `FmodAudio`. `initialize_fmod()` loads banks with LIVE_UPDATE, starts music/ambience/crowd beds, and caches snapshots `normal`, `combat`, `crowd`, `commentary`.

```gdscript
FmodAudio.post("sfx.gunfire", muzzle)
FmodAudio.set_intensity(0.7)
FmodAudio.ingest_crowd_mic(0.55)
FmodAudio.mix_commentary()
```

Snapshots: `set_snapshot("combat" | "crowd" | "commentary")`. DSP (noise gate, compressor, spectral sidechain) lives on the Crowd / Mic bus in Studio. Godot only writes `crowd_volume` and `commentary_active`.
