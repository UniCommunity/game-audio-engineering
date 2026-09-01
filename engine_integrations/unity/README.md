# Unity integration README (template)

This README is a per-engine template describing how generated code integrates into Unity projects.

Overview
- Location: engine_integrations/unity/
- Purpose: contains C# wrappers and runtime hooks generated from data/events.json and integration mapping files.

What the generated output looks like
- `Scripts/` — generated C# classes and AudioApi wrappers.
- `Scenes/AudioTestBox` — a simple Unity test scene you can open to validate event posting and RTPC writes.

How to import into your Unity project
1. Copy the contents of `engine_integrations/unity/Scripts/` into your Unity project's `Assets/Scripts/` (or add as a local package).
2. Import the FMOD banks listed in `integration/fmod/fmod_events.json` into `Assets/Plugins/FMOD/`.
3. Open `Scenes/AudioTestBox` and press Play to validate runtime behavior.

Notes for engine teams
- Ensure the project's scripting runtime version is compatible with the generated C# (target .NET 4.x equivalent / Unity 2020+ recommended).
- The generated code is small and intended as a thin wrapper: it maps event ids to friendly function names and provides typed setters for parameters.
- For production builds, verify bank versions and include them in your build pipeline.

Runbook (quick checks)
- Verify generated files compile: open Unity, check Console for compile errors.
- Confirm AudioApi calls are logged on startup; these logs help ensure the game posts the expected RTPCs and event ids.

Local validation
- You can run a syntax/lint check outside Unity using `dotnet format` or Roslyn analyzers if available.

See also: ../../docs/PRODUCTION_GUIDE.md and ../../docs/CONTRACT.schema.json
