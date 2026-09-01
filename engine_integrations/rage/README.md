# RAGE integration README (template)

This README is a per-engine template describing how generated code integrates into RAGE (Rockstar Advanced Game Engine) projects.

Overview
- Location: engine_integrations/rage/
- Purpose: contains generated C++ headers and build integration notes for RAGE-like engines.

What the generated output looks like
- `include/` — generated `.h` files exposing event ids and parameter setter prototypes for native code.
- `scripts/` — engine-specific implementation stubs where developers wire event posts to the engine's audio thread.

How to import into your RAGE project
1. Add generated headers to the engine's include path and include them where the audio subsystem posts events.
2. Implement the thin stubs in `scripts/` to call your engine's low-level FMOD/Core API bindings.
3. Build the engine module or plugin per RAGE's build system.

Notes for engine teams
- RAGE is a complex, proprietary codebase; the generator provides headers and minimal stubs but cannot perform private build integration steps.
- Expect manual work: hooking into the engine's audio thread and ensuring thread-safety is the responsibility of the integrator.

Runbook (quick checks)
- Compile the module and run a development map that exercises the generated event posts.
- Check logs for API errors and ensure FMOD initialization occurs on the correct thread.

See also: ../../docs/PRODUCTION_GUIDE.md and ../../docs/CONTRACT.schema.json
