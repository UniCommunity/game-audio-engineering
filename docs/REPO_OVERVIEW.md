# Repository overview

## What this is
A practical, production-oriented sound-engineering kit for games and esports that separates designer intent, deterministic mixing, and production routing. It combines:
- a canonical events catalogue (designer source-of-truth),
- a Python reference engine and test oracle used for deterministic validation, and
- per-engine integration layers (Unity, Unreal, Godot) and FMOD mappings for runtime delivery.

### Design goals (short)
- One canonical Events catalogue (data/events.json) mapped to FMOD/Wwise.
- Deterministic mixing behavior in a Python oracle for automated regression tests.
- Lightweight engine runtime hooks that post event IDs and parameters (no broadcast routing baked into game code).
- A separate broadcast/venue pipeline that consumes dedicated stems + telemetry to produce show mixes.

### Stack
- **Language(s):** Python (oracle & tests), C# (Unity), GDScript (Godot), C++ (Unreal / native DSP)
- **Runtime / middleware:** Python 3 (oracle), FMOD Studio (or Wwise) for runtime mixing and DSP
- **Notable systems:** FMOD Studio (events, parameters, snapshots), Unity Audio API, Godot FMOD plugin, Dante/AES67/NDI/SRT (broadcast transports)

## How it's organized
Top-level important entries (annotated):

```
README.md
docs/
  REPO_OVERVIEW.md        # this file
  PRODUCTION_GUIDE.md     # runbook for broadcast engineers (added)
  CONTRACT.schema.json    # canonical machine spec (recommended)
  SPEC.md                 # human-friendly spec derived from schema
data/
  events.json             # canonical event catalogue (source of truth)
fmod_project/
  EsportsAudioKit.fspro   # FMOD Studio project (buses, DSP, routing)
python_oracle/
  build_and_test_audio.py # CLI to generate stems & run headless tests
  code_generator.py       # generates engine wrappers from data/events.json
  example_synth.py        # synth stems for tests / local verification
  tests/                  # pytest suite for oracle-level validations
integration/ (or engine_integrations/)
  unity/                  # generated C# managers, EchoForge example, scenes
  godot/                  # generated GDScript managers and test scene
  unreal/                 # C++ hooks and test map
broadcast/
  broadcast_mixer.py      # broadcast stem mixer, clarity checks
examples/
  example_contract.json   # sample contract payloads for tests
  example_stems/          # small generated WAVs used by tests
tests/                    # repo-level tests (schema + oracle + integration smoke)
.github/
  workflows/ci.yml        # suggested CI: schema validation + python tests
.gitattributes            # git-lfs rules for large binary assets (.bank, .fspro)
CONTRIBUTING.md
```

**How it fits together**
- Designers author events in `data/events.json`.
- `python_oracle/` validates mixing logic (engine/dynamic_mixer.py), synthesizes stems (example_synth.py) and provides a deterministic oracle used by tests in `tests/`.
- `integration/*` contains engine-specific runtime glue that posts event IDs and parameters to middleware (FMOD/Wwise) and to an in-repo AudioApi (EchoForge example for Unity).
- Broadcast/Show tooling consumes dedicated stems and telemetry (stems + parameters + metadata) to assemble the final show mix with appropriate loudness and clarity constraints.

## How to run (quick)
- Validate and run oracle tests locally (no FMOD required):

```bash
python3 -m pip install -r requirements.txt  # if present
# validate examples and schema (ajv or python-jsonschema)
ajv validate -s docs/CONTRACT.schema.json -d examples/example_contract.json
# run python oracle tests
python3 python_oracle/build_and_test_audio.py
python3 -m pytest python_oracle/tests
```

- Engine integration (Unity/Godot/Unreal): import generated Scripts / Scenes, add FMOD banks to the engine project, and wire AudioApi/EchoForge hooks per engine README.

## Repo hygiene & operational notes
- Large binary assets (FMOD .bank, exported audio) should be stored carefully: prefer git-lfs or an external artifact store; use `.gitattributes` to avoid bloating Git history.
- Track versions: semantic version the contract (docs/CONTRACT.schema.json) and keep a CHANGELOG.md for bank/build releases.
- CI should validate the contract schema, run the python oracle tests, and validate example payloads (suggested workflow: schema validate → python_oracle tests → contract tests).

## Recommended next steps (what I can implement)
1. Add `docs/schemas/events.schema.json` (upgraded events schema) and `tests/test_events_schema_validation.py`.
2. Add `examples/example_contract.json` and `python_oracle/example_synth.py` to generate test stems.
3. Add `tools/validate_events.py` to run additional checks (unique IDs, reserved names, cross-references with FMOD mapping).
4. Add `.gitattributes` with git-lfs rules and a CI workflow (`.github/workflows/ci.yml`) that runs schema validation + tests.

If you want, I will implement step 1 next (create the upgraded events schema under docs/schemas/events.schema.json and a basic validation test).