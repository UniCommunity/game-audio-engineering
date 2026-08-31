# Repository overview

## What this is
A concise, practical sound-engineering kit that unifies player-facing immersion and broadcast intelligibility for multiplayer games and esports. It provides: a Python reference audio engine and adaptive dynamic mixer (used as an oracle and test harness), engine-agnostic integration layers that post named events and RTPCs to FMOD (Unity, Unreal, Godot), and a broadcast stem/mixer so commentary and crowd can be produced without losing clarity.

### Design goals (short)
- Keep one canonical Events catalogue for designers (data/events.json) and map it to FMOD.
- Make mixing decisions deterministic and testable via a Python reference implementation.
- Provide light-weight runtime hooks for Unity/Unreal/Godot that post events (not audio files).
- Produce a dedicated broadcast stem (commentary + crowd + ducked game) for streaming/OBS.

### Stack
- **Language(s):** Python (reference engine & tests), C# (Unity managers and runtime hooks), GDScript (Godot FMOD manager), C++ (possible Unreal/native glue / FMOD native bindings)
- **Framework / runtime:** Python 3 for the oracle/tests; FMOD Studio as the audio renderer; Unity and Godot runtimes for engine integration
- **Notable libraries / systems:** FMOD Studio (events, parameters, snapshots, DSP), Unity audio API (C# AudioSource / AudioMixer integration), Godot + FMOD plugin (GDScript managers), Python standard + test harness for signal-level checks

## How it's organized
Top-level important entries (annotated):

```
data/                 # Designer-authored data: events catalogue (data/events.json) and mapping helpers
engine/               # Python reference renderer & adaptive mixer
  audio_engine.py     # Reference signal rendering + helpers
  dynamic_mixer.py    # Adaptive mixing logic (priority boost, crowd/game balance, sidechain compressors)
integration/          # Platform adapters that translate events -> FMOD posts/RTPCs/snapshots
  fmod/
    fmod_events.json  # FMOD renderer map: parameters, snapshots, and event ids used by platforms
    (godot/, unity/, unreal/)  # per-engine FMOD glue and example managers
  unity/               # Unity-side AudioApi and helpers (C#)
  unreal/              # Unreal integration pieces (C++/blueprint examples)
  godot/               # Godot FMOD manager (GDScript)
src/                  # Example engine runtime hooks (e.g. src/audio_engine/Unity/EchoForgeAudioEngine.cs)
broadcast/            # Broadcast stem logic and the broadcast mixer (broadcast/broadcast_mixer.py)
docs/                 # Design docs (SUMMARY.md, ARCHITECTURE.md, DYNAMIC_MIXING.md, FMOD_* guides)
tests/                # Automated tests (unit/integration-style tests that assert latency/clarity/ducking)
.github/               # CI/workflows
```

How it fits together (runtime shape):
- Designers edit the event catalogue in data/events.json and map those events to FMOD names in integration/fmod/fmod_events.json.
- Game runtime code (Unity/EchoForgeAudioEngine.cs, Godot FMOD manager, Unreal glue) posts event ids and sets RTPCs via a small AudioApi layer so code across engines is consistent.
- FMOD receives events/RTPCs and applies authored DSP (snapshots, compressors, noise gates). The Python reference engine (engine/audio_engine.py + engine/dynamic_mixer.py) reproduces the intended mixing behavior deterministically and serves as a test oracle.
- The broadcast mixer consumes the same stems (game, crowd, commentary) and applies sidechain and ducking to guarantee a clarity target; tests report metrics like clarity_db and latency.

## Key implementation notes (concrete)
- The dynamic mixing rules live in engine/dynamic_mixer.py. Examples of behaviors implemented there:
  - Crowd ingest & hysteresis (CrowdInput.ingest)
  - AdaptiveEQ presets per device (AdaptiveEQ.for_device)
  - Sidechain compressor model (SidechainCompressor)
  - Priority boosts, environment/music scaling, and stem mixing via mix_stems()
- FMOD mapping and required parameters/snapshots are defined in integration/fmod/fmod_events.json (parameters: intensity, crowd_volume, player_health, commentary_active; snapshots: normal, arena_hot, broadcast_focus, etc.).
- Unity EchoForge hook (src/audio_engine/Unity/EchoForgeAudioEngine.cs) computes crowd RMS, sets AudioApi RTPCs (SetRtpc("intensity", value)), gates the crowd mic, and adjusts local AudioSource volumes for ambience and priority cues. It mirrors Python behavior so runtime and tests align.
- Tests live in tests/ and are invoked as simple Python scripts (python3 tests/test_audio.py). The README documents the CI gate as running those tests.

## How to run it (from a fresh clone)
- Run the Python test gate (no FMOD required to run the reference tests):

```
python3 -m pip install -r requirements.txt   # if a requirements file exists; otherwise ensure Python 3 is available
python3 tests/test_audio.py
python3 tests/test_dynamic_mix.py
```

- Running in an engine (Unity / Godot / Unreal) requires:
  - FMOD Studio project & built banks referenced by integration/fmod/fmod_events.json (banks listed there: "Master", "Master.strings")
  - Placing the appropriate integration files (integration/fmod/unity or integration/fmod/godot) into the engine project
  - In Unity, add src/audio_engine/Unity/EchoForgeAudioEngine.cs to a persistent scene object and wire the AudioSource references

- Quick runtime example (Unity-style calls from the README):
```csharp
FmodAudioManager.Instance.InitializeFmod();
FmodAudioManager.Instance.SetIntensity(0.7f);
FmodAudioManager.Instance.Post("sfx.gunfire", muzzle);
```

- The broadcast mixer is a Python module (broadcast/broadcast_mixer.py). Running it requires the same stem inputs or simulated stems; tests report a clarity metric (clarity_db) the repo treats as a regression threshold.

