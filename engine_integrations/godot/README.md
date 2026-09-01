# Godot integration README (template)

This README is a per-engine template describing how generated code integrates into Godot projects.

Overview
- Location: engine_integrations/godot/
- Purpose: contains GDScript managers and example scenes generated from data/events.json.

What the generated output looks like
- `scripts/` — generated GDScript files (FmodAudio wrapper, event shims).
- `main.tscn` — a test scene configured to exercise the generated managers.

How to import into your Godot project
1. Copy `engine_integrations/godot/scripts/` into your Godot project's `res://` folder (or add as a submodule/package).
2. Place the FMOD integration files under `res://addons/fmod/` if using the FMOD Godot plugin.
3. Open `main.tscn` and run the scene to validate event posting and parameter updates.

Notes for engine teams
- Godot versions differ: templates target Godot 3.x or 4.x depending on generation flags. Confirm compatibility in the generator manifest before generating.
- GDScript is dynamically typed; the generator adds docstrings and simple runtime checks where possible.

Runbook (quick checks)
- Run `godot --check` or open the project to ensure scripts load without parse errors.
- Verify FMOD initialization and that calls to `FmodAudio.post(event_id)` are observed in logs.

See also: ../../docs/PRODUCTION_GUIDE.md and ../../docs/CONTRACT.schema.json
