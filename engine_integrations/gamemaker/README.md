# GameMaker integration README (template)

This README is a per-engine template describing how generated code integrates into GameMaker projects (GML).

Overview
- Location: engine_integrations/gamemaker/
- Purpose: contains generated GML wrapper scripts and a small test room.

What the generated output looks like
- `scripts/` — generated `.gml` scripts mapping event ids to global constants or wrapper functions.
- `AudioTestRoom.yy` — a GameMaker test room you can open to trigger events.

How to import into your GameMaker project
1. Copy the generated `.gml` files into your GameMaker project's Scripts folder (or include them using the resource tree).
2. Ensure the project has audio resources configured and that the naming matches the generated wrappers.
3. Open `AudioTestRoom.yy` in GameMaker Studio and run the test room.

Notes for engine teams
- GameMaker's GML is interpreted; generated wrappers are simple string constants and play functions to keep integration friction low.
- If you use extensions or native functions, the generator can emit extension-compatible calls (update the manifest accordingly).

Runbook (quick checks)
- Open the project and run the test room; look for console output or on-screen debug text indicating event posts.

See also: ../../docs/PRODUCTION_GUIDE.md and ../../docs/CONTRACT.schema.json
