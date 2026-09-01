# Unreal integration README (template)

This README is a per-engine template describing how generated code integrates into Unreal Engine projects.

Overview
- Location: engine_integrations/unreal/
- Purpose: contains generated C++ headers and example Blueprints or native hooks to interface with FMOD.

What the generated output looks like
- `Source/` — generated C++ headers and thin wrappers for FMOD event posting.
- `Maps/` — a small test map with sample actors that trigger generated events.

How to import into your Unreal project
1. Add generated headers and source files into your Unreal project's `Source/<Module>/` directory.
2. Ensure your Unreal Build Tool (UBT) configuration includes FMOD plugin dependencies and link paths.
3. Open the test map in the Editor and run it to validate runtime behavior.

Notes for engine teams
- Unreal's build toolchain may require regenerating project files after adding headers; run `GenerateProjectFiles.bat` or the equivalent.
- For Blueprint exposure, the generator emits UFUNCTION wrappers if requested in the manifest.

Runbook (quick checks)
- Build the project or run a minimal compile to check for missing includes.
- Verify that generated identifiers do not conflict with existing project symbols.

See also: ../../docs/PRODUCTION_GUIDE.md and ../../docs/CONTRACT.schema.json
